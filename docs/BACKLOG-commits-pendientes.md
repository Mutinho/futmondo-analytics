# Backlog — orden de commits/arreglos pendientes

> Notas de trabajo (2026-09-12). Cambios sin commitear en el repo que quedaron de
> trabajo previo (hardening, tests, CI/CD) y del arnés AI-DLC. Este es el orden
> recomendado para dejar el repo limpio y desplegable sin arrastrar cambios ajenos.
> Regla: `git add` de rutas concretas, nunca `git add .`.

## Estado a fecha de la nota

- **Hecho:** bugfix "reemplazo transaccional de la caché de Sofascore" commiteado
  localmente en `10c9ab7` (4 ficheros de código + registros `aidlc/`), **sin push**.
  Rama `main` ahead 1.
- El pipeline `fly-deploy.yml` corre `pytest tests` COMPLETO como gate bloqueante,
  así que el deploy no pasará hasta que TODA la suite esté verde.

## Orden recomendado

1. **(Hecho)** Bugfix Sofascore: `backend/app/core/constants.py`,
   `backend/app/services/sofascore_client.py`,
   `backend/app/api/v1/endpoints/sofascore_sync.py`,
   `backend/tests/test_sofascore_sync_characterization.py` + `aidlc/`.

2. **Arreglar los 3 tests de `backend/tests/test_analytics_service.py`** (bugfix aparte).
   - Fallos: `AttributeError: 'AnalyticsService' object has no attribute '_team_cache'`
     (`test_championship_trends`, `test_clause_network`) y
     `KeyError: 'latest_price'` (`test_player_value_trend`).
   - Son preexistentes, ajenos al bugfix de Sofascore. Bloquean el gate de CI.

3. **Commit 1 — Infra de tests del backend** (para que CI tenga la suite verde):
   - `backend/conftest.py`, `backend/pytest.ini`, `backend/ruff.toml`,
     `backend/requirements.txt`
   - `backend/tests/test_auth_characterization.py`, `test_db_admin_guard.py`,
     `test_db_engine_characterization.py`, `test_finance_characterization.py`,
     `test_jwt_startup.py`
   - Mensaje sugerido: `test(backend): suite de caracterización + config pytest/ruff (red de seguridad)`
   - Incluir/preceder con el arreglo del punto 2 para que la suite quede verde.

4. **Commit 2 — CI/CD** (para activar el gate):
   - `.github/workflows/ci.yml` (nuevo), `.github/workflows/fly-deploy.yml` (mod.)
   - `docs/PR-GATE.md`, `docs/ROLLBACK.md`
   - Mensaje sugerido: `ci(deploy): gate de PR (lint+tests) + deploy Fly.io con smoke test y runbook de rollback`

5. **Commits 3-5 según prioridad:**
   - **Frontend (tooling/tests):** `angular-app/angular.json`, `package.json`,
     `tsconfig.spec.json`, `eslint.config.js` (nuevo), `karma.conf.js` (nuevo),
     `angular-app/src/app/core/interceptors/auth.interceptor.spec.ts` (nuevo).
     Mensaje: `test(frontend): configuración Karma/ESLint + spec del auth interceptor`
   - **Backend hardening (REVISAR diff antes de commitear — cambian comportamiento):**
     `backend/app/core/config.py` (+61, arranque JWT), `backend/app/api/v1/endpoints/reset_db.py` (+33, guard de reset de BD).
     Mensaje: `fix(backend): endurecer arranque JWT y guard de reset de BD`
   - **Arnés AI-DLC:** `.kiro/`, `AGENTS.md`, `aidlc.settings.json`, `.gitignore` (+90, exclusiones AI-DLC).
     Mensaje: `chore(aidlc): instalar arnés AI-DLC (skills, agentes, hooks, settings)`

## Notas

- El push del bugfix Sofascore + el deploy esperan a que la suite completa esté
  verde (punto 2 hecho) para no romper el gate de CI.
- No incluir cambios ajenos en un mismo commit; separar por tema como arriba.
