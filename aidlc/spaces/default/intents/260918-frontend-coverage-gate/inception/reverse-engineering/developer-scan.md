## Developer Code Scan Results

> Scan enfocado (link 1 de 2 — DEVELOPER) para el intent `frontend-coverage-gate`
> (scope `classic`, BROWNFIELD). No es un rescan completo: el store CodeKB vigente
> ya cubre en profundidad el área backend de premios/finanzas. Este scan se centra
> en el frontend Angular (`angular-app/`) y el pipeline CI/CD (`.github/workflows/`),
> que el store cubre solo superficialmente o no cubre. El backend se recorre a nivel
> estructural para que el architect pueda preservar/fusionar.

### Scan Coverage
- **Analyzed deeply**:
  - `angular-app/` (configuración de test/cobertura y estructura de la app; ver detalle abajo)
  - `.github/workflows/` (los cuatro workflows: `ci.yml`, `fly-deploy.yml`, `daily-sync.yml`, `sofascore-sync.yml`)
- **Skimmed only**:
  - `backend/app/api/v1/endpoints/player_finances.py`
  - `backend/app/api/v1/endpoints/matchdays.py`
  - `backend/app/api/v1/endpoints/analytics.py`
  - `backend/app/api/v1/endpoints/balances.py`
  - `backend/app/services/analytics_service.py`
  - `backend/app/models/models.py`
  - `backend/tests/test_analytics_service.py`
  - `backend/tests/test_finance_characterization.py`
  - `backend/` (layout general, `pytest.ini`, `conftest.py`, `ruff.toml`, `requirements.txt`)
  - `proxy/`, `docker-compose.yml`, configs de raíz (`.nvmrc`)

### Packages Found
- `angular-app` — frontend/application — TypeScript/Angular 22 — SPA/PWA (presupuesto, mercado, sync, finanzas, analytics, evolución, estadísticas). `package.json` name `angular-app`, version `2.1.8`, `packageManager: npm@11.12.1`.
- `backend` (app FastAPI) — service/API — Python 3.12 — API REST `/api/v1/*` + `/auth/*` + `/health`; ingesta/sync desde API Futmondo y Sofascore; cálculo de finanzas/premios. (Estructura solo; internals de premios ya en el store.)
- `proxy` — infra — nginx — reverse proxy local (`proxy/nginx.conf`).
- `cron` — infra/batch — Fly one-shot — imagen de sync reutilizada por `daily-sync.yml` y `sofascore-sync.yml`.

### Build System
- **Type**: frontend → Angular CLI (`@angular/cli` ^22.1.2) sobre el builder `@angular/build` ^22.1.2 (esbuild/vite); backend → Python/pip (`pytest`); orquestación local → Docker Compose.
- **Config Files**:
  - Frontend: `angular-app/angular.json`, `angular-app/package.json`, `angular-app/tsconfig.json`, `angular-app/tsconfig.app.json`, `angular-app/tsconfig.spec.json`, `angular-app/eslint.config.js`, `angular-app/.prettierrc`, `angular-app/ngsw-config.json`, `angular-app/proxy.conf.json`, `angular-app/Dockerfile`, `angular-app/fly.toml`.
  - Raíz: `.nvmrc` = `22.22.3` (NO existe `.nvmrc` dentro de `angular-app/`; solo el de raíz).
  - Backend: `backend/pytest.ini`, `backend/conftest.py`, `backend/ruff.toml`, `backend/requirements.txt`.
  - Infra: `docker-compose.yml`, `proxy/nginx.conf`.
- **Build Dependencies**: frontend `ng build`/`ng test` → `@angular/build:application` (build target `development` es el `buildTarget` que consume el test builder). `docker-compose` → `proxy` depende de `backend` (healthy) y `frontend`; `frontend` depende de `backend` (healthy).

