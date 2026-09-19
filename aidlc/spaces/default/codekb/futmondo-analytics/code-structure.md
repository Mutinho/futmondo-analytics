# Estructura del Código — futmondo-analytics

## Organización de Paquetes/Módulos

Monorepo con dos aplicaciones desplegables y utilidades de soporte. El catálogo con
responsabilidades y dependencias está en `component-inventory.md`; aquí se describe la
organización física y los patrones de código.

```
futmondo-analytics/
├── backend/                    # Servicio web FastAPI (Python 3.12)
│   ├── app/
│   │   ├── main.py             # App FastAPI, AuthMiddleware, montaje de routers, /photos, /health
│   │   ├── api/v1/endpoints/   # Routers HTTP (market, reset_db, analytics, balances, matchdays,
│   │   │                       #   player_finances, sync, _helpers, ...)
│   │   ├── auth/               # JWT + sesión: routes.py, token_store.py, session_store.py
│   │   ├── core/               # config.py (entorno, JWT guard NFR1.1), constants.py
│   │   ├── services/           # Lógica de negocio + clientes externos (god-files, ver más abajo);
│   │   │                       #   data_sync_service.sync_prizes() = fórmula de premios
│   │   ├── stores/             # Repositorios de durabilidad (intent previo)
│   │   ├── security/           # Protección de credenciales
│   │   └── models/             # Modelos de dominio/datos (DTOs Pydantic; sin modelo de premios)
│   ├── scripts/                # Scripts one-shot (sync, migraciones, exportaciones) — no web
│   ├── tests/                  # pytest (test_db_admin_guard, test_jwt_startup,
│   │                           #   test_auth_characterization, test_finance_characterization,
│   │                           #   test_analytics_service)
│   ├── requirements.txt, pytest.ini, ruff.toml, fly.toml, Dockerfile, nixpacks.toml
├── angular-app/                # Frontend Angular 22 (PWA); ver detalle abajo
├── proxy/, angular-app/nginx*.conf   # Reverse proxy nginx (local y prod)
├── cron/                       # Config Fly.io del worker cron (sync; nunca emite JWT)
├── docker-compose.yml          # Orquestación local (SSL_VERIFY=0 aquí)
├── .nvmrc                      # Node 22.22.3 (SOLO en raíz; NO existe en angular-app/)
└── .github/workflows/          # ci.yml, fly-deploy.yml, daily-sync.yml, sofascore-sync.yml
```

### Estructura del frontend `angular-app/` (intent activo)

```
angular-app/
├── src/app/
│   ├── main.ts / app.config.ts / app.routes.ts   # bootstrapApplication, providers, rutas
│   ├── core/
│   │   ├── services/*.service.ts   # 11 clientes HTTP: analytics, assistant, auth, budget,
│   │   │                           #   championship, evolution, favorites, roster, stats, sync
│   │   ├── interceptors/auth.interceptor.ts       # Bearer + refresh en cola ante 401 (+ .spec.ts)
│   │   ├── guards/auth.guard.ts                    # Protección de rutas (SIN spec)
│   │   └── preloading/idle-preloading-strategy.ts  # Precarga por inactividad (+ .spec.ts)
│   ├── features/{market,finances,budget,calculator,analytics,evolution,statistics,...}/
│   │                                # Componentes standalone por pantalla (SIN spec)
│   └── shared/                      # UI/utilidades reutilizables (SIN spec)
├── angular.json                     # Builder @angular/build; architect.test.runner: vitest;
│                                    #   schematics con skipTests: true (deuda FR10.1)
├── package.json                     # name angular-app, v2.1.8, packageManager npm@11.12.1
├── tsconfig.json / tsconfig.app.json / tsconfig.spec.json  # spec: types ["vitest/globals"]
├── eslint.config.js (flat) / .prettierrc
├── ngsw-config.json / proxy.conf.json / Dockerfile / fly.toml
└── node_modules.old-1789382239/     # árbol residual (ruido de repo; no dependencia activa)
```

Estado de tests del frontend (detalle y evidencia en `code-quality-assessment.md`): SOLO
existen **2** specs sobre ~90 fuentes en `src/app/` —
`core/interceptors/auth.interceptor.spec.ts` y
`core/preloading/idle-preloading-strategy.spec.ts`. NO hay `vitest.config.*` ni proveedor de
cobertura instalado. NO quedan restos Karma/Jasmine (`karma.conf.js`/`src/test.ts` ausentes).

### Estructura de `.github/workflows/` (intent activo)

```
.github/workflows/
├── ci.yml            # PR → main, job "quality": gitleaks(bloq) + pytest --cov=app(bloq)
│                     #   + ruff/pip-audit(adv) + npm ci + ng test --watch=false(bloq)
│                     #   + ng lint/npm audit(adv). Node fijado a '22'.
├── fly-deploy.yml    # push → main + workflow_dispatch. job verify (gitleaks@v2 + pytest -q
│                     #   SIN --cov + npm ci + ng test --watch=false, bloqueantes) →
│                     #   deploy-backend → deploy-frontend → smoke-test /health (5 reintentos)
├── daily-sync.yml    # cron 04:30 UTC + manual: máquina Fly one-shot; sync completo; poll
│                     #   hasta "stopped" y verifica exit code
└── sofascore-sync.yml# cron 05:00 UTC + manual: reutiliza imagen cron; corre
                      #   scripts/sync_sofascore_local.py; destrucción garantizada (trap EXIT)
```

