# Developer Code Scan — Futmondo Analytics

> Handoff del link 1 (developer) del pipeline de Reverse Engineering. El architect (link 2) sintetiza esto en los artefactos del CodeKB. Este documento NO es el CodeKB.
> Intent activo: `260914-ci-tooling-mejoras` (mejoras técnicas de CI/tooling). Scope: `refactor`. Profundidad: Minimal. Escaneo: FULL RESCAN sobre la raíz del repo (`./`).

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply**:
  - `./angular-app/package.json`
  - `./angular-app/angular.json`
  - `./angular-app/karma.conf.js`
  - `./angular-app/eslint.config.js`
  - `./angular-app/tsconfig.spec.json`
  - `./angular-app/src/app/app.config.ts`
  - `./angular-app/src/app/version.ts`
  - `./angular-app/package-lock.json` (engines de Node + dependencia transitiva `punycode`)
  - `./angular-app/Dockerfile`
  - `./angular-app/fly.toml`
  - `./.github/workflows/ci.yml`
  - `./.github/workflows/fly-deploy.yml`
  - `./.github/workflows/daily-sync.yml`
  - `./.github/workflows/sofascore-sync.yml`
  - `./backend/requirements.txt`
  - `./backend/pytest.ini`
  - `./backend/ruff.toml`
  - `./backend/nixpacks.toml`
  - `./backend/Dockerfile`
  - `./backend/fly.toml`
  - `./backend/entrypoint.sh`
  - `./backend/app/main.py` (montaje de routers, middleware de auth, endpoints raíz/health/foto)
  - `./cron/fly.toml`
  - `./docker-compose.yml`
- **Skimmed only**:
  - `./angular-app/src/app/features/` (17 features; inventario a nivel de directorio, sin lectura profunda de cada componente)
  - `./angular-app/src/app/core/` (services, interceptors, guards, models — clasificados por nombre/ruta)
  - `./angular-app/src/app/shared/` (components, pipes, utils, styles)
  - `./backend/app/services/` (12 módulos; clasificados por nombre/tamaño, sin lectura línea a línea)
  - `./backend/app/api/v1/endpoints/` (~24 routers; inventario por fichero)
  - `./backend/app/auth/`, `./backend/app/core/`, `./backend/app/models/`
  - `./backend/scripts/` (scripts de sync/migración)
  - `./backend/tests/` (7 ficheros de tests; conteo y framework)
  - `./docs/` (documentación de proyecto y backlogs)
  - `./proxy/nginx.conf`, `./angular-app/nginx.conf`, `./angular-app/nginx.prod.conf`, `./angular-app/ngsw-config.json`
  - `./stitch_*` (mockups de diseño estáticos, fuera del código de app)

### Packages Found

- **angular-app** — aplicación (application) — TypeScript — Frontend Angular 22 PWA (Material, signals, standalone components, service worker). `package.name = angular-app`, `version 2.1.7`.
- **backend** — servicio web (service) — Python 3.12 — API FastAPI (`app.main:app`), integraciones Futmondo/Sofascore, capa de datos PostgreSQL/libsql, servicio de assistant (IA), fotos.
- **cron** — proceso worker one-shot — reutiliza `backend/Dockerfile`; ejecuta `python scripts/sync_data.py` en una máquina Fly efímera (app `futmondo-cron`).
- **proxy** — nginx reverse proxy (`nginx:alpine`) — enrutado local para docker-compose.

### Build System

