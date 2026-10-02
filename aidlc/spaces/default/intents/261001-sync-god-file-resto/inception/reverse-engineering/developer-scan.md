# Reverse Engineering — Developer Scan Handoff (link 1 de 2)

> Pipeline handoff del developer para la síntesis del architect. Scan FOCALIZADO
> (store STALE) sobre el área de trabajo del intent `261001-sync-god-file-resto`.
> Idioma de conversación: castellano. Identificadores, rutas y tokens en inglés
> literal.

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply**:
  - `backend/app/services/data_sync_service.py` (god-file, 1918 líneas / ~84 KB — sujeto principal)
  - `backend/app/services/sync/` (árbol DDD sembrado por el piloto `match_odds`)
  - `backend/app/services/sync/__init__.py`
  - `backend/app/services/sync/match_odds/__init__.py`
  - `backend/app/services/sync/match_odds/orchestrator.py`
  - `backend/app/services/sync/match_odds/domain/ports.py`
  - `backend/app/services/sync/match_odds/infrastructure/match_odds_adapter.py`
  - `backend/app/services/prizes/` (ya extraído; a uniformar al patrón facade)
  - `backend/app/services/prizes/__init__.py`
  - `backend/app/services/prizes/calculator.py`
  - `backend/app/services/prizes/team_prizes_writer.py`
  - `backend/app/api/v1/endpoints/sync.py` (sync router)
- **Skimmed only**:
  - `backend/app/services/` (resto: `data_manager_v2.py` ~166 KB / 3692 líneas, `futmondo_client.py`, `sofascore_client.py`, `photo_service.py`, `task_service.py`, `session_service.py`, `integration_errors.py`, `sync_step_status.py`, `assistant/`, `analytics/`)
  - `backend/app/api/` (resto de endpoints; sólo contexto)
  - `backend/` build/config: `pytest.ini`, `ruff.toml`, `requirements.txt`, `conftest.py`
  - `backend/tests/` (inventario de ficheros; no leídos en profundidad)
  - frontend (`angular-app/`) — sólo a nivel de contexto por el README

> El conjunto profundo se mantiene DENTRO de las rutas del snapshot:
> `backend/app/services/data_sync_service.py`, `backend/app/services/sync/`,
> `backend/app/services/prizes/`, `backend/app/api/v1/endpoints/sync.py`.

### Packages Found

- `app.services.data_sync_service` — service / god-file — Python — Facade público `DataSyncService`: ingestión desde la API Futmondo + persistencia vía `DataManagerV2`, un método `sync_*` por dominio. Objetivo de descomposición.
- `app.services.sync` — package (bounded contexts) — Python — Raíz del árbol DDD por dominio sync (Wave 3). Hoy contiene sólo el piloto `match_odds`.
- `app.services.sync.match_odds` — bounded context (piloto) — Python — Patrón de referencia a replicar: `orchestrator.py` + `domain/ports.py` (Protocol consumer-owned) + `infrastructure/match_odds_adapter.py` (único punto que toca `DataManagerV2`, verbatim).
- `app.services.prizes` — bounded context (parcial) — Python — Cálculo puro de premios (`calculator.py`, sin I/O ni SQL) + escritor transaccional atómico (`team_prizes_writer.replace_team_prizes`). Falta el facade/orchestrator para uniformarlo al patrón.
- `app.services.analytics` / `app.services.assistant` — bounded contexts (completos, Waves 1-2) — Python — Referencia del patrón facade uniforme (`__init__` re-exporta desde `facade.py`; shim de re-export en el módulo histórico).
- `app.services.data_manager_v2` — data access / god-file — Python — `DataManagerV2`, fachada de persistencia (SQL crudo). FUERA de alcance: NUNCA ampliar/reescribir; los adapters la envuelven verbatim.
- `app.api.v1.endpoints.sync` — router (FastAPI) — Python — Endpoints de sync y worker en background que invoca el surface público de `DataSyncService`.

### Build System

