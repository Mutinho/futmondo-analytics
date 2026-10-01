# Reverse Engineering — Escaneo de código del desarrollador (link 1)

Intent activo: `260929-sync-god-file` (Brownfield · scope `refactor` · depth Minimal).
Repo mono-repo: la raíz del workspace (`/home/javi/futmondo-analytics`) ES el
codebase. Escaneo: FULL RESCAN.

## Developer Code Scan Results

### Scan Coverage

#### Analyzed deeply
- `backend/app/services/data_sync_service.py` (1955 líneas, ~84 KB — god-file OBJETIVO del intent)
- `backend/app/services/prizes/__init__.py`
- `backend/app/services/prizes/calculator.py`
- `backend/app/services/prizes/team_prizes_writer.py`
- `backend/app/services/analytics/__init__.py`
- `backend/app/services/analytics/facade.py`
- `backend/app/services/analytics/domain/ports.py`
- `backend/app/services/analytics_service.py`
- `backend/app/services/assistant_service.py`
- `backend/app/api/v1/endpoints/sync.py`
- `backend/pytest.ini`
- `backend/ruff.toml`
- `backend/requirements.txt`
- `backend/conftest.py` (contrato de fakes, referenciado)
- `.github/workflows/ci.yml`
- `angular-app/package.json`
- `README.md`

#### Skimmed only
- `backend/app/` (resto: `main.py`, `core/`, `models/`, `auth/`, `stores/`, `security/`, `api/v1/endpoints/` — inventariados a granularidad de fichero/función)
- `backend/app/services/` (resto: `data_manager_v2.py` ~166 KB, `photo_service.py`, `futmondo_client.py`, `sofascore_client.py`, `data_initializer*.py`, `task_*`, `session_*`, `db_connection.py`, `integration_errors.py`, `sync_step_status.py`, subpaquetes `assistant/`, `analytics/application|infrastructure`)
- `backend/tests/` (44 ficheros; contadas suites de caracterización)
- `backend/scripts/`, `backend/Dockerfile`, `backend/fly.toml`
- `angular-app/src/app/` (`core/`, `features/`, `shared/`; 14 `*.spec.ts`)
- `angular-app/angular.json`, `eslint.config.js`, `nginx*.conf`, `fly.toml`, `Dockerfile`
- `.github/workflows/` (`fly-deploy.yml`, `daily-sync.yml`, `sofascore-sync.yml`)
- `proxy/`, `docs/`, `cron/`, `docker-compose.yml`, `scripts/`
- Excluidos: `angular-app/node_modules.old-*` (artefacto obsoleto), `.kiro/` (tooling AI-DLC, fuera del codebase de aplicación), cachés (`__pycache__`, `.ruff_cache`, `.pytest_cache`), `stitch_*` (mockups estáticos)

### Packages Found
- `backend/app` — servicio web FastAPI (Python 3.12). Capas: `api/v1/endpoints/` (routers), `services/` (lógica de negocio + integraciones), `auth/` (JWT + session/token stores), `stores/` (repositorios de durabilidad), `core/` (config/constants), `models/`, `security/`.
- `backend/app/services/prizes` — contexto acotado DDD (Wave previa): `calculator.py` (cálculo puro) + `team_prizes_writer.py` (persistencia atómica).
- `backend/app/services/analytics` — contexto acotado DDD (Wave 1): `domain/ports.py`, `application/calculations.py`, `infrastructure/data_manager_adapter.py`, `facade.py`.
- `backend/app/services/assistant` — contexto acotado DDD (Wave 2, FR13): `domain/`, `application/`, `infrastructure/`, `facade.py`.
- `angular-app` — frontend Angular 22 (PWA, standalone components, signals, Material 22).
- `proxy` — nginx reverse proxy local.
- `cron` — máquinas Fly one-shot para sincronizaciones programadas.

### Build System
- **Type**: Backend Python (pip/`requirements.txt`, `pytest`); Frontend Angular CLI (npm, `@angular/build`).
- **Config Files**: `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`, `backend/Dockerfile`, `backend/fly.toml`, `angular-app/package.json`, `angular-app/angular.json`, `angular-app/eslint.config.js`, `angular-app/tsconfig*.json`, `docker-compose.yml`, `.nvmrc` (`22.22.3`).
- **Build Dependencies**: `data_sync_service` → `data_manager_v2` (DataManagerV2), `futmondo_client`, `prizes/` (`PrizeConfig`, `RoundTeamEntry`, `calculate_round_prizes`, `replace_team_prizes`), `integration_errors`, `core.config`. Router `api/v1/endpoints/sync.py` → `DataSyncService`. `data_initializer.py` → `DataSyncService.sync_all()`.