## Clasificación de Archivos

- **Punto de entrada / composición**: `backend/app/main.py`, `run.py`/`entrypoint.sh`;
  frontend `angular-app/src/app/main.ts` + `app.config.ts`.
- **Configuración**: `backend/app/core/config.py`, `constants.py`, `.env.example`,
  `fly.toml`, `docker-compose.yml`, `.nvmrc`; frontend `angular.json`, `tsconfig*.json`,
  `eslint.config.js`, `.prettierrc`, `ngsw-config.json`, `proxy.conf.json`.
- **Superficie HTTP (backend)**: `backend/app/api/v1/endpoints/*` (incl.
  `player_finances.py`, `balances.py`, `matchdays.py`, `analytics.py`),
  `backend/app/auth/routes.py`.
- **Cliente HTTP (frontend)**: `angular-app/src/app/core/services/*.service.ts` +
  `core/interceptors/auth.interceptor.ts`.
- **Lógica de premios (fórmula)**: `backend/app/services/data_sync_service.py::sync_prizes`
  (~líneas 1577-1885) — productor de la tabla `team_prizes`. Los routers de finanzas/saldos
  sólo leen/suman.
- **Persistencia**: `backend/app/stores/*` (capa nueva estrecha) y SQL crudo en
  `auth/token_store.py`, `_helpers.py`, `balances.py`, `analytics.py`,
  `routes._auto_detect_championships`.
- **Integración externa**: `services/futmondo_client.py`, `sofascore_client.py`,
  `photo_service.py`.
- **Tests**: `backend/tests/*.py`, `angular-app/**/*.spec.ts` (hoy sólo 2).
- **Entrega/CI**: `.github/workflows/*.yml`.
- **Datos estáticos (no código)**: `backend/static/photos/players/**` (~800 PNG).

## Patrones de Código Observados

### Backend

- **Middleware de autenticación global** con lista de exclusión (`AUTH_EXCLUDED_PATHS`) en
  vez de dependencias por endpoint; ver `api-documentation.md`.
- **Proxy a APIs externas** desde `services/`, con cliente por usuario resuelto en
  `_helpers.get_user_futmondo_client`.
- **Precálculo batch + lectura barata**: la fórmula de premios se ejecuta una vez en
  `sync_prizes` y persiste en `team_prizes`; los endpoints sólo hacen `SELECT`/suma. UPSERT
  con `ON CONFLICT (championship_id, team_id, matchday)` y limpieza defensiva
  `DELETE ... WHERE matchday NOT IN (...)`.
- **Matchday sintético negativo** para las pseudo-jornadas adelantadas de Futmondo (número
  no entero, p. ej. `0.5 -> -5`), evitando colisión con jornadas reales 1..38 en una columna
  entera.
- **Persistencia mixta**: capa `stores/` estrecha (patrón recomendado) conviviendo con SQL
  crudo disperso (anti-patrón a no ampliar; detalle en `code-quality-assessment.md`).
- **God-files en `services/`**: `data_manager_v2.py` (~166 KB), `data_sync_service.py`
  (~84 KB, aloja la fórmula de premios), `assistant_service.py` (~51 KB); no deben crecer.
- **Imports dinámicos dentro de funciones** (p. ej. `import requests` en `get_player_photo`);
  preferir import estático. **Idioma en el código**: identificadores/docstrings/comentarios
  en inglés; texto de usuario (`HTTPException.detail`) en castellano.

### Frontend (Angular 22)

- **Componentes standalone + signals**: sin `NgModule` de app; arranque por
  `bootstrapApplication` y providers en `app.config.ts`; rutas lazy con precarga por
  inactividad (`idle-preloading-strategy`).
- **Interceptor de auth transversal**: `auth.interceptor` añade Bearer, excluye `/auth/*`
  (usa `withCredentials`), encola peticiones y refresca ante 401, fuerza logout ante
  403/refresh fallido. Es el patrón de referencia de spec Vitest ya existente.
- **Servicios por dominio** en `core/services/*.service.ts` (un servicio por área de la API).
- **`skipTests: true` en TODOS los schematics de `angular.json`** (anti-patrón; el código
  nuevo nace sin spec — deuda FR10.1, detalle en `code-quality-assessment.md`).
- **Tests con Vitest**: los specs importan de `vitest` (`vi`, `describe`, `it`, `expect`) y
  usan `@angular/core/testing` + `@angular/common/http/testing`; `tsconfig.spec.json` incluye
  `types: ["vitest/globals"]`.

### Entrega / CI

- **Doble gate bloqueante** (`ci.yml` PR + `verify` en `fly-deploy.yml`) con `gitleaks`,
  `pytest` y `ng test` bloqueantes; `ruff`/ESLint/`pip-audit`/`npm audit` advisory
  (`continue-on-error`).
- **Crons de coste ~0**: máquinas Fly one-shot que se crean, ejecutan y destruyen
  (`trap cleanup EXIT` en `sofascore-sync.yml`).
