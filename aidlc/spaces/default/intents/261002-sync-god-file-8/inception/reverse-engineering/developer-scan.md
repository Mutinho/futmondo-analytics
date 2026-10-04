# Reverse Engineering — Developer Code Scan (link 1)

> Intent `sync-god-file-8` (scope=refactor, depth=Minimal). Barrido FOCALIZADO
> y de SOLO LECTURA del área de sincronización. Repo único sin cualificador.
> Identificadores, rutas, código y encabezados preservados en inglés; prosa en
> castellano (regla de proyecto Code Style).

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply**:
  - `backend/app/services/data_sync_service.py`
  - `backend/app/services/sync/` (incluye `__init__.py`, pilotos `match_odds/` y `clauses/` completos: `orchestrator.py`, `domain/ports.py`, `infrastructure/<domain>_adapter.py`)
  - `backend/app/services/prizes/` (`__init__.py`, `calculator.py`, `team_prizes_writer.py`)
  - `backend/app/api/v1/endpoints/sync.py`
- **Skimmed only** (contratos adyacentes, NO cobertura profunda):
  - `backend/app/services/sync_step_status.py` — helper `record_degraded_step` + `StepStatus` (running/done/degraded); lo consume el worker del router, no los orquestadores.
  - `backend/app/services/data_manager_v2.py` — fachada de persistencia (god-file ~166 KB); NO se descompone en este intent (los adapters la envuelven verbatim).
  - `backend/app/services/futmondo_client.py` — cliente de ingesta inyectado (`FutmondoClient`); mantiene las credenciales fuera de sus propios errores.
  - `backend/app/services/integration_errors.py` — jerarquía de excepciones tipadas (`IntegrationBanError`, `IntegrationTimeoutError`, `IntegrationUnparseableError`, `IntegrationRequestError`).
  - `backend/tests/` — tests de caracterización del área sync (`test_sync_match_odds_characterization.py`, `test_sync_clauses_characterization.py`, `test_prizes_characterization.py`, `test_prizes_calculator.py`, `test_team_prizes_atomic_replacement.py`, `test_sync_degraded_steps.py`, `test_sync_step_status.py`, `test_sync_integration_failure_effect.py`).
  - `backend/pytest.ini` — configuración del runner y piso de cobertura.

### Packages Found

- `app.services.sync` — bounded-context root (Wave 3 de la descomposición del god-file) — Python 3.12 — hospeda un subpaquete por dominio sync extraído; `__init__.py` documenta el patrón DDD.
- `app.services.sync.match_odds` — dominio PILOTO (shape ligero) — Python — `sync_match_odds` ya extraído end-to-end.
- `app.services.sync.clauses` — dominio PILOTO (shape paginado) — Python — `sync_clauses` ya extraído.
- `app.services.prizes` — cálculo puro + escritor atómico — Python — lógica de premios YA extraída (`calculator.py` + `team_prizes_writer.py`), pero `sync_prizes` sigue INLINE en el god-file (fachada no uniformizada).
- `app.services.data_sync_service` — fachada god-file (`DataSyncService`) — Python — superficie pública a preservar; aún hospeda 8 dominios inline + `sync_prizes`.
- `app.api.v1.endpoints.sync` — router FastAPI — Python — punto de entrada (`/trigger`, `/task/{id}`, `/status`, `/last-sync`).

### Proven DDD shape (pilotos `match_odds` + `clauses`) — patrón a replicar

Estructura por dominio bajo `backend/app/services/sync/<domain>/`:

```
<domain>/
  __init__.py                       # re-exporta <Domain>SyncOrchestrator; docstring del contrato
  orchestrator.py                   # <Domain>SyncOrchestrator: ingesta (client inyectado) + throttling + manejo de errores + delegación
  domain/
    __init__.py
    ports.py                        # <Domain>SyncDataPort: typing.Protocol consumer-owned; SOLO ops que consume; sin SQL, sin framework
  infrastructure/
    __init__.py
    <domain>_adapter.py             # DataManager<Domain>Adapter: ÚNICO punto que toca DataManagerV2; delega verbatim
```

Invariantes del patrón (observadas, no aspiracionales):