- **Type**: npm (frontend, `packageManager: npm@11.12.1`, builder `@angular/build`); pip/requirements.txt (backend); Docker multi-stage; Fly.io (`flyctl`) para deploy; nixpacks.toml presente (config Railway heredada, target `python311`).
- **Config Files**: `angular-app/angular.json`, `angular-app/package.json`, `angular-app/tsconfig*.json`, `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`, `backend/nixpacks.toml`, `docker-compose.yml`, `*/Dockerfile`, `*/fly.toml`, `.github/workflows/*.yml`.
- **Build Dependencies**:
  - Frontend build: `@angular/build:application` → `tsconfig.app.json`; serve `@angular/build:dev-server`; test `@angular/build:unit-test` (`runner: karma`).
  - Frontend Docker: `node:24-alpine` (stage build, `npm ci` + `ng build --configuration=production`) → `nginx:alpine` (stage serve, `NGINX_CONF` build-arg = `nginx.prod.conf` en Fly).
  - Backend Docker: `python:3.12-slim` → `pip install -r requirements.txt` → `uvicorn app.main:app`.
  - cron → depende del `backend/Dockerfile` (mismo build, distinto proceso).

### APIs Discovered

- **REST interna (FastAPI)** — `backend/app/main.py` — routers montados:
  - Auth (sin prefijo `/api/v1`): `/auth/*` (`app/auth/routes.py`) — login/refresh/logout; excluidos de auth middleware: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/health`, `/`, `/docs`, `/openapi.json`, `/redoc`.
  - `/api/v1/*` (protegidos por `AuthMiddleware`, Bearer JWT): `matchdays`, `initialize`, `database` (reset_db), `statistics`, `player-finances`, `user-stats`, `clausulable-players`, `sync`, `analytics` (+ `balances`, `phantoms`), `championships` (prefijo `/api/v1`), `market`, `roster`, `favorites`, `transactions`, `sofascore` (sync + detail), `user`, `assistant`.
  - No-API: `GET /`, `GET /health` (usado por smoke test y healthchecks), `GET /api/v1/photos/{player_id}` (fotos con fallback SVG), montaje estático `/static/photos`.
  - CORS whitelist: `https://futmondo-app.fly.dev`, `http://futmondo.localhost`, `http://localhost:4200`, `http://localhost:3000` (+ `EXTRA_CORS_ORIGIN`).
- **Integraciones externas (cliente)** — `backend/app/services/futmondo_client.py` (API Futmondo), `backend/app/services/sofascore_client.py` (API Sofascore vía `curl_cffi`), `assistant_service.py` (IA: `google-genai`, `groq`).

### Frameworks & Libraries

Frontend (`angular-app/package.json`):
- `@angular/animations` — `^22.1.0` — presente como dependencia; ver Deuda técnica (uso real mínimo).
- `@angular/cdk`, `@angular/common`, `@angular/compiler`, `@angular/core`, `@angular/forms`, `@angular/material`, `@angular/platform-browser`, `@angular/router`, `@angular/service-worker` — `^22.1.0`.
- `chart.js` — `^4.5.1`; `ng2-charts` — `^10.0.0`; `marked` — `^18.0.11`; `rxjs` — `~7.8.0`; `tslib` — `^2.3.0`.
- devDeps: `@angular/build`/`@angular/cli` — `^22.1.2`; `@angular/compiler-cli` — `^22.1.0`; `typescript` — `~6.0.2`; `prettier` — `^3.8.1`.
- devDeps de test (Karma, target de migración): `karma` — `~6.4.0`, `karma-chrome-launcher` — `~3.2.0`, `karma-coverage` — `~2.2.0`, `karma-jasmine` — `~5.1.0`, `karma-jasmine-html-reporter` — `~2.1.0`, `jasmine-core` — `~5.4.0`, `@types/jasmine` — `~5.1.0`.

Backend (`backend/requirements.txt`):
- `fastapi>=0.104.0`, `uvicorn[standard]>=0.24.0`, `pydantic>=2.5.0`, `python-multipart>=0.0.6`, `requests>=2.31.0`, `python-dotenv>=1.0.0`.
- `psycopg2-binary>=2.9.9` (Neon PostgreSQL), `libsql-experimental==0.0.55` (Turso/libsql heredado), `curl_cffi>=0.16.0` (Sofascore), `PyJWT==2.9.0`.
- IA: `google-genai==1.14.0`, `groq==0.25.0`.
- test: `pytest>=8.0.0`, `pytest-cov>=5.0.0`, `httpx>=0.27.0`.

### Test Coverage

- **Test Directories**: `backend/tests/` (7 ficheros: `test_analytics_service.py`, `test_sofascore_sync_characterization.py`, `test_auth_characterization.py`, `test_db_admin_guard.py`, `test_jwt_startup.py`, `test_db_engine_characterization.py`, `test_finance_characterization.py`); frontend specs junto al código (`src/app/core/interceptors/auth.interceptor.spec.ts` — único `.spec.ts` presente).
- **Test Frameworks**:
  - Backend: `pytest` (config en `pytest.ini`: `testpaths = tests`, `pythonpath = .`, `addopts = -ra`, `filterwarnings = ignore::DeprecationWarning`) + `pytest-cov` + `httpx` (para `starlette.testclient.TestClient`). `conftest.py` presente.
  - Frontend: runner **Karma** vía `@angular/build:unit-test` (`runner: karma`) con Jasmine. `karma.conf.js` define launcher `ChromeHeadlessNoSandbox` (flags `--no-sandbox --disable-gpu --disable-dev-shm-usage`) para CI containerizado; `singleRun: false` en el fichero, ejecutado con `--watch=false` en CI. `tsconfig.spec.json` incluye `types: ["jasmine"]` e `include: src/**/*.spec.ts`. angular.json `test.options.browsers = ["ChromeHeadless"]`.
- **Coverage Config**: Backend `--cov=app --cov-report=term-missing` (informativo, sin piso bloqueante). Frontend `karma-coverage` (reporters `html` + `text-summary`, dir `./coverage/angular-app`).

### Code Quality Indicators

- **Linting**: Backend `ruff` (`backend/ruff.toml`, `target-version = py312`, `line-length = 100`, `select = [E, F, I]`, `ignore = [E501, E402, E722]`) — advisory en CI. Frontend ESLint flat config (`angular-app/eslint.config.js`, `typescript-eslint` + `angular-eslint`, reglas degradadas a `warn`) — advisory; NOTA: `eslint`/`typescript-eslint`/`angular-eslint` aún NO están en devDependencies (el propio comentario del fichero indica que se añaden al adoptar el gate bloqueante). Prettier `^3.8.1` (frontend), formato ruff (backend). `.prettierrc`, `.editorconfig` presentes.
- **CI/CD**: 4 workflows en `.github/workflows/`:
  - `ci.yml` (CI Gate en PR→main): gitleaks (BLOQUEANTE), pytest+cobertura (BLOQUEANTE), `ng test` headless (BLOQUEANTE); ruff, ESLint, pip-audit, npm audit en modo advisory.
  - `fly-deploy.yml` (push→main): job `verify` (pytest + ng test) → `deploy-backend` → `deploy-frontend` → `smoke-test` contra `/health`.
  - `daily-sync.yml` (cron 4:30 UTC) y `sofascore-sync.yml` (cron 5:00 UTC): orquestan máquinas Fly one-shot (coste ~0).
- **Documentation**: `README.md` raíz + `angular-app/README.md`; `docs/` extenso (DEPLOY, ROLLBACK, PR-GATE, PROJECT_CONTEXT, REVERSE_ENGINEERING, planes de migración, `BACKLOG-mejoras-ci-tooling.md`).

### Technical Debt Signals

- **GitHub Actions con majors desactualizados** (target del intent, tarea 1): `.github/workflows/ci.yml` y `fly-deploy.yml` usan `actions/setup-node@v4` y `actions/setup-python@v5` con `node-version: '22'`. `checkout@v5` ya actualizado. Hay que llevar los setup-* a majors Node24-compatibles y fijar Node local/CI a `>=22.22.3` (los 4 workflows deben quedar consistentes; `daily-sync.yml`/`sofascore-sync.yml` sólo usan `checkout@v5` + `setup-flyctl@master`).
- **`punycode` DEP0040** (tarea 2): `angular-app/package-lock.json` contiene `punycode@1.4.1` como dependencia transitiva (líneas ~4437/7653). Origen del `DeprecationWarning DEP0040`; resolver vía `overrides`/dedupe de deps transitivas sin coste.
- **Migración de animaciones a Angular 22** (tarea 3): superficie **mínima**. En `src` NO hay imports de `@angular/animations` ni uso de `trigger()/state()/transition()`; sólo `provideAnimationsAsync()` (desde `@angular/platform-browser/animations/async`) en `app.config.ts`. La dependencia `@angular/animations@^22.1.0` sigue declarada en `package.json`. La migración a `animate.enter`/`animate.leave` afecta sólo a animaciones declarativas si aparecen en plantillas/CSS; el proveedor async y Material siguen siendo válidos. Confirmar en la fase de análisis si alguna plantilla usa animaciones antes de retirar la dependencia.
- **EBADENGINE / Node local** (tarea 5): `package-lock.json` exige `node: ^22.22.3 || ^24.15.0 || >=26.0.0` en múltiples paquetes Angular 22; NO existe `.nvmrc`. Alinear Node local a `>=22.22.3` (vía nvm) y añadir `.nvmrc` para reproducibilidad.
- **Runner Karma → Vitest** (tarea 4): angular.json `test.builder = @angular/build:unit-test` con `runner: karma`. Migrar a `runner: vitest`, retirar `karma.conf.js` y las 5 devDependencies de Karma + `jasmine-core`/`@types/jasmine`; ajustar `tsconfig.spec.json` (`types`) y los comandos `ng test --browsers=ChromeHeadless` en `ci.yml`/`fly-deploy.yml`. RIESGO: sólo hay 1 `.spec.ts` real (`auth.interceptor.spec.ts`), en Jasmine; la migración debe portar su API (Jasmine → Vitest) o el gate de tests frontend quedará vacío/roto.
- **Deuda heredada menor**: `libsql-experimental==0.0.55` y `nixpacks.toml` (Railway, `python311`) parecen restos de una etapa previa (el deploy actual es Fly.io + Neon PostgreSQL); confirmar si siguen vivos. `ng build` de producción usa `NODE_TLS_REJECT_UNAUTHORIZED=0` (Google Fonts) — señal de seguridad a revisar fuera de scope.

## Handoff Summary

- **Intent-relevant finding**: Las 5 tareas del intent tienen superficie acotada y verificable en ficheros concretos: workflows en `.github/workflows/ci.yml` y `fly-deploy.yml` (setup-node/setup-python + `node-version: '22'`); `punycode@1.4.1` transitivo en `angular-app/package-lock.json`; animaciones con superficie mínima (sólo `provideAnimationsAsync()` en `app.config.ts`, sin `trigger()`); runner Karma en `angular.json` (`@angular/build:unit-test`, `runner: karma`) con las devDeps de Karma en `package.json`; y engines `^22.22.3 || ^24.15.0` sin `.nvmrc`.
- **Risks / follow-up**:
  1. Migración a Vitest: sólo existe **un** spec real (`auth.interceptor.spec.ts`, Jasmine) — hay que portarlo o el gate frontend BLOQUEANTE queda sin cobertura efectiva. Verificar `npm ci` + `ng test` en local antes de pushear (regla de proyecto: no romper el gate de CI al tocar devDependencies del frontend).
  2. Coste 0€: todas las tareas se resuelven en tiers gratuitos (GitHub Actions free, deps npm/pip sin gasto); no introducir dependencias con coste recurrente.
  3. La tarea de animaciones puede reducirse a retirar la dependencia si no hay animaciones declarativas en plantillas — confirmar con un barrido de `.html` antes de eliminar `@angular/animations`.
  4. ESLint advisory referencia `angular-eslint`/`typescript-eslint`/`eslint` que aún no están instalados (fuera de scope, pero relevante si `npx ng lint` se ejecuta en CI).
