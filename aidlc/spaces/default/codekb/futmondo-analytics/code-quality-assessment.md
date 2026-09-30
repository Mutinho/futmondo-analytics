# Code Quality Assessment

## Cobertura de tests

- **Backend**: piso **BLOQUEANTE** `--cov-fail-under=27` (line-only) en
  `backend/pytest.ini` (medido 27.52%). Sube solo por trinquete; nunca se relaja
  para pasar el gate. Fakes in-memory en `backend/conftest.py`
  (`_FakeInMemoryDB`/`_FakeCursor`, `clean_jwt_env`, `fake_db`): sin red, sin BD
  real, sin credenciales reales.
- **Frontend**: umbrales por métrica en `angular.json` (`coverageThresholds`:
  statements 15 / branches 15 / functions 13 / lines 14), enforcement dentro de
  `ng test` (builder `@angular/build:unit-test` + Vitest).
- **Suites de caracterización** (backend, 44 ficheros de test): existen para
  `prizes` y flujos de integración/degradado —
  `test_prizes_characterization.py`, `test_team_prizes_atomic_replacement.py`,
  `test_sofascore_sync_characterization.py`, `test_finance_characterization.py`,
  `test_futmondo_client_characterization.py`, `test_sync_degraded_steps.py`,
  `test_sync_integration_failure_effect.py`. Frontend: 14 `*.spec.ts`.

## Linting

- **`ruff`** backend (`ruff==0.16.9`, `backend/ruff.toml`: `py312`, line-length
  100, `select=["E","F","I"]`, `ignore=["E501","E402"]`), promovido a
  **BLOQUEANTE** en `ci.yml`. `[lint.per-file-ignores]` registra la deuda de los
  god-files (`data_manager_v2.py`, `data_sync_service.py`, `assistant_service.py`,
  `photo_service.py`).
- **ESLint frontend**: advisory / **deuda diferida** (no instalado como
  devDependency; `ci.yml` tolera su ausencia).
- Regla afirmada: **NUNCA** `ruff format` masivo sobre ficheros brownfield;
  formatear solo ficheros nuevos o de forma quirúrgica.

## CI/CD

- **`.github/workflows/ci.yml`** (PR gate): gitleaks + `ruff` + `pytest`+cov +
  `pip-audit` + `ng test` + `npm audit`.
- **`.github/workflows/fly-deploy.yml`** (push a `main`): job `verify` en
  **paridad** con `ci.yml` + deploy (cadena `verify` → `deploy-backend` →
  `deploy-frontend` → `smoke-test`).
- Allowlist versionada `backend/.pip-audit-allowlist` para findings sin fix.
- Crons de coste ~0: `daily-sync.yml`, `sofascore-sync.yml`.

## Calidad de documentación

- `README.md` completo; `docs/` extensa (DEPLOY, ROLLBACK, PR-GATE,
  PROJECT_CONTEXT, backlogs).
- Docstrings ricos en el código nuevo (waves DDD `analytics/`, `assistant/`,
  `prizes/`); **escasos en los god-files**.

## Deuda técnica

- **God-files**:
  - `data_manager_v2.py` (3692 líneas, ~166 KB) — SQL/acceso a datos monolítico;
    deuda `E722`/`F841` registrada. Dependencia común, **no ampliar**.
  - `data_sync_service.py` (1955 líneas, ~84 KB) — **objetivo del intent**.
  - `photo_service.py` (492 líneas) — `E722` registrado.
  - `assistant_service.py` — ya reducido a shim (lógica migrada a `assistant/`).
- **SQL-en-router**: prácticamente todos los routers bajo `api/v1/endpoints/`
  ejecutan SQL crudo inline (`sync`, `market`, `balances`, `analytics`,
  `transactions`, `favorites`, `clausulable_players`, `player_finances`, …).
  Patrón heredado a **NO ampliar**; el SQL debe caer tras un adaptador de
  infraestructura.
- **8 dominios de sync sin caracterización directa**: de los 10 `sync_*`, solo
  `sync_prizes` delega y varios flujos de integración/degradado tienen suites;
  **`transactions`, `clauses`, `punishments_bonuses`, `dream_teams_mvps`,
  `player_performance`, `rosters`, `round_rankings`, `players_full`, `match_odds`**
  no tienen caracterización directa evidente. **Characterization-first obligatorio**
  (mandato afirmado) antes de extraer cada dominio.
- **Métodos mixtos + red de error genérica**: 8 de 10 `sync_*` mezclan ingesta +
  SQL/persistencia + cálculo; `except Exception → return {"status":"error"}` como
  red final; `time.sleep()` de throttling incrustado.
- **Comportamiento observable a preservar** (`sync_prizes`): pseudo-rondas
  adelantadas (matchday sintético negativo), gating `round_fully_played` /
  `all(m.get("status")=="F")`, throttling. Ver `api-documentation.md`.