1. **Thin facade delegation** — el método `DataSyncService.sync_<domain>` queda como delegación delgada: import perezoso del orquestador + del adapter, instancia con `client=self.client`, `championship_id=self.championship_id`, `data=DataManager<Domain>Adapter(dm=self.dm)`, y `return orchestrator.sync()`. Misma firma, mismo return. El import perezoso mantiene el grafo de imports de la fachada sin cambios.
2. **Orchestrator** — `__init__(self, client, championship_id, data=None)`; `data` por defecto construye el adapter de producción (`DataManager<Domain>Adapter()` → `DataManagerV2(skip_init=True)`), permitiendo inyectar un stub en tests. El método `sync()` reproduce byte-a-byte el `SyncResult` del método inline previo (status, keys, campos).
3. **Port consumer-owned** — `typing.Protocol` estructural en `domain/ports.py`; refleja la superficie de `DataManagerV2` verbatim (mismos nombres, misma firma por keyword); no importa `infrastructure/` ni framework; no contiene SQL (dependency inversion).
4. **Adapter** — implementa el Protocol; `__init__(self, dm=None)` con default `DataManagerV2(skip_init=True)`; delega cada llamada verbatim; para `update_sync_metadata` reenvía SOLO los kwargs que la llamada inline original suministraba (preserva los defaults de `DataManagerV2`, fila persistida idéntica). NO se añade ningún método a `data_manager_v2.py`.
5. **No credenciales en errores/logs** — la ruta de fallo loguea `str(e)` y lo guarda como `error_message`; el `FutmondoClient` ya mantiene credenciales fuera de sus errores.
6. **Set-replacement atómico (patrón `team_prizes_writer`)** — para dominios con reemplazo-de-conjunto, el patrón de referencia es `prizes/team_prizes_writer.py::replace_team_prizes`: upsert del conjunto completo + DELETE de filas stale en UNA sola transacción (`with db.get_connection()`), all-or-nothing, el fallo PROPAGA (no se traga). Reemplaza el antiguo `DELETE ... NOT IN` con `try/except → logger.warning` que dejaba estado mixto.

### Domains STILL inline en `data_sync_service.py` (a extraer)

Orden y clave literal según `sync_all()` (debe preservarse exacto). SyncResult = payload observable que el router propaga a `progress[step]`.

1. **`sync_transactions`** → clave `transactions`.
   - Ingesta paginada `client.get_pressroom_news` (filtro `_player`/`_buyer`/`_seller`, de-dup `seen_ids`, parada en `previous_last_id`, `time.sleep(0.3)`, límite 50 páginas).
   - Helpers: `_store_bids(transaction_items)` (UPDATE `transactions.bids_json` por `api_transaction_id`), `_enrich_market_values()` (SELECT txns con `market_value_at_purchase IS NULL`; llama `client.get_player_fullprofile`; batches de 20 con pausa 5s; UPDATE por `transaction_id`), `_find_price_at_date(prices, txn_date, prefer_previous_day)` (puro, sin I/O).
   - DataManagerV2/SQL: `get_last_sync_metadata`, `save_pressroom_transactions`, `update_sync_metadata`; **SQL directo sobre `self.dm.db`** — `ALTER TABLE transactions ADD COLUMN IF NOT EXISTS …` (migración oportunista en caliente), UPDATE `bids_json`, SELECT/UPDATE de enriquecimiento. Acoplamiento alto: toca el `db` crudo, no solo métodos de `DataManagerV2`.
   - SyncResult: `{status(success|no_new_data|error), records_synced, last_sync_id, duration_seconds}` (+ `error` en fallo).
   - Coupling signals: el ramo-`try/except: pass` del ALTER TABLE; el enriquecimiento con `except … logger.warning` no-crítico; `_find_price_at_date` es candidato a `domain/` puro.

2. **`sync_punishments_bonuses`** → clave `punishments_bonuses`.
   - Ingesta `client.get_locker_news` (filtro `styp in ["punish","bonus"]`, de-dup, `time.sleep(0.3)`, límite 1000 páginas).
   - DataManagerV2: `get_last_sync_metadata`, `save_punishments_bonuses`, `update_sync_metadata`.
   - SyncResult: `{status, records_synced, last_sync_id, duration_seconds}`.
   - Nota: `status = "success" if total_synced > 0 or from_id else "no_new_data"` — preservar esta condición exacta.