- **Type**: Python 3.12 (backend) con `pip` + `requirements.txt`; frontend Angular 22 (`npm`/Angular CLI) — fuera del foco.
- **Config Files**: `backend/pytest.ini`, `backend/ruff.toml`, `backend/requirements.txt`, `backend/conftest.py`.
- **Build Dependencies**:
  - `data_sync_service` → `data_manager_v2`, `futmondo_client`, `prizes` (calculator + team_prizes_writer), `integration_errors`, `core.config`, y (lazy) `sync.match_odds`.
  - `sync.match_odds.orchestrator` → `domain.ports` (abstracción) + `infrastructure.match_odds_adapter` (default); el adapter → `data_manager_v2`.
  - `prizes.calculator` → sin dependencias de I/O (puro); `prizes.team_prizes_writer` → sólo un `_DbLike` Protocol (DB inyectada).
  - `api.v1.endpoints.sync` → `data_sync_service` (surface público), `task_service`, `sync_step_status`, `data_manager_v2`, `db_connection`, `integration_errors`.

### APIs Discovered

- **Interna (surface público a PRESERVAR, FR5)** — `DataSyncService` — 10 métodos `sync_*` + `sync_all()`:
  - `sync_transactions` (L135), `sync_clauses` (L452), `sync_punishments_bonuses` (L589), `sync_dream_teams_mvps` (L681), `sync_player_performance` (L842), `sync_rosters` (L1065), `sync_round_rankings` (L1215), `sync_players_full` (L1429), `sync_match_odds` (L1564, ya delegado), `sync_prizes` (L1585).
  - `sync_all()` (L1888) — orquesta los 10 en **orden fijo** con 10 claves literales en el dict de retorno: `players`, `transactions`, `clauses`, `punishments_bonuses`, `dream_teams`, `player_performance`, `rosters`, `team_standings`, `match_odds`, `prizes`. (Nota de mapeo: la clave `players` ↔ `sync_players_full`, `dream_teams` ↔ `sync_dream_teams_mvps`, `team_standings` ↔ `sync_round_rankings`.)
  - Helpers privados (no públicos): `_find_championship`, `_store_bids`, `_enrich_market_values`, `_find_price_at_date`, `_save_favorites`.
- **HTTP (externa, sync router)** — `app/api/v1/endpoints/sync.py`:
  - `GET /status`, `GET /last-sync`, `POST /trigger` (202 + `task_id`, lanza thread), `GET /task/{task_id}`.
  - El worker `_run_sync_in_background` invoca el surface público (`sync_players_full`, `sync_transactions`, `sync_clauses`, `sync_punishments_bonuses`, `sync_dream_teams_mvps`, `sync_player_performance`, `sync_rosters`, `sync_round_rankings`, `sync_match_odds`, `sync_prizes`) con el mismo orden/claves que `sync_all`, más `phantoms` (helper del router `_check_phantoms`).
- **Externa consumida** — `FutmondoClient` (inyectado): `get_pressroom_news`, `get_locker_news`, `get_match_list`, `get_matchday_standings`, `get_userteam_rounds`, `get_user_roundlineup`, `get_round_ranking`, `get_round_matches`, `get_dream_team`, `get_round_lineup`, `get_championship_players`, `get_player_fullprofile`, `get_userteam_roster`.

### Frameworks & Libraries

- FastAPI == 0.141.1 — API HTTP (router de sync).
- pydantic == 2.13.5 — modelos (contexto).
- requests == 2.34.2 / curl_cffi == 0.16.3 — clientes de integración externa.
- psycopg2-binary == 2.9.13 — driver PostgreSQL (Neon); fakes SQLite en tests.
- PyJWT == 2.15.0 — auth (contexto, fuera del foco).
- pytest == 9.1.1, pytest-cov == 7.1.0, httpx == 0.28.1 — testing / cobertura.
- ruff (sin pin en instalación de CI; `backend/ruff.toml` fija `target-version = "py312"`, `line-length = 100`, `select = ["E","F","I"]`, `ignore = ["E501","E402"]`).
- `typing.Protocol` (stdlib) — base del patrón port consumer-owned.
- `dataclasses` (stdlib, `frozen=True`) — DTOs del calculator de premios.

### Test Coverage

