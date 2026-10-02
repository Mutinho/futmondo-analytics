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

### Dominio sync en extracción DDD — `services/sync/` (patrón objetivo)

Árbol sembrado por el piloto `match_odds` (oleada previa). Estructura actual:

- `sync/__init__.py` — raíz del paquete de contextos sync.
- `sync/match_odds/` — contexto acotado piloto (patrón de referencia a replicar):
  - `match_odds/__init__.py`
  - `match_odds/orchestrator.py` — `MatchOddsSyncOrchestrator` (capa application):
    aloja la orquestación antes inline en `DataSyncService.sync_match_odds`
    (ingesta vía `FutmondoClient` inyectado, throttling, manejo de errores,
    delegación al port). Preserva el `SyncResult` observable byte-a-byte (FR5.3).
  - `match_odds/domain/ports.py` — `MatchOddsSyncDataPort`, `typing.Protocol`
    consumer-owned, SIN SQL ni framework; describe sólo las operaciones de
    persistencia que el orchestrator consume (`save_match_odds`,
    `update_sync_metadata`), reflejando la superficie de `DataManagerV2` verbatim.
  - `match_odds/infrastructure/match_odds_adapter.py` — `DataManagerMatchOddsAdapter`:
    único punto que toca `DataManagerV2`, al que delega verbatim (Wave 3 NO
    descompone `data_manager`).

> Los 8 dominios pendientes (`clauses`, `transactions`, `punishments_bonuses`,
> `dream_teams`, `rosters`, `round_rankings`→`team_standings`,
> `player_performance`, `players_full`) deben replicar este molde
> orchestrator + domain port + infrastructure adapter.

### Contexto `prizes/` — parcial (a uniformar al patrón)

- `prizes/__init__.py`
- `prizes/calculator.py` — cálculo puro de premios (sin I/O ni SQL); DTOs
  `dataclasses` `frozen=True`.
- `prizes/team_prizes_writer.py` — `replace_team_prizes`: escritura transaccional
  atómica set-replacement sobre un `_DbLike` Protocol (DB inyectada).

Falta el facade/orchestrator uniforme (comparar con `analytics/__init__.py` /
`assistant/__init__.py`, que re-exportan desde `facade.py`).

### God-files (deuda; ver `code-quality-assessment.md`)

- `data_sync_service.py` (1918 líneas, ~84 KB) — **objetivo del intent**. Define
  `DataSyncService` con 10 `sync_*` + `sync_all()` (L1888, coordinador fino).
  `sync_match_odds` (L1564) ya es delegación fina al orchestrator;
  `sync_prizes` (L1585) delega cálculo/escritura a `prizes/`.
- `data_manager_v2.py` (3692 líneas, ~166 KB) — SQL/acceso a datos monolítico
  (`DataManagerV2`), dependencia de datos común de casi todos los `sync_*`.
- `photo_service.py` (492 líneas) — deuda `E722` registrada.

### Otros módulos de servicios (skimmed)

`futmondo_client.py`, `sofascore_client.py`, `data_initializer*.py`,
`task_*`, `session_*`, `db_connection.py`, `integration_errors.py`,
`sync_step_status.py`, `analytics/`, `assistant/` (contextos completos de
oleadas 1-2, patrón de facade uniforme).

## Patrones de código

- **Patrón objetivo DDD (a replicar)**: delegación fina en el método público →
  `orchestrator.py` (application, ingesta + throttling + errores) → domain port
  (`Protocol` consumer-owned, sin SQL) → `infrastructure/*_adapter.py` (único SQL,
  envuelve `DataManagerV2` verbatim). Demostrado end-to-end en `sync/match_odds/`;
  `sync_prizes` es el ejemplo de delegación de cálculo/escritura dentro del propio
  god-file.
- **Set-replacement + escritura atómica**: upsert de todo el conjunto y
  `DELETE ... NOT IN (...)` de filas stale en una sola transacción
  (`team_prizes_writer.replace_team_prizes`), all-or-nothing.
- **Anti-patrones heredados (NO ampliar, regla afirmada)**:
  - **SQL-en-router**: el propio `sync.py` ejecuta SQL crudo inline
    (`_check_phantoms`, `get_last_sync_date`), igual que casi todos los routers.
  - **Métodos mixtos**: 8 de 10 `sync_*` mezclan ingesta + SQL/persistencia +
    cálculo en el mismo método; sólo `sync_match_odds` delega del todo y
    `sync_prizes` parcialmente.
  - **SQL dentro de métodos de servicio**: `sync_transactions` ejecuta
    `ALTER TABLE` y `UPDATE ... bids_json`; `_enrich_market_values` hace
    `SELECT`/`UPDATE`; `_save_favorites` hace `CREATE TABLE IF NOT EXISTS`/
    `DELETE`/`INSERT`; `sync_prizes` abre `get_db()` para un `SELECT user_championships`.
    Debe migrar a un adapter de infraestructura por dominio, NUNCA al DataManager.
  - **`except Exception → return {"status":"error"}`** como red final por método;
    1 `except: pass` silencioso (`ALTER TABLE` idempotente en `sync_transactions`);
    `time.sleep()` de throttling incrustado.
- **Convenciones**: identificadores/docstrings/comentarios en inglés; texto de
  usuario y mensajes de commit en castellano; snake_case Python, camelCase TS.
  Docstrings ricos en el código nuevo (`match_odds/*`, `prizes/*`, citando BR*/FR*/
  NFR*), escasos en los god-files.