3. **`sync_dream_teams_mvps`** → clave `dream_teams`.
   - Usa `_find_championship()` (helper privado compartido) para resolver rounds; mapea round_id→number vía `get_matchday_standings` + `get_userteam_rounds`; filtra `closed_statuses`; `client.get_dream_team` por round; `time.sleep(0.1)`.
   - DataManagerV2: `get_last_sync_metadata`, `save_dream_team_mvp(…, player_details=…)`, `update_sync_metadata`.
   - SyncResult: `{status, records_synced, last_sync_matchday, duration_seconds}`.
   - Coupling: depende de `_find_championship()` (comparte lógica con `sync_rosters`).

4. **`sync_player_performance`** → clave `player_performance`.
   - `get_matchday_standings` → `team_map`; `get_userteam_rounds` → `round_id_map`; itera matchdays; `client.get_user_roundlineup` por team/round; extracción tolerante de `points`/`value`/`was_best_player`; `time.sleep(0.05)`; batch por matchday.
   - DataManagerV2: `get_last_sync_metadata`, `save_player_performance_batch`, `update_sync_metadata`.
   - SyncResult: `{status, records_synced, last_sync_matchday, duration_seconds}`.
   - Coupling: dos retornos tempranos `no_new_data` (sin teams / sin round map) que también escriben metadata — preservar ambos.

5. **`sync_rosters`** → clave `rosters`.
   - Comparte el patrón de `_find_championship()` + `round_numbers` + `closed_rounds` con `sync_dream_teams_mvps`; `client.get_user_roundlineup`; solo `players` (NO `bench`); `time.sleep(0.1)`.
   - DataManagerV2: `get_last_sync_metadata`, `save_team_roster(…, matchday=…)`, `update_sync_metadata`.
   - SyncResult: `{status, records_synced, last_sync_matchday, duration_seconds}`.

6. **`sync_round_rankings`** → clave `team_standings` (clave literal DISTINTA del nombre del método — crítico).
   - Siempre re-sincroniza desde matchday 1; `get_userteam_rounds` → `round_id_map`; `client.get_round_ranking` por matchday; parada tras 2 misses consecutivos; `max_rounds=38`; `time.sleep(0.2)`.
   - Helper `_save_favorites(player_ids)` está físicamente ENTRE `sync_round_rankings` y `sync_players_full`, pero lo consume `sync_players_full` (ver nota de coupling), NO `sync_round_rankings`. Hace `CREATE TABLE IF NOT EXISTS player_favorites` + DELETE/INSERT sobre `self.dm.db` crudo (incluye rama `psycopg2.extras.execute_values` para Postgres).
   - DataManagerV2: `save_round_ranking`, `get_latest_matchday`, `update_sync_metadata`.
   - SyncResult: `{status, rounds_synced, records_synced, last_matchday, duration_seconds}` — forma DISTINTA (incluye `rounds_synced` y `last_matchday`, no `last_sync_matchday`).

7. **`sync_players_full`** → clave `players` (en `sync_all`; también `players` en el payload).
   - `client.get_championship_players`; construye `player_records` + `stats_payload`; batch insert; `delete_orphan_players(live_ids)`; `save_player_championship_stats`; invoca `self._save_favorites(favorites)`.
   - DataManagerV2: `save_players_batch`, `delete_orphan_players`, `save_player_championship_stats`, `update_sync_metadata`.
   - SyncResult: `{status, records_synced, duration_seconds}` (sin `last_sync_*`).
   - Coupling: `_save_favorites` toca `self.dm.db` crudo y `self.client.user_id`; es el único consumidor de ese helper.