- **Test Directories**: `backend/tests/` (39 ficheros `test_*.py`).
- **Test Frameworks**: pytest + pytest-cov; fakes in-memory en `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor` sobre SQLite `:memory:`, `clean_jwt_env`, `fake_db`). Sin red, sin BD real, sin credenciales reales.
- **Coverage Config**: presente. `pytest.ini` fija `addopts = -ra --cov-fail-under=27` (piso line-only, SIN `--cov-branch`; requiere `--cov=app` en la invocación — paridad `ci.yml` ↔ job `verify` de `fly-deploy.yml`). Cobertura real medida ~27.52 %; piso = 27, ratchet sólo sube.
- **Tests relevantes al intent ya presentes (characterization-first)**: `test_sync_match_odds_characterization.py` (piloto congelado), `test_prizes_calculator.py`, `test_prizes_characterization.py`, `test_team_prizes_atomic_replacement.py`, `test_sync_degraded_steps.py`, `test_sync_integration_failure_effect.py`, `test_sync_step_status.py`, `test_sofascore_sync_characterization.py`. NO existe aún cobertura de caracterización directa para los 8 dominios sync pendientes (clauses, transactions, punishments_bonuses, dream_teams, rosters, round_rankings/team_standings, player_performance, players_full).

### Code Quality Indicators

- **Linting**: ruff (`backend/ruff.toml`), modo advisory escalonado. `per-file-ignores` registra la deuda de los god-files en lugar de sanearla tocándolos: `data_manager_v2.py` → `["E722","F841","F401","I001"]`; `data_sync_service.py` → `["F401","I001"]`; `assistant_service.py` → `["I001"]`; `photo_service.py` → `["E722","F841"]`. `E722` (bare-except) re-habilitado como advisory por trinquete.
- **CI/CD**: gate bloqueante (`gitleaks` + `pytest` + `ng test`) en `ci.yml` y en el job `verify` de `fly-deploy.yml` (no leídos en profundidad en este scan; referidos por memory). Deploy Fly.io on-merge (región `cdg`).
- **Documentation**: docstrings extensas y en INGLÉS en los módulos nuevos (`match_odds/*`, `prizes/*`) citando reglas de negocio (BR*, FR*, NFR*) y preservación de surface. El god-file tiene docstrings por método pero mezcla orquestación, SQL inline (`ALTER TABLE`, `UPDATE`, `CREATE TABLE IF NOT EXISTS`) y throttling.

### Technical Debt Signals

- **God-file**: `data_sync_service.py` 1918 líneas / ~84 KB; `DataManagerV2` 3692 líneas / ~166 KB. Regla afirmada: NUNCA ampliarlos/reescribirlos.
- **Broad/bare excepts en el god-file**: 27 `except Exception`/`except:` detectados; 1 `except: pass` silencioso (en `sync_transactions`, el `ALTER TABLE ... ADD COLUMN` idempotente). Múltiples `except ...: logger.warning/debug ... continue` tragan fallos por página/ronda/equipo.
- **SQL dentro de métodos de servicio (no sólo en el DataManager)**: `sync_transactions` ejecuta `ALTER TABLE` y `UPDATE transactions SET bids_json`; `_enrich_market_values` hace `SELECT`/`UPDATE` directos; `_save_favorites` hace `CREATE TABLE IF NOT EXISTS`/`DELETE`/`INSERT`; `sync_prizes` abre `get_db()` y hace `SELECT ... FROM user_championships`. El router `sync.py` también tiene SQL inline (`_check_phantoms`, `get_last_sync_date`) — patrón SQL-en-router que NO debe ampliarse.
- **Acoplamiento ingestión+persistencia+throttling**: cada `sync_*` mezcla llamadas al `FutmondoClient`, `time.sleep` de rate-limiting, mapeo de rondas y escritura vía `self.dm`, todo inline — justo lo que el patrón piloto `match_odds` separa en orchestrator + port + adapter.
- **`sync_prizes` es el más complejo** (~300 líneas): lógica de pseudo-rondas adelantadas (matchday sintético negativo), gating `round_fully_played` (status "F"), detección de MVP/dream-team por lineup, y acumulación para reemplazo atómico vía `replace_team_prizes`. Ya delega el cálculo puro a `prizes.calculator` y la escritura atómica a `prizes.team_prizes_writer`, pero NO está envuelto en un facade/orchestrator de dominio como `match_odds`.
- **Manejo de errores tipado ya parcialmente introducido**: `_log_integration_failure` (log key=value sin credenciales, NFR1/BR4.2) y ramas `IntegrationBanError` (fatal, propaga) vs `IntegrationTimeout/Unparseable/Request` (recoverable) en `sync_prizes` y en el worker del router (`record_degraded_step`). Este patrón de clasificación recoverable/fatal debe preservarse al extraer cada dominio.