### APIs Discovered
- **REST FastAPI** — `backend/app/api/v1/endpoints/` (21 routers): `sync`, `market`, `balances`, `analytics`, `player_finances`, `transactions`, `clausulable_players`, `roster`, `sofascore_sync`, `sofascore_detail`, `user`, `user_stats`, `championships`, `favorites`, `phantoms`, `matchdays`, `statistics`, `initialize`, `reset_db` + helpers (`_helpers.py`, `_sofascore_helpers.py`). Auth JWT (`auth/routes.py`: `/auth/login|refresh|logout`).
- **Integraciones externas**: `futmondo_client.py` (API Futmondo, excepciones tipadas `Integration*Error`), `sofascore_client.py` (API Sofascore vía `curl_cffi`).
- **Sync interno**: `DataSyncService` expone 10 `sync_*` + `sync_all()` (ver Handoff Summary).

### Frameworks & Libraries
- Backend: `fastapi==0.141.1`, `uvicorn[standard]==0.54.0`, `pydantic==2.13.5`, `PyJWT==2.13.0`, `psycopg2-binary==2.9.13`, `requests==2.34.2`, `curl_cffi==0.16.3`, `google-genai==1.14.0`, `groq==0.25.0`, `python-dotenv==1.2.3`, `python-multipart==0.0.32`. Test: `pytest==9.1.1`, `pytest-cov==7.1.0`, `httpx==0.28.1`.
- Frontend: `@angular/*==^22.1.0`, `@angular/material`, `chart.js==^4.5.1`, `ng2-charts==^10.0.0`, `marked==^18.0.11`, `rxjs~7.8.0`. Test: `vitest==4.1.11`, `@vitest/coverage-v8==4.1.11`, `jsdom`.
- DB: Neon PostgreSQL (serverless). Deploy: Fly.io (`cdg`) + GitHub Actions.

### Test Coverage
- **Test Directories**: `backend/tests/` (44 ficheros, muchos `*_characterization.py`: `test_prizes_characterization.py`, `test_team_prizes_atomic_replacement.py`, `test_sofascore_sync_characterization.py`, `test_finance_characterization.py`, `test_futmondo_client_characterization.py`, `test_sync_degraded_steps.py`, `test_sync_integration_failure_effect.py`, etc.). Frontend: 14 `*.spec.ts` bajo `angular-app/src`.
- **Test Frameworks**: `pytest` (+ `pytest-cov`); Angular `ng test` (builder `@angular/build:unit-test` + Vitest).
- **Coverage Config**: backend piso BLOQUEANTE `--cov-fail-under=27` (line-only) en `pytest.ini` (medido 27.52%); frontend umbrales por métrica en `angular.json` (`coverageThresholds`: statements 15 / branches 15 / functions 13 / lines 14). Fakes in-memory en `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`, `clean_jwt_env`, `fake_db`).

### Code Quality Indicators
- **Linting**: `ruff` backend (`backend/ruff.toml`, `py312`, line-length 100, `select=["E","F","I"]`, `ignore=["E501","E402"]`), promovido a BLOQUEANTE en `ci.yml` (`ruff==0.16.9`). ESLint frontend advisory / deuda diferida (no instalado). `[lint.per-file-ignores]` registra la deuda de los god-files (`data_manager_v2.py`, `data_sync_service.py`, `assistant_service.py`, `photo_service.py`).
- **CI/CD**: `.github/workflows/ci.yml` (PR gate: gitleaks + ruff + pytest+cov + pip-audit + ng test + npm audit) y `fly-deploy.yml` (job `verify` en paridad + deploy). Allowlist versionada `backend/.pip-audit-allowlist`.
- **Documentation**: `README.md`, `docs/` extensa (DEPLOY, ROLLBACK, PR-GATE, PROJECT_CONTEXT, backlogs). Docstrings ricos en el código nuevo (waves DDD), escasos en los god-files.

### Technical Debt Signals
- **God-files**: `data_manager_v2.py` (3692 líneas, ~166 KB — SQL/acceso a datos monolítico, deuda `E722`/`F841` registrada), `data_sync_service.py` (1955 líneas, ~84 KB — OBJETIVO), `assistant_service.py` ya reducido a shim (la lógica migró a `assistant/`). `photo_service.py` (492 líneas, `E722` registrado).
- **SQL-en-router**: prácticamente todos los routers bajo `api/v1/endpoints/` contienen `cursor.execute`/SQL crudo (`sync.py`, `market.py`, `balances.py`, `analytics.py`, `transactions.py`, `favorites.py`, `clausulable_players.py`, `player_finances.py`, etc.) — patrón heredado a NO ampliar (regla afirmada).
- **`data_sync_service.py`**: 8 de 10 `sync_*` aún tienen ingesta + SQL/persistencia + cálculo mezclados en el mismo método (solo `sync_prizes` ya delega). Llamadas `time.sleep()` de throttling incrustadas. `except Exception → return {"status":"error"}` como red final por método.

## Handoff Summary