8. **`sync_prizes`** → clave `prizes` (uniformizar a fachada; lógica YA extraída a `prizes/`).
   - Orquestación inline: lee config de `user_championships` vía SQL directo sobre `get_db()`; `get_matchday_standings`; `get_userteam_rounds`; lógica de pseudo-rounds avanzados (número float → matchday sintético negativo); `round_fully_played` (todos los matches status `F`); `get_dream_team` + `get_round_lineup` para MVP/dream-team counts; materializa `RoundTeamEntry`; llama al calculador puro `calculate_round_prizes` (de `prizes/calculator.py`); acumula filas; persiste UNA vez vía `replace_team_prizes` (de `prizes/team_prizes_writer.py`).
   - Manejo de errores TIPADO: `IntegrationBanError` → ERROR + `raise` (fatal); `IntegrationTimeoutError`/`IntegrationUnparseableError`/`IntegrationRequestError` → WARNING + `raise` (escalado-en-punto-de-escritura BR2.3); `Exception` → red de seguridad final retorna `{status:"error", …}`. Usa `_log_integration_failure` (helper módulo-nivel).
   - SyncResult: `{status(success|no_new_data|no_config|no_prizes_configured|no_standings|no_teams|no_rounds|error), rounds_processed, records_synced, stale_prizes_removed, duration_seconds}` — el conjunto de status es el más rico; preservar TODOS los early-returns.
   - Estado actual: lógica pura y escritor atómico YA viven en `prizes/`; falta mover la ORQUESTACIÓN a `sync/prizes_sync/` (o equivalente) dejando `sync_prizes` como delegación delgada, igual que `match_odds`/`clauses`.

### Public surface que DEBE preservarse (equivalencia observable, FR5)

- `DataSyncService(futmondo_client=None)` — `__init__` crea `DataManagerV2(skip_init=True)`, `ensure_championship_exists`, auth del cliente si no se inyecta. Atributos públicos: `self.dm`, `self.client`, `self.championship_id`, `self.league_id`, `self.user_id`.
- Los **10 métodos** `sync_*` (firma `() -> Dict`): `sync_transactions`, `sync_clauses`, `sync_punishments_bonuses`, `sync_dream_teams_mvps`, `sync_player_performance`, `sync_rosters`, `sync_round_rankings`, `sync_players_full`, `sync_match_odds`, `sync_prizes`.
- `sync_all()` — orden FIJO y 10 claves LITERALES: `players`, `transactions`, `clauses`, `punishments_bonuses`, `dream_teams`, `player_performance`, `rosters`, `team_standings`, `match_odds`, `prizes`. (Nota: `players` va PRIMERO por FKs; la clave `dream_teams` ≠ método `sync_dream_teams_mvps`; la clave `team_standings` ≠ método `sync_round_rankings`.)
- Helpers privados consumidos por los dominios: `_find_championship()` (dream_teams + rosters), `_store_bids`/`_enrich_market_values`/`_find_price_at_date` (transactions), `_save_favorites` (players), `_log_integration_failure` (prizes).

### APIs Discovered

- REST (FastAPI) — `backend/app/api/v1/endpoints/sync.py` — 4 endpoints:
  - `GET /status` — estado de sync por data_type (lee `get_last_sync_metadata`).
  - `GET /last-sync` — `MAX(last_sync_date)` por championship (SQL directo).
  - `POST /trigger` — lanza sync async en thread daemon; `valid_types=("all","transactions","clauses","dream_teams","rosters","players")`; 409 si hay sync en curso; 202 con `task_id`.
  - `GET /task/{task_id}` — polling de progreso (pending|running|completed|failed).
- Entry point del fan-out: `_run_sync_in_background(task_id, sync_type, …)` — para `sync_type=="all"` llama los 10 `sync_*` en orden con `tm.update_progress` por paso usando las claves literales (incl. `team_standings`→`sync_round_rankings`, `dream_teams`→`sync_dream_teams_mvps`), + `phantoms` extra (`_check_phantoms`, local al router). El manejo DEGRADED de `prizes`/`phantoms` vive en el router vía `record_degraded_step`.

### Build System

- **Type**: pip (requirements.txt) + pytest; runner ejecutado DESDE `backend/`.
- **Config Files**: `backend/pytest.ini`, `backend/requirements.txt`, `backend/ruff.toml` (no leído en profundidad), `backend/conftest.py` (fakes in-memory; skimmed via tests).
- **Build Dependencies**: `app.services.sync.*` → `app.services.data_manager_v2` (vía adapters), `app.services.futmondo_client`; `data_sync_service` → `app.services.prizes` (calculator + team_prizes_writer), `app.services.integration_errors`, `app.core.config`.

