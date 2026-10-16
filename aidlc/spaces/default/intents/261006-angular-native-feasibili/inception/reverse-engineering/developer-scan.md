# Reverse Engineering — Developer Code Scan (pipeline link 1 de 2)

> Intent activo: `angular-native-feasibili` — análisis de VIABILIDAD de migrar
> Futmondo Analytics a app nativa con **Angular Native (NativeScript + Angular)**.
> Este documento es el handoff estructurado del DEVELOPER; el architect (link 2)
> lo sintetizará en los 9 artefactos del CodeKB. Proyecto BROWNFIELD, repo único,
> raíz = workspace root. Scan FULL RESCAN, profundidad STANDARD.

## Developer Code Scan Results

### Scan Coverage
- **Analyzed deeply**:
  - `./` (raíz: `README.md`, `docker-compose.yml`, `.nvmrc`, `.env.example`)
  - `angular-app/package.json`, `angular-app/angular.json`, `angular-app/ngsw-config.json`, `angular-app/public/site.webmanifest`, `angular-app/eslint.config.js`, `angular-app/fly.toml`
  - `angular-app/src/app/` (shell `app.ts`/`app.html`/`app.routes.ts`/`app.config.ts`; `core/services/`, `core/interceptors/`, `core/guards/`, `core/preloading/`, `core/models/`; `features/` — login, splash, evolution (Chart.js), market, calculator, analytics; `shared/components/` incl. `assistant-fab.component.ts`)
  - `backend/app/main.py` (registro de routers + middleware de auth)
  - `backend/app/api/v1/endpoints/` (22 ficheros de endpoints, muestreo profundo de market/sync/analytics/user/photos)
  - `backend/app/services/` (god-files `data_manager_v2.py`, `data_sync_service.py`, `assistant_service.py`, `photo_service.py`, `futmondo_client.py`, `sofascore_client.py`; descomposiciones DDD `data_manager/`, `sync/*`, `analytics/`, `assistant/`; `db_connection.py`, `task_service.py`, `session_service.py`)
  - `backend/app/auth/` (`routes.py`, `token_store.py`, `session_store.py`, `jwt_utils.py`, `dependencies.py`), `backend/app/core/config.py`
  - `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`, `backend/fly.toml`, `backend/.pip-audit-allowlist`
  - `.github/workflows/` (`ci.yml`, `fly-deploy.yml`; `daily-sync.yml`/`sofascore-sync.yml` a nivel de propósito), `cron/fly.toml`
- **Skimmed only**:
  - `backend/tests/` y `angular-app/src/**/*.spec.ts` (inventariados por conteo y nombre; no leídos test a test)
  - `backend/scripts/` (scripts one-shot: `sync_data.py`, `fetch_user_finances_data.py`, etc. — identificados por nombre/tamaño)
  - `backend/app/services/photo_service.py` (leído parcialmente; tamaño y rol confirmados)
  - `docs/` (identificados por nombre; `README.md` leído a fondo)
  - `angular-app/node_modules.old-*` (ignorado: artefacto obsoleto, no fuente)
  - `proxy/nginx.conf`, `angular-app/nginx*.conf`, Dockerfiles (identificados por rol; no desgranados línea a línea)

### Packages Found
- `angular-app` — frontend SPA/PWA — TypeScript/Angular 22 — UI web multi-usuario (presupuesto, mercado, finanzas, analytics, asistente IA). `version: 2.2.0`.
- `backend` — API web — Python 3.12/FastAPI — autenticación JWON, sync con Futmondo/Sofascore, cálculo de premios/finanzas, servir fotos. `version: 2.0.0`.
- `proxy` — nginx reverse proxy local (solo docker-compose).
- `cron` — app Fly.io one-shot (`futmondo-cron`) que ejecuta `scripts/sync_data.py` y sale; comparte Dockerfile del backend.
- NO hay monorepo tooling (no workspaces npm, no Nx); dos builds independientes acoplados por contrato HTTP `/api/v1/*` + `/auth/*`.

### Build System
- **Type**: npm (frontend, Angular CLI builder `@angular/build:application`) + pip/`requirements.txt` (backend); Docker para empaquetado; Fly.io para deploy.
- **Config Files**: `angular-app/package.json` (`packageManager: npm@11.12.1`), `angular-app/angular.json`, `angular-app/tsconfig*.json`, `.nvmrc` (`22.22.3`); `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`, `backend/run.py`; `docker-compose.yml`; `backend/fly.toml`, `angular-app/fly.toml`, `cron/fly.toml`; `.github/workflows/*.yml`.
- **Build Dependencies**: frontend `npm ci` → `ng build` (budgets: initial warn 900kB/error 1MB; serviceWorker `ngsw-config.json` en producción). backend `pip install -r requirements.txt` → `uvicorn`. Acople de deploy (cadena `needs:` en `fly-deploy.yml`): `verify` → `deploy-backend` → `deploy-frontend` → `smoke-test` (`/health`).

