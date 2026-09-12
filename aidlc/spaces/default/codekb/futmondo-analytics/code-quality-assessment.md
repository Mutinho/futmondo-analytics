# Evaluación de Calidad del Código — Futmondo Analytics

> Reverse-engineering (escaneo FULL). Cobertura de tests, linting, CI/CD, calidad
> de documentación y deuda técnica, según la evidencia del scan y el código.

## Cobertura de tests

- **Backend**: `backend/tests/` con 6 ficheros de **caracterización** (congelan el
  comportamiento actual, metodología `custom` characterization-first, ver
  `conftest.py`): `test_analytics_service.py` (con fakes de `DataManager`),
  `test_auth_characterization.py`, `test_db_admin_guard.py`, `test_jwt_startup.py`,
  `test_db_engine_characterization.py`, `test_finance_characterization.py`.
  `--cov=app` disponible pero **sin piso bloqueante** (`pytest.ini`).
- **Frontend**: **cobertura efectivamente ~0**. Solo existe
  `angular-app/src/app/core/interceptors/auth.interceptor.spec.ts` (1 test).
  `angular.json` fija `skipTests: true` en todos los schematics → los componentes
  y servicios nuevos nacen sin test. `karma-coverage` está configurado (report
  html + text-summary) pero sin umbral.
- **Asimetría**: `ci.yml` marca `ng test` como bloqueante, pero el gate pasa con
  cobertura casi nula porque apenas hay specs.

## Linting y formato

- **Backend**: ruff (`ruff.toml`, `select=["E","F","I"]`, con `E501/E402/E722`
  ignorados en base heredada). Modo **ADVISORY** en CI. Formato con ruff format.
- **Frontend**: ESLint (`eslint.config.js`), `ng lint` **ADVISORY** en CI. Formato
  con Prettier (`.prettierrc`).

## CI/CD

Cuatro workflows GitHub Actions:

| Workflow | Trigger | Gates |
|----------|---------|-------|
| `ci.yml` | PR → main | **BLOQUEANTE**: gitleaks, pytest, `ng test`. **ADVISORY**: ruff, ESLint, pip-audit, npm audit (decisión escalonada R-05). |
| `fly-deploy.yml` | push → main | job `verify` (pytest + ng test) → deploy backend → deploy frontend → smoke test `/health`. |
| `daily-sync.yml` | cron | job one-shot en Fly con polling de estado y verificación de exit code. |
| `sofascore-sync.yml` | cron | one-shot; trata exit code 2 (baneo IP Sofascore) explícitamente. |

Procesos documentados en `docs/PR-GATE.md` y `docs/ROLLBACK.md`.

## Calidad de la documentación

- `README.md` completo (arquitectura, stack, deploy, endpoints).
- `docs/` rico: `PROJECT_CONTEXT`, planes de migración, `DEPLOY`, `ROLLBACK`,
  `PR-GATE`.
- Comentarios en castellano con referencias a NFRs/FRs (endurecimiento previo ya
  aplicado). Organización general por capas/feature razonable.

## Deuda técnica

- **God files**: `data_manager_v2.py` (166 KB / ~4.700 líneas),
  `data_sync_service.py` (84 KB), `assistant_service.py` (51 KB),
  `analytics_service.py` (34 KB). Superan con creces el objetivo de <300 líneas;
  concentran riesgo de cambio e intestables sin fakes.
- **Manejo de errores demasiado amplio**: 159 `except Exception` y 6 `except:`
  desnudos en `backend/app`; varios `except Exception: pass` silenciosos
  (`token_store.init_auth_tables`, `_ensure_conversations_table` en `assistant.py`,
  `_auto_detect_championships` en `auth/routes.py`) que enmascaran fallos.
- **Estado no durable en memoria**: `TaskManager` y `SessionStore` son singletons
  in-memory; un reinicio Fly (`auto_stop_machines`/restart) pierde tareas de sync y
  sesiones → 403 "sesión expirada" y tareas huérfanas. `SessionStore` guarda
  email+password en claro en memoria.
- **Config heredada / entornos mezclados**: `config.py` con 3 backends de BD
  (SQLite/Turso/PostgreSQL) y ramas muertas; `nixpacks.toml` (Railway) y
  `migrate_to_turso.py` residuales; `constants.py` con `CHAMPIONSHIP_ID`/`LEAGUE_ID`
  hardcodeados.
- **`docker-compose.yml` fija `SSL_VERIFY=0`** en backend (local) — patrón de
  deshabilitar TLS; confirmar que no se propaga a producción.
- **Bug potencial**: `token_store.is_refresh_token_valid` con ternario ambiguo
  (naive/aware datetimes) que puede evaluar mal la expiración.
- **Doble montaje de rutas**: `matchdays` bajo `/api/v1/matchdays` y `/v1/matchdays`.
- **Script muerto**: `entrypoint.sh` no referenciado por el `Dockerfile` (usa
  `CMD uvicorn ...`).
- **Artefactos versionados innecesarios**: imágenes sueltas (`42874.jpg`,
  `IMG_9904.PNG`), dirs `stitch_*` y ficheros `:Zone.Identifier` en la raíz.
- **Validación de entrada**: `market.py::place_bid` acepta `price` sin validar
  rango/positividad en backend (solo el frontend valida min/max).

## Postura de seguridad (positivo)

Endurecimiento presente y correcto: JWT fail-fast (`config.py::resolve_jwt_secret`),
endpoints destructivos tras `ENABLE_DB_ADMIN` (404 por defecto), refresh HttpOnly,
CORS con whitelist, gitleaks bloqueante en CI.