### Frameworks & Libraries

- FastAPI — router de sync (`APIRouter`, `JSONResponse`).
- Python stdlib — `typing.Protocol` (ports), `dataclasses` (PrizeConfig/RoundTeamEntry/TeamRoundPrize), `threading` (sync en background), `logging`, `time`.
- psycopg2 — `psycopg2.extras.execute_values` (rama Postgres de `_save_favorites`).
- pytest + pytest-cov — framework de test/cobertura (versiones no fijadas aquí; ver pytest.ini).

### Test Coverage

- **Test Directories**: `backend/tests/`.
- **Test Frameworks**: pytest (pytest 9.1.1 por los `.pyc`), con dobles in-memory (`_RecordingDM`, `_FakeFutmondoClient`, `_FakeInMemoryDB` de `conftest.py`); `time.sleep` monkeypatched a no-op; sin red, sin DB real, sin credenciales.
- **Coverage Config**: PRESENTE — `pytest.ini` fija `--cov-fail-under=27` (line-only, requiere `--cov=app`); piso bloqueante, ratchet solo-sube.
- **Área sync — tests de caracterización ya existentes**: `test_sync_match_odds_characterization.py` y `test_sync_clauses_characterization.py` congelan el SyncResult observable de los pilotos y verifican que `sync_all` mantiene la clave literal en su posición histórica (los MISMOS tests corren verde contra el código extraído → equivalencia). También: `test_prizes_characterization.py`, `test_prizes_calculator.py`, `test_team_prizes_atomic_replacement.py`, `test_sync_degraded_steps.py`, `test_sync_step_status.py`, `test_sync_integration_failure_effect.py`.
- **Gap de cobertura directa**: los 8 dominios inline (transactions, punishments_bonuses, dream_teams_mvps, player_performance, rosters, round_rankings, players_full) NO tienen test de caracterización dedicado todavía — characterization-first aplica antes de extraerlos (mandato de equipo).

### Code Quality Indicators

- **Linting**: `ruff` backend (`backend/ruff.toml`, `select=["E","F","I"]`); hoy advisory, en vías de bloqueante en otro intent. NO reformatear brownfield en masa (regla afirmada).
- **CI/CD**: `.github/workflows/ci.yml` (PR-gate) y `fly-deploy.yml` job `verify` (push-gate) — gitleaks + pytest + ng test (no leídos en profundidad; fuera del área focalizada).
- **Documentation**: docstrings de módulo/clase ricos en los pilotos y en `prizes/` (citan BR/FR/NFR); el god-file tiene docstrings por método pero mezcla orquestación + SQL + manejo de errores.

### Technical Debt Signals

- **God-file**: `data_sync_service.py` ~77 KB / ~1806 líneas, 8 dominios inline + `sync_prizes` sin uniformizar + 5 helpers privados mezclando ingesta, SQL crudo y persistencia.
- **SQL en caliente / crudo sobre `self.dm.db`**: `sync_transactions` (`ALTER TABLE … IF NOT EXISTS` oportunista, UPDATE bids), `_enrich_market_values` (SELECT/UPDATE), `_save_favorites` (`CREATE TABLE IF NOT EXISTS` + DELETE/INSERT, rama Postgres). Estos puntos NO pasan por métodos de `DataManagerV2` y requerirán un port/adapter cuidadoso (envolver verbatim, sin reescribir SQL).
- **`try/except: pass` / `except … logger.warning`**: el ALTER TABLE de transactions traga toda excepción (`except Exception: pass`); el enriquecimiento de market value y la limpieza de huérfanos degradan con warning. Son deuda registrada de intents previos (god-file) — NO entran al alcance de este refactor salvo que el patrón atómico los sustituya.
- **Dependencia de clave literal divergente**: `team_standings`≠`sync_round_rankings` y `dream_teams`≠`sync_dream_teams_mvps`; alto riesgo de regresión si la extracción toca `sync_all()` o el fan-out del router.
- **`_find_championship()` compartido** por dos dominios (dream_teams + rosters): decidir si queda en la fachada o se promueve a un módulo compartido en `sync/`.
- **Rutas de rate-limiting** (`time.sleep` con valores distintos por dominio: 0.3/0.1/0.05/0.2) y límites de paginación distintos (50/1000) son comportamiento observable a preservar en cada orquestador.