### APIs Discovered
- **REST interna (FastAPI)** — `backend/app/api/v1/endpoints/` (22 ficheros de endpoints) + `backend/app/auth/routes.py` — **59 operaciones** de ruta: 38 `@router.get`, 18 `@router.post`, 2 `@router.delete`, 1 `@router.put`. Prefijos montados en `main.py`: `/api/v1/{matchdays,initialize,database,statistics,player-finances,user-stats,clausulable-players,sync,analytics,market,roster,favorites,transactions,sofascore,user,assistant}` + `/api/v1` (championships, phantoms) y `/api/v1/photos/{player_id}`.
- **Auth (sin prefijo `/api/v1`)** — `/auth/login`, `/auth/refresh`, `/auth/logout`. JWT access (1h, en memoria del navegador) + refresh token (30d, cookie HttpOnly). `AuthMiddleware` (Starlette `BaseHTTPMiddleware`) exige Bearer en todo `/api/v1/*` salvo `AUTH_EXCLUDED_PATHS` (`/health`, `/`, `/docs`, `/openapi.json`, `/redoc`, rutas `/auth/*`).
- **Externas consumidas** — API Futmondo (`backend/app/services/futmondo_client.py`, 720 líneas), API Sofascore (`backend/app/services/sofascore_client.py`, 392 líneas, vía `curl_cffi`), LLM Gemini (`google-genai`) + Groq fallback (`backend/app/services/assistant/infrastructure/llm_adapter.py`).
- **Cliente Angular → API** — 12 servicios en `core/services/*.service.ts` (`auth`, `analytics`, `budget`, `stats`, `evolution`, `roster`, `favorites`, `sync`, `assistant`, `championship`) usando `HttpClient`. `authInterceptor` inyecta `Bearer`, maneja refresh en 401 (cola con `BehaviorSubject`) y fuerza logout en 403. Health público: `/health` (HTTP 200).

### Frameworks & Libraries
- **Frontend** (versiones de `package.json`, rangos `^`/`~`):
  - `@angular/{core,common,router,forms,animations,compiler,platform-browser,service-worker}` `^22.2.1`; `@angular/cdk` + `@angular/material` `^22.2.1`.
  - `chart.js` `^4.5.1` + `ng2-charts` `^10.0.0` (cargados lazy por ruta/`@defer`).
  - `marked` `^18.0.11` (markdown del asistente, diferido). `rxjs` `~7.8.0`, `tslib` `^2.3.0`.
  - devDeps: `@angular/build` + `@angular/cli` `^22.2.0`, `typescript` `~6.0.2`, `vitest` **`4.1.11`** (pin exacto) + `@vitest/coverage-v8` **`4.1.11`**, `jsdom` `^25.0.1`, `prettier` `^3.8.1`. Node fijado en `.nvmrc` = `22.22.3`.
- **Backend** (versiones EXACTAS de `requirements.txt`): `fastapi==0.141.1`, `uvicorn[standard]==0.54.0`, `pydantic==2.13.5`, `requests==2.34.2`, `python-dotenv==1.2.3`, `python-multipart==0.0.32`, `psycopg2-binary==2.9.13`, `curl_cffi==0.16.3`, `PyJWT==2.15.0`, `google-genai==1.14.0`, `groq==0.25.0`; test: `pytest==9.1.1`, `pytest-cov==7.1.0`, `httpx==0.28.1`.

### Test Coverage
- **Test Directories**: `backend/tests/` (**62** ficheros `test_*.py`, muchos de characterization: `test_sync_*`, `test_data_manager_*`, `test_prizes_*`, `test_assistant_*`, `test_durable_*`, `test_auth_*`, `test_jwt_startup.py`). Frontend: **15** `*.spec.ts` colocados junto a sus fuentes en `src/app/core/**` y `src/app/features/**`.
- **Test Frameworks**: backend `pytest` + `pytest-cov` (ejecutado DESDE `backend/`, `pythonpath = .`; fixtures fake in-memory en `conftest.py`). Frontend `ng test` builder `@angular/build:unit-test` con runner **Vitest** + `@vitest/coverage-v8`, entorno `jsdom`.
- **Coverage Config**: PRESENTE y BLOQUEANTE en ambos. Backend: `pytest.ini` `addopts = -ra --cov-fail-under=27` (line-only, requiere `--cov=app` que pasan `ci.yml` y `verify`; piso real medido 27.52% → 27, ratchet solo sube). Frontend: `angular.json` target `test` `coverageThresholds` statements 19 / branches 19 / functions 17 / lines 18 (fuente única de umbral, enforcement dentro de `ng test`).

