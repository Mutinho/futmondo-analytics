# Code Quality Assessment

## Cobertura de tests

- **Backend**: piso **BLOQUEANTE** `--cov-fail-under=27` (line-only, SIN
  `--cov-branch`) en `backend/pytest.ini` (`addopts = -ra --cov-fail-under=27`;
  requiere `--cov=app` en la invocación — paridad `ci.yml` ↔ job `verify` de
  `fly-deploy.yml`). Sube solo por trinquete; nunca se relaja para pasar el gate.
  Fakes in-memory en `backend/conftest.py` (`_RecordingDM`, `_FakeFutmondoClient`,
  `_FakeInMemoryDB`/`_FakeCursor` sobre SQLite `:memory:`, `clean_jwt_env`,
  `fake_db`); `time.sleep` monkeypatched a no-op: sin red, sin BD real, sin
  credenciales reales.
- **Frontend**: umbrales por métrica en `angular.json` (`coverageThresholds`:
  statements 15 / branches 15 / functions 13 / lines 14), enforcement dentro de
  `ng test` (builder `@angular/build:unit-test` + Vitest).
- **Suites de caracterización relevantes al intent (área sync)**: congelan el
  `SyncResult` observable y la posición de la clave literal en `sync_all`:
  `test_sync_match_odds_characterization.py`, `test_sync_clauses_characterization.py`
  (ambos pilotos verdes contra el código extraído → equivalencia), más
  `test_prizes_characterization.py`, `test_prizes_calculator.py`,
  `test_team_prizes_atomic_replacement.py`, `test_sync_degraded_steps.py`,
  `test_sync_step_status.py`, `test_sync_integration_failure_effect.py`.

## Linting

- **`ruff`** backend (`backend/ruff.toml`: `py312`, line-length 100,
  `select=["E","F","I"]`, `ignore=["E501","E402"]`), modo advisory escalonado hacia
  bloqueante. La deuda de los god-files se registra con `[lint.per-file-ignores]`
  en lugar de sanearla tocándolos (`E722` bare-except re-habilitado como advisory
  por trinquete).
- **ESLint frontend**: advisory / **deuda diferida** (no instalado como
  devDependency; `ci.yml` tolera su ausencia).
- Regla afirmada: **NUNCA** `ruff format` masivo sobre ficheros brownfield;
  formatear solo ficheros nuevos (por dominio) o de forma quirúrgica. La reviewer
  sólo corre `ruff check`.

## CI/CD

- **`.github/workflows/ci.yml`** (PR gate) y **`fly-deploy.yml`** job `verify`
  (push a `main`, en paridad): gitleaks + `ruff` + `pytest`+cov + `pip-audit` +
  `ng test` + `npm audit`; cadena de deploy `verify` → `deploy-backend` →
  `deploy-frontend` → `smoke-test` (Fly.io on-merge, región `cdg`). No leídos en
  profundidad (fuera del área focalizada). Allowlist versionada
  `backend/.pip-audit-allowlist`. Crons de coste ~0: `daily-sync.yml`,
  `sofascore-sync.yml`.

## Calidad de documentación

- `README.md` completo; `docs/` extensa.
- Docstrings ricos y en INGLÉS en el código nuevo (`match_odds/*`, `clauses/*`,
  `prizes/*`), citando reglas de negocio (BR*, FR*, NFR*); **escasos en los
  god-files**, que mezclan orquestación, SQL inline y throttling.

## Deuda técnica (foco del scan: dominio sync)

- **God-files — NEVER ampliar/reescribir (regla afirmada)**:
  - `data_sync_service.py` (~1806 líneas, ~77 KB) — **objetivo del intent**;
    `sync_match_odds` y `sync_clauses` ya delegan, `sync_prizes` delega
    cálculo/escritura. Alberga 8 dominios inline + 5 helpers privados.
  - `data_manager_v2.py` (~3692 líneas, ~166 KB) — SQL/acceso a datos monolítico;
    dependencia común. **NO ampliar/reescribir**; los adapters la envuelven
    verbatim.
  - `photo_service.py` (~492 líneas) — `E722` registrado.
- **SyncResult NO uniforme entre dominios**: `round_rankings` devuelve
  `rounds_synced`/`last_matchday`; `players_full` no devuelve `last_sync_*`;
  `prizes` tiene el set de status más rico (`no_config`/`no_prizes_configured`/
  `no_standings`/`no_teams`/`no_rounds` + early-returns). Cada orquestador debe
  reproducir su payload byte-a-byte (riesgo de regresión).
- **Characterization-first gap (mandato de equipo)**: los 8 dominios inline
  (`transactions`, `punishments_bonuses`, `dream_teams_mvps`,
  `player_performance`, `rosters`, `round_rankings`, `players_full`) **NO tienen
  test de caracterización dedicado todavía**. Hay que congelar el `SyncResult`
  observable y el modo de fallo (recuperable vs fatal) por dominio ANTES de
  extraer, como ya se hizo para `match_odds`/`clauses`.
- **SQL crudo sobre `self.dm.db` dentro de métodos de servicio (no sólo en el
  DataManager)**: `sync_transactions` (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
  oportunista en caliente + UPDATE `bids_json`), `_enrich_market_values`
  (`SELECT`/`UPDATE`), `_save_favorites` (`CREATE TABLE IF NOT EXISTS` +
  `DELETE`/`INSERT`, rama Postgres `psycopg2.extras.execute_values`), `sync_prizes`
  (`SELECT ... FROM user_championships` vía `get_db()`). El router `sync.py`
  también tiene SQL inline (`_check_phantoms`, `get_last_sync_date`) — patrón
  SQL-en-router a NO ampliar. El SQL debe envolverse **verbatim** tras
  port+adapter, SIN reescribirlo ni ampliar `data_manager_v2.py`.
- **Broad/bare excepts**: 1 `except: pass` silencioso (`ALTER TABLE` idempotente
  en `sync_transactions`); el enriquecimiento de market value y la limpieza de
  huérfanos degradan con `logger.warning`. Son deuda registrada de intents previos
  (god-file) — NO entran al alcance de este refactor salvo que el patrón atómico
  los sustituya.
- **Dependencia de clave literal divergente (alto riesgo de regresión)**:
  `team_standings`≠`sync_round_rankings` y `dream_teams`≠`sync_dream_teams_mvps`;
  el worker del router (`_run_sync_in_background`) depende de esas claves
  literales. Cualquier cambio de surface rompería el worker — mantener firma y
  retorno idénticos (FR5).
- **Comportamiento de ingesta a preservar por dominio**: `time.sleep`
  (0.3/0.2/0.1/0.05), límites de paginación (50 vs 1000), condiciones de parada
  (misses consecutivos, `previous_last_id`), y la lógica de pseudo-rounds
  avanzados de prizes (número float → matchday sintético negativo).
  `_find_championship()` lo comparten `dream_teams` y `rosters`.
- **Manejo de errores tipado a preservar**: `_log_integration_failure` (log
  key=value sin credenciales, NFR1/BR4.2) y clasificación fatal
  (`IntegrationBanError` propaga) vs recoverable (`IntegrationTimeout/Unparseable/
  Request` → `record_degraded_step`). Ninguna credencial/token debe llegar a
  mensajes de excepción, `repr` ni logs en los adapters extraídos.
- **Reemplazo de conjunto atómico** (`team_prizes_writer`) es el patrón de
  referencia para full-refresh; `_save_favorites` (DELETE+INSERT) es candidato a
  elevarse o quedar como deuda registrada según el alcance refactor/Minimal.