### APIs Discovered
- REST HTTP (backend, skim) — `backend/app/api/v1/endpoints/` — ~22 módulos de endpoints (`analytics`, `balances`, `matchdays`, `player_finances`, `market`, `sync`, `championships`, `user`, `statistics`, `transactions`, `roster`, `favorites`, `clausulable_players`, `phantoms`, `sofascore_detail`, `sofascore_sync`, `assistant`, etc.) + `/auth/*` y `/health`.
- Cliente HTTP frontend — `angular-app/src/app/core/services/*.service.ts` (11 servicios: `analytics`, `assistant`, `auth`, `budget`, `championship`, `evolution`, `favorites`, `roster`, `stats`, `sync`) + `core/interceptors/auth.interceptor.ts` (Bearer + refresh en cola ante 401, `withCredentials` para `/auth/*`).

### Frameworks & Libraries
Frontend (`angular-app/package.json`):
- `@angular/*` (animations, cdk, common, compiler, core, forms, material, platform-browser, router, service-worker) — `^22.1.0` — framework + Material + PWA (service worker).
- `chart.js` — `^4.5.1` y `ng2-charts` — `^10.0.0` — gráficos.
- `marked` — `^18.0.11` — render Markdown (asistente).
- `rxjs` — `~7.8.0`; `tslib` — `^2.3.0`.
- devDependencies: `@angular/build` — `^22.1.2`, `@angular/cli` — `^22.1.2`, `@angular/compiler-cli` — `^22.1.0`, `vitest` — `^4.0.8`, `jsdom` — `^25.0.1`, `typescript` — `~6.0.2`, `prettier` — `^3.8.1`.
- **NOTA CRÍTICA para el intent**: NO hay `@vitest/coverage-v8` (ni `istanbul`) en devDependencies — la cobertura no es medible hoy con el toolchain instalado.
- ESLint flat config referencia `angular-eslint`, `typescript-eslint`, `@eslint/js`, pero esos paquetes NO están en devDependencies (se añadirán al pasar el lint a bloqueante — ver `eslint.config.js` y R-05).

Backend (skim, `backend/requirements.txt`): `fastapi>=0.104.0`, `uvicorn[standard]`, `pydantic>=2.5.0`, `PyJWT==2.9.0`, `psycopg2-binary`, `curl_cffi`, `requests`, `google-genai`, `groq`; testing `pytest>=8.0.0`, `pytest-cov>=5.0.0`, `httpx>=0.27.0`.

### Test Coverage
- **Test Directories**:
  - Frontend: tests co-localizados (`*.spec.ts` junto al fuente). SOLO existen **2** specs sobre ~90 archivos fuente en `src/app/`:
    - `src/app/core/interceptors/auth.interceptor.spec.ts` (caracterización del interceptor: Bearer, exclusión `/auth/*`, `withCredentials`, refresh en cola ante 401, logout ante 403/refresh-fallido).
    - `src/app/core/preloading/idle-preloading-strategy.spec.ts` (lógica pura de precarga por inactividad con fake timers).
  - NO hay specs de servicios (`core/services/*`), del guard `core/guards/auth.guard.ts`, ni de componentes `features/*` / `shared/*`.
  - Backend (skim): `backend/tests/` con ~20 tests, incluidos varios `*_characterization.py` (`test_finance_characterization.py`, `test_prizes_characterization.py`, `test_analytics_service.py`, etc.).
- **Test Frameworks**:
  - Frontend: **Vitest** (`^4.0.8`) con `jsdom` (`^25.0.1`), ejecutado por el builder `@angular/build:unit-test` (`angular.json` → `architect.test`: `runner: vitest`, `tsConfig: tsconfig.spec.json`, `buildTarget: angular-app:build:development`). Los specs importan de `vitest` (`vi`, `describe`, `it`, `expect`) y usan `@angular/core/testing` + `@angular/common/http/testing`. `tsconfig.spec.json` incluye `types: ["vitest/globals"]` e `include: src/**/*.spec.ts`. NO quedan restos Karma/Jasmine (no hay `karma.conf.js` ni `src/test.ts`).
  - Backend: `pytest` (`pytest.ini`: `testpaths = tests`, `pythonpath = .`; ejecutado DESDE `backend/`) + `pytest-cov`.