### Code Quality Indicators
- **Linting**: backend **ruff** (`backend/ruff.toml`, `target-version = py312`, `line-length = 100`, `select = ["E","F","I"]`, `ignore = ["E501","E402"]`; `[lint.per-file-ignores]` registra la deuda de los god-files y los adapters DDD extraídos verbatim — p.ej. `data_manager_v2.py` → `E722,F841,F401,I001`). `ruff check` es BLOQUEANTE en ambos gates; `ruff format` NUNCA se corre en masa (regla afirmada). Frontend **ESLint** flat config (`eslint.config.js`) pero sus devDependencies NO están instaladas → `ci.yml` corre `npx ng lint || echo …` en modo advisory (deuda diferida).
- **CI/CD**: `.github/workflows/ci.yml` (gate de PR, job `quality`: gitleaks + ruff + pytest+cov + pip-audit + ng test + npm audit), `fly-deploy.yml` (push a `main`: job `verify` replica el gate → deploy backend → frontend → smoke `/health`), `daily-sync.yml` y `sofascore-sync.yml` (crons que lanzan máquinas Fly one-shot). gitleaks unificado a `@v3` en ambos. Secretos vía GitHub Actions / Fly.io; `JWT_SECRET` efímero no-productivo en CI.
- **Documentation**: `README.md` raíz exhaustivo (arquitectura, stack, endpoints, auth, PWA). `docs/` extenso (DEPLOY, ROLLBACK, PR-GATE, PROJECT_CONTEXT, varios BACKLOG, V2_MIGRATION_PLAN, FRONTEND_IMPROVEMENTS_PLAN, SDD_ANGULAR_MIGRATION, MOCKUPS_NAVIGATION). Docstrings backend ricos (comentan clasificación de errores FR3.2 y notas de seguridad). Comentarios en castellano + inglés mezclados.

### Technical Debt Signals
- **God-files backend (tamaños reales medidos)**:
  - `app/services/analytics/application/calculations.py` — **872 líneas / 36.028 bytes** (el mayor por tamaño; lógica de cálculo analytics).
  - `app/services/futmondo_client.py` — **720 líneas / 27.267 bytes**.
  - `app/services/data_manager_v2.py` — **685 líneas / 33.368 bytes** (YA descompuesto parcialmente a `data_manager/<resp>/{domain,application,infrastructure}` DDD por intent previo 261005; la facade mantiene nombres/firmas byte-for-byte y delega; su deuda `E722,F841` queda registrada en `per-file-ignores`). NOTA: la memoria del proyecto lo cita como «~166 KB»; el valor ACTUAL en disco es 33 KB tras la descomposición.
  - `app/api/v1/endpoints/market.py` — **580 líneas / 24.560 bytes** (SQL-en-router).
  - `app/services/photo_service.py` — **492 líneas / 22.764 bytes** (`E722` registrado como deuda).
  - `app/services/sofascore_client.py` — **392 líneas**, `app/services/data_sync_service.py` — **362 líneas / 15.397 bytes**, `app/api/v1/endpoints/sync.py` — **407 líneas / 16.864 bytes**.
  - `assistant_service.py` ahora es solo **60 líneas / 2.290 bytes** (shim; la lógica real está en el paquete DDD `assistant/`). La memoria lo cita «~51 KB» — desactualizado.