## Handoff Summary

- **Intent-relevant finding**: El surface público a preservar byte-a-byte (FR5) está acotado y verificado: `DataSyncService` + los 10 métodos `sync_*` (líneas 135–1585) + `sync_all()` (L1888–1917) con sus **10 claves literales y orden fijo** (`players`, `transactions`, `clauses`, `punishments_bonuses`, `dream_teams`, `player_performance`, `rosters`, `team_standings`, `match_odds`, `prizes`). El patrón DDD de destino ya existe y está probado end-to-end en `sync/match_odds/` (orchestrator + `domain/ports.py` Protocol consumer-owned + `infrastructure/match_odds_adapter.py` que envuelve `DataManagerV2` verbatim), y `sync_match_odds` (L1564) ya es una delegación fina a ese orchestrator — ésa es la plantilla literal a replicar para los 8 dominios restantes. `prizes/` tiene el cálculo puro (`calculator.py`) y la escritura atómica set-replacement (`team_prizes_writer.replace_team_prizes`, patrón de referencia para "atomic writes à la `team_prizes_writer`") pero le falta el facade/orchestrator uniforme (comparar con `analytics/__init__.py` y `assistant/__init__.py`, que re-exportan desde `facade.py`).
- **Risks / follow-up**:
  - Characterization-first STRICT por dominio ANTES de refactorizar: hoy sólo existen tests de caracterización para `match_odds` y `prizes`; los 8 dominios pendientes (clauses, transactions, punishments_bonuses, dream_teams, rosters, round_rankings/team_standings, player_performance, players_full) NO tienen cobertura directa — hay que congelar su `SyncResult` observable (claves `status`/`records_synced`/`last_sync_id`/`last_sync_matchday`/`rounds_synced`/`duration_seconds` según el dominio) antes de extraer.
  - Las formas de `SyncResult` NO son uniformes entre dominios: p.ej. `sync_round_rankings` devuelve `rounds_synced` + `last_matchday`; `sync_transactions`/`sync_clauses` devuelven `last_sync_id`; los basados en matchday devuelven `last_sync_matchday`; `sync_prizes` devuelve `rounds_processed` + `stale_prizes_removed`. Cada port/adapter debe preservar la forma exacta por dominio.
  - NUNCA ampliar/reescribir `data_sync_service.py` ni `data_manager_v2.py` ni el patrón SQL-en-router: los adapters envuelven `DataManagerV2` verbatim (como `match_odds_adapter`), y el SQL inline que hoy vive en los métodos de servicio (`ALTER TABLE`, `UPDATE bids_json`, `_enrich_market_values`, `_save_favorites`, el `SELECT user_championships` de `sync_prizes`) debe migrar a un adapter de infraestructura por dominio, NO al god-file del DataManager.
  - Preservar el manejo de errores tipado (fatal `IntegrationBanError` propaga; recoverable degrada vía `record_degraded_step`) y la garantía de que NINGUNA credencial/token llega a mensajes de excepción, `repr` ni logs (`_log_integration_failure`, NFR1/BR4.2).
  - No ejecutar `ruff format` masivo sobre el god-file ya modificado; formatear sólo los ficheros nuevos de cada dominio o de forma quirúrgica (regla afirmada; la reviewer sólo corre `ruff check`).
  - `_run_sync_in_background` (router) replica el orden/claves de `sync_all` y añade `phantoms` fuera del surface de `DataSyncService`; cualquier cambio de surface rompería el worker — mantener firma y retorno idénticos.
