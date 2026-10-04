# Code Structure

## Organización de paquetes/módulos

Mono-repo con dos apps desplegables más soporte de infra:

- `backend/app/` — servicio web FastAPI (Python 3.12). Capas:
  - `api/v1/endpoints/` — 21 routers REST (ver `api-documentation.md`), entre
    ellos `sync.py` (sync router + worker en background).
  - `services/` — lógica de negocio + integraciones (núcleo del intent).
  - `auth/` — JWT + session/token stores.
  - `stores/` — repositorios de durabilidad.
  - `core/` — config/constants.
  - `models/`, `security/`.
  - `main.py` — arranque FastAPI.
- `angular-app/` — frontend Angular 22 (PWA, standalone components, signals,
  Material 22): `src/app/{core,features,shared}`.
- `proxy/` — nginx reverse proxy local.
- `cron/` — máquinas Fly one-shot para sincronizaciones programadas.
- `docs/`, `scripts/`, `docker-compose.yml`, `.github/workflows/`.

## Clasificación de ficheros (backend `services/`, foco del scan)

### Dominio sync en extracción DDD — `services/sync/` (patrón objetivo probado)

Árbol con DOS pilotos completos (`match_odds` + `clauses`). Estructura por dominio
bajo `backend/app/services/sync/<domain>/`:

```
<domain>/
  __init__.py                       # re-exporta <Domain>SyncOrchestrator; docstring del contrato
  orchestrator.py                   # <Domain>SyncOrchestrator (application): ingesta (client inyectado) + throttling + manejo de errores + delegacion al port
  domain/
    __init__.py
    ports.py                        # <Domain>SyncDataPort: typing.Protocol consumer-owned; SOLO ops consumidas; sin SQL, sin framework
  infrastructure/
    __init__.py
    <domain>_adapter.py             # DataManager<Domain>Adapter: UNICO punto que toca DataManagerV2; delega verbatim
```

- `sync/__init__.py` — raíz del paquete de contextos sync; documenta el patrón DDD.
- `sync/match_odds/` — contexto PILOTO (shape ligero): `sync_match_odds` ya
  extraído end-to-end.
- `sync/clauses/` — contexto PILOTO (shape paginado): `sync_clauses` ya extraído.

**Invariantes del patrón (observadas en los pilotos, no aspiracionales):**

1. **Thin facade delegation** — el método `DataSyncService.sync_<domain>` queda
   como delegación delgada: import perezoso del orquestador + del adapter,
   instancia con `client=self.client`, `championship_id=self.championship_id`,
   `data=DataManager<Domain>Adapter(dm=self.dm)`, y `return orchestrator.sync()`.
   El import perezoso mantiene el grafo de imports de la fachada sin cambios.
2. **Orchestrator** — `__init__(self, client, championship_id, data=None)`; `data`
   por defecto construye el adapter de producción
   (`DataManager<Domain>Adapter()` → `DataManagerV2(skip_init=True)`), permitiendo
   inyectar un stub en tests. `sync()` reproduce byte-a-byte el `SyncResult` del
   método inline previo.
3. **Port consumer-owned** — `typing.Protocol` estructural en `domain/ports.py`;
   refleja la superficie de `DataManagerV2` verbatim (mismos nombres, misma firma
   por keyword); no importa `infrastructure/` ni framework; sin SQL.
4. **Adapter** — implementa el Protocol; `__init__(self, dm=None)` con default
   `DataManagerV2(skip_init=True)`; delega cada llamada verbatim; para
   `update_sync_metadata` reenvía SOLO los kwargs que la llamada inline original
   suministraba (preserva los defaults de `DataManagerV2`). NO se añade ningún
   método a `data_manager_v2.py`.
5. **No credenciales en errores/logs** — la ruta de fallo loguea `str(e)` y lo
   guarda como `error_message`; el `FutmondoClient` ya mantiene credenciales fuera
   de sus errores.
6. **Set-replacement atómico** (patrón `team_prizes_writer`) para dominios con
   reemplazo-de-conjunto.

> Los 8 dominios pendientes (`transactions`, `punishments_bonuses`,
> `dream_teams`, `player_performance`, `rosters`,
> `round_rankings`→`team_standings`, `players_full`, y la uniformización de
> `prizes`) deben replicar este molde orchestrator + domain port + infrastructure
> adapter.

### Contexto `prizes/` — parcial (a uniformar al patrón)

- `prizes/__init__.py`
- `prizes/calculator.py` — cálculo puro de premios (sin I/O ni SQL); DTOs
  `dataclasses` (`PrizeConfig`/`RoundTeamEntry`/`TeamRoundPrize`).