- **SQL-en-router**: **17** ficheros de `api/v1/endpoints/` ejecutan SQL directo (`.execute(`) — acoplamiento persistencia↔HTTP; patrón heredado que las reglas afirmadas prohíben ampliar.
- **Patrón `? → %s`**: `db_connection.adapt_params()` reescribe placeholders en runtime (herencia del soporte multi-engine SQLite/Turso ya retirado; `DATABASE_PATH` y ramas `db_type != postgres` son dead-ish code tolerado).
- **Manejo de errores**: endurecido recientemente (clasificación RECOVERABLE/FATAL documentada en `main.py`, `db_connection.py`, `token_store.py`); los `except:` amplios de los god-files quedan como deuda registrada, no en alcance.
- **Acoplamiento frontend ↔ APIs de navegador/PWA** (relevante para la viabilidad NativeScript): `localStorage` usado en **17** ficheros (sesión de usuario, tema, `futmondo_last_route`, `futmondo_sync_task_id` de reconexión del sync); `window.` en 2, `document.` en 2 (`app.ts` manipula `document.body`/`documentElement` para dark mode), `navigator.` en 0. Service worker en 1 sitio (`app.config.ts` `provideServiceWorker`). **Material** (`@angular/material`, 25 módulos distintos; top: progress-spinner 27, button 23, icon 21, table 17, form-field 16, dialog 14) y **CDK layout** (`BreakpointObserver`) son DOM-dependientes → no portan a NativeScript (que usa `@nativescript/angular` + widgets nativos, no DOM ni Material). `routerLink`/`RouterOutlet` del router web también difieren del `nativescript-angular` routing.

## Handoff Summary
- **Intent-relevant finding**: La navegación actual es un **`mat-sidenav` lateral** (no una barra inferior): `app.html` define `<mat-sidenav>` con `<mat-nav-list>` de **12 items** (`app.ts` `allNavItems`: Presupuesto, Mi Plantilla, Calculadora, Mercado, Favoritos, Agentes Libres, Transacciones, Evolución, Estadísticas, Clausulables, Clasificación, Ajustes) + acciones Sincronizar/Modo oscuro/Cerrar sesión; en móvil se abre con un `MatToolbar` + botón `menu` (`isMobile()` vía `BreakpointObserver`). NO existe hoy ningún bottom-nav ni concepto de «4 opciones más usadas», así que el menú inferior iOS 'liquid glass' con 4 opciones del intent es construcción NUEVA de UI nativa, no una adaptación de un patrón existente. NO hay ninguna superficie de widget (iOS/Android) en el código — confirmado: 0 referencias a widgets; es greenfield nativo. La lógica de dominio reutilizable vive en el **backend FastAPI intacto** (la app nativa consumiría el mismo contrato `/api/v1/*` + `/auth/*`, 59 operaciones), por lo que la migración es esencialmente un **reemplazo de la capa de presentación** (Angular web/Material/PWA → NativeScript + Angular), no un rewrite del backend. Evidencia: `app.html` (sidenav), `app.routes.ts` (14 rutas lazy con `authGuard`), `app.ts:allNavItems`.
- **Risks / follow-up** (el architect debe preservar):
  1. **Acoplamiento web-DOM alto en la capa de UI**: todo `features/*` usa Angular **Material + CDK** (DOM) y plantillas HTML (`.html`) con `@angular/material/*`; NativeScript NO soporta Material ni DOM → **toda la capa de vista se reescribe** con widgets nativos (`@nativescript/angular`). Los **servicios** (`core/services/*.service.ts`, RxJS/`HttpClient`, signals) y los **modelos** (`core/models/*`) son portables casi 1:1; los **componentes** no.
  2. **PWA / service worker / `localStorage`**: `ngsw-config.json` + `provideServiceWorker` + 17 usos de `localStorage` (sesión, tema, reconexión de sync) → en nativo se sustituyen por `@nativescript/core` ApplicationSettings / SecureStorage; el **access token en memoria + refresh en cookie HttpOnly** (`auth.service.ts`, `auth.interceptor.ts`) depende de cookies del navegador y `withCredentials` → **el modelo de sesión cookie-based NO existe igual en nativo** y es el riesgo de portabilidad #1 (habrá que mover el refresh token a almacenamiento seguro nativo).
  3. **Chart.js/ng2-charts** (Evolución, Analytics): dependen de `<canvas>` DOM; en NativeScript requieren un plugin de charting nativo distinto (reescritura de los gráficos).
  4. **Discrepancia de tamaños god-file vs memoria del proyecto**: `data_manager_v2.py` es hoy 33 KB (no ~166 KB) y `assistant_service.py` 2 KB (no ~51 KB) tras descomposiciones DDD de intents 261005/261003; el architect debe usar las cifras MEDIDAS de este scan, no las de `project.md`. Sigue siendo backend fuera del alcance de un intent de viabilidad de UI nativa.
  5. **Restricción coste 0 € y stack Fly.io/Neon**: la viabilidad debe respetar que el backend/deploy no cambian; Angular Native/NativeScript es OSS, pero la distribución a iPhone 13 Pro / Samsung A17 implica build nativo (Xcode/Android SDK) y potencialmente coste de cuenta de desarrollador Apple — a señalar en feasibility, no resuelto aquí.
