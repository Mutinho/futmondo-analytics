# Code Quality Assessment

## Cobertura de tests

- **Backend**: piso **BLOQUEANTE** `--cov-fail-under=27` (line-only, SIN
  `--cov-branch`) en `backend/pytest.ini` (`addopts = -ra --cov-fail-under=27`;
  requiere `--cov=app` en la invocación — paridad `ci.yml` ↔ job `verify` de
  `fly-deploy.yml`; medido ~27.52%). Sube solo por trinquete; nunca se relaja para
  pasar el gate. Fakes in-memory en `backend/conftest.py`
  (`_FakeInMemoryDB`/`_FakeCursor` sobre SQLite `:memory:`, `clean_jwt_env`,
  `fake_db`): sin red, sin BD real, sin credenciales reales.
- **Frontend**: umbrales por métrica en `angular.json` (`coverageThresholds`:
  statements 15 / branches 15 / functions 13 / lines 14), enforcement dentro de
  `ng test` (builder `@angular/build:unit-test` + Vitest).
- **Suites de caracterización relevantes al intent (backend, ~39 ficheros
  `test_*.py`)**: existen para `match_odds` (`test_sync_match_odds_characterization.py`,
  piloto congelado), `prizes` (`test_prizes_calculator.py`,
  `test_prizes_characterization.py`, `test_team_prizes_atomic_replacement.py`), y
  flujos de integración/degradado (`test_sync_degraded_steps.py`,
  `test_sync_integration_failure_effect.py`, `test_sync_step_status.py`,
  `test_sofascore_sync_characterization.py`, `test_futmondo_client_characterization.py`).

## Linting

- **`ruff`** backend (`backend/ruff.toml`: `py312`, line-length 100,
  `select=["E","F","I"]`, `ignore=["E501","E402"]`), modo advisory escalonado hacia
  bloqueante. `[lint.per-file-ignores]` registra la deuda de los god-files en lugar
  de sanearla tocándolos: `data_manager_v2.py` → `["E722","F841","F401","I001"]`;
  `data_sync_service.py` → `["F401","I001"]`; `assistant_service.py` → `["I001"]`;
  `photo_service.py` → `["E722","F841"]`. `E722` (bare-except) re-habilitado como
  advisory por trinquete.
- **ESLint frontend**: advisory / **deuda diferida** (no instalado como
  devDependency; `ci.yml` tolera su ausencia).
- Regla afirmada: **NUNCA** `ruff format` masivo sobre ficheros brownfield;
  formatear solo ficheros nuevos (por dominio) o de forma quirúrgica. La reviewer
  sólo corre `ruff check`.

## CI/CD

- **`.github/workflows/ci.yml`** (PR gate): gitleaks + `ruff` + `pytest`+cov +
  `pip-audit` + `ng test` + `npm audit`.
- **`.github/workflows/fly-deploy.yml`** (push a `main`): job `verify` en
  **paridad** con `ci.yml` + deploy (cadena `verify` → `deploy-backend` →
  `deploy-frontend` → `smoke-test`). Deploy Fly.io on-merge (región `cdg`).
- Allowlist versionada `backend/.pip-audit-allowlist` para findings sin fix.
- Crons de coste ~0: `daily-sync.yml`, `sofascore-sync.yml`.

## Calidad de documentación

- `README.md` completo; `docs/` extensa (DEPLOY, ROLLBACK, PR-GATE,
  PROJECT_CONTEXT, backlogs).
- Docstrings ricos y en INGLÉS en el código nuevo (`match_odds/*`, `prizes/*`),
  citando reglas de negocio (BR*, FR*, NFR*) y preservación de surface; **escasos
  en los god-files**, que mezclan orquestación, SQL inline y throttling.

## Deuda técnica (foco del scan: dominio sync)

- **God-files**:
  - `data_sync_service.py` (1918 líneas, ~84 KB) — **objetivo del intent**;
    `sync_match_odds` ya delega, `sync_prizes` delega parcialmente.
  - `data_manager_v2.py` (3692 líneas, ~166 KB) — SQL/acceso a datos monolítico;
    deuda `E722`/`F841` registrada. Dependencia común, **no ampliar/reescribir**.
  - `photo_service.py` (492 líneas) — `E722` registrado.
- **Broad/bare excepts en el god-file**: 27 `except Exception`/`except:` detectados;
  1 `except: pass` silencioso (`ALTER TABLE ... ADD COLUMN` idempotente en
  `sync_transactions`). Múltiples `except ...: logger.warning/debug ... continue`
  tragan fallos por página/ronda/equipo.
- **SQL dentro de métodos de servicio (no sólo en el DataManager)**:
  `sync_transactions` ejecuta `ALTER TABLE` y `UPDATE transactions SET bids_json`;
  `_enrich_market_values` hace `SELECT`/`UPDATE`; `_save_favorites` hace
  `CREATE TABLE IF NOT EXISTS`/`DELETE`/`INSERT`; `sync_prizes` abre `get_db()` y
  hace `SELECT ... FROM user_championships`. El router `sync.py` también tiene SQL
  inline (`_check_phantoms`, `get_last_sync_date`) — patrón SQL-en-router a NO
  ampliar. El SQL debe migrar a un adapter de infraestructura por dominio.
- **Acoplamiento ingestión+persistencia+throttling**: cada `sync_*` pendiente
  mezcla `FutmondoClient` + `time.sleep` + mapeo de rondas + escritura vía `self.dm`
  inline — justo lo que el piloto `match_odds` separa en orchestrator + port +
  adapter.
- **`sync_prizes` es el más complejo** (~300 líneas): pseudo-rondas adelantadas
  (matchday sintético negativo), gating `round_fully_played` (status "F"),
  detección de MVP/dream-team por lineup, acumulación para reemplazo atómico. Ya
  delega cálculo (`prizes.calculator`) y escritura atómica
  (`prizes.team_prizes_writer`), pero NO está envuelto en facade/orchestrator de
  dominio como `match_odds`.
- **8 dominios de sync sin caracterización directa**: `clauses`, `transactions`,
  `punishments_bonuses`, `dream_teams`, `rosters`, `round_rankings`→`team_standings`,
  `player_performance`, `players_full` no tienen cobertura de caracterización
  directa. **Characterization-first obligatorio** (mandato afirmado): congelar el
  `SyncResult` observable por dominio (claves `status`/`records_synced`/
  `last_sync_id`/`last_sync_matchday`/`rounds_synced`/`duration_seconds` según el
  dominio) ANTES de extraer. Las formas NO son uniformes entre dominios.
- **Manejo de errores tipado a preservar**: `_log_integration_failure` (log
  key=value sin credenciales, NFR1/BR4.2) y clasificación fatal
  (`IntegrationBanError` propaga) vs recoverable (`IntegrationTimeout/Unparseable/
  Request` → `record_degraded_step`) en `sync_prizes` y en el worker del router.
  Implicación de seguridad: ninguna credencial/token debe llegar a mensajes de
  excepción, `repr` ni logs en los adapters extraídos.
- **Contrato del worker del router**: `_run_sync_in_background` replica el
  orden/claves de `sync_all` y añade `phantoms` fuera del surface de
  `DataSyncService`; cualquier cambio de surface rompería el worker — mantener
  firma y retorno idénticos (FR5).