- **Coverage Config**: **absent** (frontend). NO existe `vitest.config.*` en `angular-app/`; `angular.json` no declara opciones de `coverage`; no hay proveedor (`v8`/`istanbul`) instalado ni thresholds. `ng test` hoy ejecuta specs pero NO reporta ni exige cobertura. (Backend: `pytest.ini` documenta cobertura como métrica informativa, sin `fail_under`/piso bloqueante — coherente con `team.md`.)

### Code Quality Indicators
- **Linting**:
  - Frontend: `eslint.config.js` (flat config, Angular) en modo **advisory** (arranca tolerante; degrada reglas a `warn`). CI lo corre con `continue-on-error: true` (`npx ng lint || echo ...`). Dependencias de ESLint aún no instaladas.
  - Backend: `ruff` (`ruff.toml`: `select = ["E","F","I"]`, `ignore = ["E501","E402","E722"]`, `line-length = 100`, format comillas dobles) en modo **advisory** en CI (`continue-on-error`). Prettier `^3.8.1` disponible en el frontend.
- **CI/CD** (`.github/workflows/`):
  - `ci.yml` (**PR → `main`**, job `quality`): orden = gitleaks (BLOQUEANTE) → setup Python 3.12 + install → `ruff check` (advisory) → `pytest tests -q --cov=app --cov-report=term-missing` (BLOQUEANTE, CON cobertura) → `pip-audit` (advisory) → setup Node 22 + `npm ci` → `ng lint` (advisory) → **`ng test --watch=false` (BLOQUEANTE)** → `npm audit` (advisory).
  - `fly-deploy.yml` (**push → `main`**, `workflow_dispatch`): job `verify` = gitleaks@v2 (BLOQUEANTE) → `pytest tests -q` (BLOQUEANTE, SIN `--cov`) → setup Node 22 + `npm ci` → **`ng test --watch=false` (BLOQUEANTE)**. Deploys `deploy-backend` → `deploy-frontend` (Fly.io, `needs:` en cadena) → `smoke-test` contra `/health` (5 reintentos, HTTP 200).
  - `daily-sync.yml` (cron 04:30 UTC + manual): despliega imagen cron y ejecuta el sync completo en máquina Fly one-shot; poll hasta `stopped`, verifica exit code.
  - `sofascore-sync.yml` (cron 05:00 UTC + manual): reutiliza la imagen cron, lanza one-shot que corre `scripts/sync_sofascore_local.py`, la destruye siempre (`trap cleanup EXIT`).
  - Node en CI fijado a `'22'` (alineado con `.nvmrc` de raíz = `22.22.3`).
- **Documentation**: `README.md` (raíz y `angular-app/`), `docs/` (incluye `docs/BACKLOG-cobertura-frontend-y-pipeline.md`, `docs/DEPLOY.md`, `docs/ROLLBACK.md`), `AGENTS.md`. Los specs existentes llevan docstrings de caracterización con trazas a FR/BR.