- `prizes/team_prizes_writer.py` — `replace_team_prizes`: escritura transaccional
  atómica set-replacement sobre un `_DbLike` Protocol (DB inyectada).

Falta mover la ORQUESTACIÓN de `sync_prizes` a un dominio `sync/<prizes>/`,
dejando la delegación delgada igual que `match_odds`/`clauses` (comparar también
con `analytics/__init__.py` / `assistant/__init__.py`, que re-exportan desde
`facade.py`).

### God-files (deuda; ver `code-quality-assessment.md`)

- `data_sync_service.py` (~1806 líneas, ~77 KB) — **objetivo del intent**. Define
  `DataSyncService` con 10 `sync_*` + `sync_all()` (coordinador fino).
  `sync_match_odds` y `sync_clauses` ya son delegación fina; `sync_prizes` delega
  cálculo/escritura a `prizes/`. Aloja aún 8 dominios inline + 5 helpers privados.
- `data_manager_v2.py` (~3692 líneas, ~166 KB) — SQL/acceso a datos monolítico
  (`DataManagerV2`), dependencia de datos común de casi todos los `sync_*`.
- `photo_service.py` (~492 líneas) — deuda `E722` registrada.

### Otros módulos de servicios (skimmed)

`futmondo_client.py`, `sofascore_client.py`, `data_initializer*.py`,
`task_*`, `session_*`, `db_connection.py`, `integration_errors.py`
(`IntegrationBanError`/`IntegrationTimeoutError`/`IntegrationUnparseableError`/
`IntegrationRequestError`), `sync_step_status.py` (`record_degraded_step` +
`StepStatus` running/done/degraded), `analytics/`, `assistant/` (contextos
completos de oleadas 1-2, patrón de facade uniforme).

## Patrones de código

- **Patrón objetivo DDD (probado y a replicar)**: delegación fina en el método
  público → `orchestrator.py` (application, ingesta + throttling + errores) →
  domain port (`Protocol` consumer-owned, sin SQL) → `infrastructure/*_adapter.py`
  (único SQL, envuelve `DataManagerV2` verbatim). Demostrado end-to-end en
  `sync/match_odds/` y `sync/clauses/`.
- **Helpers privados compartidos del god-file (a decidir ubicación)**:
  `_find_championship()` (compartido por `dream_teams` + `rosters`),
  `_store_bids`/`_enrich_market_values`/`_find_price_at_date` (transactions),
  `_save_favorites` (players), `_log_integration_failure` (prizes).
  `_find_price_at_date` es puro (sin I/O) → candidato a `domain/`.
- **Set-replacement + escritura atómica**: upsert de todo el conjunto y
  `DELETE ... NOT IN (...)` de filas stale en una sola transacción
  (`team_prizes_writer.replace_team_prizes`), all-or-nothing.
- **Anti-patrones heredados (NO ampliar, regla afirmada)**:
  - **SQL-en-router**: el propio `sync.py` ejecuta SQL crudo inline
    (`_check_phantoms`, `get_last_sync_date`).
  - **Métodos mixtos**: 8 de 10 `sync_*` mezclan ingesta + SQL/persistencia +
    cálculo; sólo `sync_match_odds` y `sync_clauses` delegan del todo y
    `sync_prizes` parcialmente.
  - **SQL crudo sobre `self.dm.db`** (no sólo métodos de `DataManagerV2`):
    `sync_transactions` (`ALTER TABLE ... IF NOT EXISTS` oportunista + UPDATE
    `bids_json`), `_enrich_market_values` (`SELECT`/`UPDATE`), `_save_favorites`
    (`CREATE TABLE IF NOT EXISTS` + `DELETE`/`INSERT`, rama Postgres
    `psycopg2.extras.execute_values`), `sync_prizes` (`SELECT user_championships`
    vía `get_db()`). Debe migrar a un adapter de infraestructura por dominio,
    NUNCA al DataManager.
  - **`except Exception → return {"status":"error"}`** como red final por método;
    1 `except: pass` silencioso (`ALTER TABLE` idempotente en `sync_transactions`);
    `time.sleep()` de throttling incrustado (0.3/0.2/0.1/0.05 según dominio) y
    límites de paginación distintos (50 vs 1000) — comportamiento observable a
    preservar por orquestador.
- **Convenciones**: identificadores/docstrings/comentarios en inglés; texto de
  usuario y mensajes de commit en castellano; snake_case Python, camelCase TS.
  Docstrings ricos en el código nuevo (`match_odds/*`, `clauses/*`, `prizes/*`,
  citando BR*/FR*/NFR*), escasos en los god-files.