## Handoff Summary

- **Intent-relevant finding**: El patrón DDD destino está PROBADO y es replicable mecánicamente. Los pilotos `match_odds` (`backend/app/services/sync/match_odds/`) y `clauses` (`backend/app/services/sync/clauses/`) demuestran la forma completa: fachada delgada (`DataSyncService.sync_match_odds`/`sync_clauses` = import perezoso + instancia del orquestador con `data=DataManager<Domain>Adapter(dm=self.dm)` + `return orchestrator.sync()`), orquestador con `data` inyectable, port `typing.Protocol` consumer-owned sin SQL, y adapter como único punto que toca `DataManagerV2` delegando verbatim. `prizes/` ya tiene la lógica pura (`calculator.py`) y el escritor atómico (`team_prizes_writer.py::replace_team_prizes`) extraídos, pero `sync_prizes` sigue inline: solo falta mover su ORQUESTACIÓN a un dominio `sync/<prizes>/` y dejar la delegación delgada. Quedan 8 dominios inline (transactions, punishments_bonuses, dream_teams_mvps, rosters, round_rankings, player_performance, players_full) + la uniformización de prizes = 10 dominios finales bajo `sync/`.
- **Risks / follow-up** (el arquitecto/siguiente etapa DEBE preservar):
  1. **Superficie pública congelada**: 10 métodos `sync_*`, `sync_all()` con orden fijo (`players` primero por FKs) y 10 claves LITERALES. Dos claves divergen del nombre del método: `team_standings`→`sync_round_rankings` y `dream_teams`→`sync_dream_teams_mvps`. El router (`sync.py` `_run_sync_in_background`) depende de esas claves literales.
  2. **Formas de SyncResult NO uniformes**: `sync_round_rankings` devuelve `rounds_synced`/`last_matchday`; `sync_players_full` no devuelve `last_sync_*`; `sync_prizes` tiene el set de status más rico (`no_config`/`no_prizes_configured`/`no_standings`/`no_teams`/`no_rounds` + early-returns). Cada orquestador debe reproducir su payload byte-a-byte.
  3. **SQL crudo sobre `self.dm.db`** en transactions (ALTER/UPDATE), `_enrich_market_values` (SELECT/UPDATE), `_save_favorites` (CREATE/DELETE/INSERT, rama Postgres `execute_values`), y `sync_prizes` (SELECT config vía `get_db()`): hay que envolverlo verbatim tras port+adapter, SIN reescribir SQL y SIN ampliar `data_manager_v2.py` (regla NEVER afirmada sobre god-files).
  4. **Characterization-first es mandato de equipo**: antes de extraer cada uno de los 8 dominios inline debe existir un test de caracterización que congele su SyncResult observable y su modo de fallo (recuperable vs fatal), como ya se hizo para `match_odds`/`clauses`. Hoy esos 8 dominios NO tienen cobertura directa dedicada.
  5. **Reemplazo de conjunto atómico** (patrón `team_prizes_writer`) es el patrón de referencia para cualquier dominio que haga full-refresh (`_save_favorites` ya hace DELETE+INSERT; evaluar si se eleva al patrón atómico o se deja como deuda registrada, respetando el alcance refactor/Minimal).
  6. **Comportamiento de ingesta a preservar por dominio**: valores distintos de `time.sleep` (0.3/0.2/0.1/0.05), límites de paginación (50 vs 1000), condiciones de parada (misses consecutivos, `previous_last_id`), y la lógica de pseudo-rounds avanzados de prizes (número float → matchday sintético negativo). `_find_championship()` lo comparten dream_teams y rosters.
  7. **Alcance read-only respetado**: no se modificó ningún archivo fuente; el único artefacto escrito es este scan.