- **Intent-relevant finding**: `backend/app/services/data_sync_service.py` define la clase `DataSyncService` (L67) con exactamente las **10 funciones públicas `sync_*`** que hay que preservar, más el coordinador `sync_all()`:
  - `sync_transactions` (L135), `sync_clauses` (L452), `sync_punishments_bonuses` (L589), `sync_dream_teams_mvps` (L681), `sync_player_performance` (L842), `sync_rosters` (L1065), `sync_round_rankings` (L1215), `sync_players_full` (L1429), `sync_match_odds` (L1564), `sync_prizes` (L1622); y `sync_all` (L1925).
  - `sync_all()` (L1925-1955) es un **coordinador fino** que ya solo invoca los 10 `sync_*` en orden (players primero por FK) y agrega los resultados en un dict — es el molde del `sync_all` "thin" del target.
  - **`sync_prizes` es el patrón EXACTO a replicar por dominio**: solo orquesta (a) ingesta desde `FutmondoClient`, (b) materialización de `RoundTeamEntry`/`PrizeConfig` (L~1817-1835), (c) delegación del cálculo puro a `calculate_round_prizes(...)` de `app.services.prizes.calculator` (L1836), y (d) persistencia atómica vía `replace_team_prizes(db, championship_id, all_prizes_to_save, valid_matchdays)` de `app.services.prizes.team_prizes_writer` (L1868). Imports de delegación ya presentes en cabecera (L11-16).
  - **Set-replacement-after-repositories + escritura atómica (patrón `team_prizes_writer`)**: `replace_team_prizes` (`prizes/team_prizes_writer.py`) hace el upsert de todo el conjunto Y el `DELETE ... matchday NOT IN (...)` de filas stale en **una sola transacción** (`with db.get_connection() as conn`), all-or-nothing, propagando cualquier fallo (corrige el antiguo `try/except → logger.warning` que dejaba estado mixto). El manejo de errores tipados (`IntegrationBanError` fatal; `IntegrationTimeoutError`/`IntegrationUnparseableError`/`IntegrationRequestError` recuperables pero fatales en el punto de escritura por BR2.3) ya está modelado en `sync_prizes` (L~1888-1924) y espejado en el router `sync.py`.
  - **Waves 1-2 de referencia a espejar**: `analytics/` (Wave 1) y `assistant/` (Wave 2) ya demuestran la capa DDD objetivo — `domain/ports.py` (Protocol consumer-owned, sin SQL), `application/` (cálculo puro sobre el port), `infrastructure/*_adapter.py` (único sitio con SQL crudo sobre `DataManagerV2`), `facade.py` (servicio de aplicación fino que preserva la superficie pública), y un **shim de re-export** en la ruta histórica (`analytics_service.py`, `assistant_service.py`) para no romper imports. El decomposition del target debe crear un módulo de aplicación por dominio (transactions, clauses, punishments, dream_teams, performance, rosters, rankings, players, odds, prizes) bajo el mismo layering, manteniendo `DataSyncService` + sus 10 `sync_*` + `sync_all()` como superficie pública (probablemente vía shim/facade delegante).

- **Risks / follow-up** (para el arquitecto / siguiente etapa):
  - **Characterization-first obligatorio por dominio ANTES de partir** (mandato afirmado, `team.md`/`project.md`): de los 10 dominios, `prizes` y varios flujos de integración/degradado ya tienen suites (`test_prizes_characterization.py`, `test_team_prizes_atomic_replacement.py`, `test_sync_degraded_steps.py`, `test_sync_integration_failure_effect.py`), pero **transactions, clauses, punishments_bonuses, dream_teams_mvps, player_performance, rosters, round_rankings, players_full, match_odds no tienen caracterización directa evidente** — hay que congelarlos antes de extraerlos.
  - **NUNCA ampliar los god-files** (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router (regla afirmada); el SQL crudo de cada dominio debe caer detrás de un adaptador de infraestructura como en `analytics/infrastructure/data_manager_adapter.py`, no seguir inline.
  - **`data_manager_v2.py` (~166 KB) es la dependencia de datos común** de casi todos los `sync_*`; la extracción debe apoyarse en él vía Protocol/adapter (dependency inversion) sin tocarlo ni engordarlo.
  - **Piso de cobertura backend `--cov-fail-under=27` sube solo por trinquete**: la caracterización nueva puede subir la cobertura, pero nunca bajar el piso; verificar verde en AMBOS gates (PR + `verify`).
  - **NUNCA `ruff format` masivo** sobre los ficheros brownfield; formatear solo los ficheros nuevos de cada dominio o de forma quirúrgica (invalida el pase de revisión en vuelo si se tocan bytes de ficheros ya modificados).
  - **Detalles a preservar en la extracción de `sync_prizes`**: la lógica de pseudo-rondas adelantadas (matchday sintético negativo, `points_prize` inmediato vs `ranking/MVP/dream-team` solo con `round_fully_played`), el gating `all(m.get("status")=="F")`, y el throttling `time.sleep()` — son comportamiento observable que la caracterización debe fijar.
