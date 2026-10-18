# Code Structure — futmondo-analytics

## Organización de alto nivel

```
futmondo-analytics/
├── angular-app/          # Frontend Angular 22 + Material 22 (PWA)
├── backend/              # Backend FastAPI (Python 3.12)
├── proxy/                # nginx reverse proxy (sólo local)
├── cron/                 # app Fly.io one-shot (futmondo-cron)
├── docs/                 # documentación (DEPLOY, ROLLBACK, PR-GATE, planes…)
├── .github/workflows/    # CI/CD (ci.yml, fly-deploy.yml, crons)
├── docker-compose.yml
└── .nvmrc                # Node 22.22.3
```

## Paquete `angular-app` (frontend)

- **Builder**: Angular CLI `@angular/build:application`; config en
  `angular.json`, `tsconfig*.json`; PWA en `ngsw-config.json` +
  `public/site.webmanifest`. `version: 2.2.0`.
- **Estructura `src/app/`**:
  - **shell**: `app.ts` / `app.html` / `app.routes.ts` / `app.config.ts` —
    layout con `<mat-sidenav>` + `<mat-nav-list>` (12 items), dark mode vía
    manipulación de `document.body`/`documentElement`, `provideServiceWorker`.
  - **`core/`**: `services/` (12 servicios `*.service.ts` sobre `HttpClient`),
    `interceptors/` (`authInterceptor`: inyecta Bearer, refresh en 401, logout
    en 403), `guards/` (`authGuard`), `preloading/`, `models/`.
  - **`features/`**: login, splash, evolution (Chart.js), market, calculator,
    analytics — vistas con plantillas `.html` + Material.
  - **`shared/components/`**: componentes reutilizables incl.
    `assistant-fab.component.ts`.
- **Clasificación**: fuente portable a nativo casi 1:1 → `core/services/*` y
  `core/models/*`; fuente NO portable → `features/*` y `shared/*` (DOM +
  Material + plantillas HTML). Ver riesgos en `code-quality-assessment.md`.

## Paquete `backend` (FastAPI)

- **Entrada**: `app/main.py` monta routers y el `AuthMiddleware`; `run.py`
  arranca uvicorn. `version: 2.0.0`.
- **`app/api/v1/endpoints/`**: 22 ficheros de endpoints (market, sync, analytics,
  user, photos, etc.). **17** ejecutan SQL directo (patrón SQL-en-router).
- **`app/services/`**: mezcla de god-files heredados y descomposiciones DDD:
  - God-files: `data_manager_v2.py`, `data_sync_service.py`, `photo_service.py`,
    `futmondo_client.py`, `sofascore_client.py` (ver tamaños medidos en
    `code-quality-assessment.md`).
  - DDD extraído: `data_manager/<resp>/{domain,application,infrastructure}`,
    `sync/*`, `analytics/`, `assistant/` (con
    `assistant/infrastructure/llm_adapter.py`). `assistant_service.py` es hoy un
    shim de 60 líneas que delega al paquete `assistant/`.
  - Infra: `db_connection.py` (incl. `adapt_params()` `? → %s`), `task_service.py`,
    `session_service.py`.
- **`app/auth/`**: `routes.py`, `token_store.py`, `session_store.py`,
  `jwt_utils.py`, `dependencies.py`.
- **`app/core/config.py`**: configuración (exige `JWT_SECRET` no-default).
- **`scripts/`**: scripts one-shot (`sync_data.py`,
  `fetch_user_finances_data.py`, …), usados por la app `cron`.
- **Tests**: `backend/tests/` (62 ficheros `test_*.py`, muchos de
  characterization). Ejecutados DESDE `backend/` (`pythonpath = .`), con fixtures
  fake in-memory en `conftest.py`.

## Patrones de código observados

- **Facade byte-for-byte**: al descomponer un god-file se mantiene su nombre y
  firmas, delegando al paquete DDD (migración sin romper llamadores).
- **SQL-en-router** (heredado, prohibido ampliar por reglas afirmadas).
- **Reescritura de placeholders** `? → %s` en runtime (`adapt_params()`),
  herencia del soporte multi-engine SQLite/Turso retirado — dead-ish code
  tolerado.
- **Clasificación de errores RECOVERABLE/FATAL** documentada en `main.py`,
  `db_connection.py`, `token_store.py`.
- **Convenciones de nombres**: snake_case Python, camelCase TS. Comentarios
  mezclados castellano + inglés.