### Technical Debt Signals
- **`skipTests: true` global en `angular.json`** — aplicado a TODOS los schematics (`component`, `class`, `directive`, `guard`, `interceptor`, `pipe`, `resolver`, `service`). Los componentes/servicios/guards nuevos NACEN sin spec. Diana directa de **FR10.1**.
- **Sin infraestructura de cobertura en el frontend** — no hay `vitest.config.*`, ni proveedor de cobertura instalado, ni `coverage.thresholds`. `ng test` no mide cobertura. Diana directa de **FR10.2** (requiere añadir `@vitest/coverage-v8` como devDependency — cambio de `package.json`/lock que debe verificarse contra el gate `npm ci`).
- **Cobertura de specs casi nula** — 2 specs / ~90 fuentes. Servicios core (`auth`, `budget`, `sync`, `analytics`…), el `auth.guard.ts` y los componentes de `features/` sin tests. El intent debe sembrar specs de servicios/guards/interceptores críticos primero.
- **`verify` de `fly-deploy.yml` YA corre `ng test --watch=false` (bloqueante)** — matiz importante para **FR17.1**: NO es que el frontend no se pruebe en el camino push→`main`; el hueco es que esos tests hoy no imponen cobertura (no hay threshold que rompa). Además `verify` corre `pytest` **sin `--cov`** mientras `ci.yml` sí mide `--cov=app` (paridad de cobertura diferida por decisión de pipeline — Q5=A en `team.md`, deuda registrada, NO seguridad: gitleaks es bloqueante en ambos caminos).
- **Dependencias de ESLint declaradas pero no instaladas** — `eslint.config.js` importa `angular-eslint`/`typescript-eslint`/`@eslint/js` que no están en devDependencies; el lint solo funciona en advisory best-effort. Fuera del alcance de cobertura, pero afecta la superficie del gate.
- **Directorio residual** `angular-app/node_modules.old-1789382239/` — árbol `node_modules` antiguo dejado en disco (no es dependencia activa; ruido de repo, no afecta build con `npm ci`).

## Handoff Summary
- **Intent-relevant finding**: El frontend usa Angular 22 + Vitest vía `@angular/build:unit-test` (`angular.json` → `architect.test.runner: vitest`) pero (1) tiene `skipTests: true` en TODOS los schematics de `angular.json` (bloquea que nuevo código nazca con spec — FR10.1) y (2) carece por completo de infraestructura de cobertura: NO hay `vitest.config.*`, NO hay proveedor de cobertura instalado (`@vitest/coverage-v8`/istanbul ausente en `package.json` devDependencies) y NO hay `coverage.thresholds`; hoy solo existen 2 specs (`auth.interceptor.spec.ts`, `idle-preloading-strategy.spec.ts`) sobre ~90 fuentes en `src/app/` (FR10.2). El gate `ng test --watch=false` es bloqueante tanto en `ci.yml` (PR→`main`) como en el job `verify` de `fly-deploy.yml` (push→`main`), así que activar un threshold de cobertura se propaga a AMBOS caminos automáticamente; el hueco de **FR17.1** es de MEANINGFULNESS de los tests de `verify` (cobertura), no de ausencia de ejecución.
- **Risks / follow-up**:
  - FR10.2 exige añadir `@vitest/coverage-v8` a devDependencies → cambia `package.json`/`package-lock.json`; hay que verificar `npm ci` + `ng test` en local/contenedor `node:22.22.3` antes de pushear (mandato afirmado en `project.md` para no romper el gate de CI). Coste 0 € (paquete OSS).
  - El threshold inicial debe ser bajo-y-trinquete (ratcheting): el estado base es ~2 specs, un piso alto rompería el gate bloqueante de inmediato.
  - Sembrar specs de servicios/guard/interceptores críticos ANTES de subir el threshold; `auth.interceptor.spec.ts` e `idle-preloading-strategy.spec.ts` ya fijan el patrón Vitest + `@angular/*/testing`.
  - Orden FR10 → FR17.1: primero cobertura en frontend (`ci.yml`), luego endurecer `verify` en `fly-deploy.yml`.
  - `.nvmrc` (22.22.3) vive SOLO en la raíz, no en `angular-app/`; CI usa `node-version: '22'`.
  - Deuda de paridad de pipeline preexistente (Q5=A): `verify` corre `pytest` sin `--cov`; queda fuera de alcance de este intent (decisión de calidad/pipeline diferida, no seguridad).
  - El store CodeKB backend ya cubre premios/finanzas; el architect debe MERGE (no reemplazar) al sintetizar, sumando `angular-app/` y `.github/workflows/` a `analyzed.paths`/`analyzed.components` y demoteando lo que proceda según la política de scope-diff.
