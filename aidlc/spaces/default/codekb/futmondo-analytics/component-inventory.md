# Component Inventory — futmondo-analytics

> Los encabezados de componente de este fichero son la fuente de verdad para el
> bloque `## Scope of Analysis` de `reverse-engineering-timestamp.md` (se comparan
> literalmente en el rerun guard).

## angular-app (frontend SPA/PWA)
- **Responsabilidad**: UI web multi-usuario (presupuesto, mercado, finanzas,
  analytics, asistente). Shell con `mat-sidenav` (12 items), rutas lazy con
  `authGuard`, PWA (service worker + manifest). `version: 2.2.0`.
- **Depende de**: backend (FastAPI) vía `/api/v1/*` + `/auth/*` (`HttpClient`),
  `@angular/material` + `@angular/cdk`, `chart.js`/`ng2-charts`.
- **Portabilidad a nativo**: servicios y modelos portables ~1:1; vistas
  (`features/*`, Material/DOM) no portables (reescritura con `@nativescript/angular`).

## calculator-component
- **Responsabilidad**: feature de cálculo (`features/calculator`) sobre las
  finanzas/premios expuestas por el backend.
- **Depende de**: `core/services/*` (budget/finanzas), backend.

## analytics-and-charts
- **Responsabilidad**: features `evolution` y `analytics`; gráficos con
  `chart.js` + `ng2-charts` sobre `<canvas>` (cargados lazy/`@defer`).
- **Depende de**: `core/services/analytics`, `evolution`, `stats`; DOM `<canvas>`
  → requiere plugin de charting nativo distinto en NativeScript.

## backend (FastAPI app)
- **Responsabilidad**: API monolítica; monta routers + `AuthMiddleware` en
  `main.py`. 59 operaciones de ruta. `version: 2.0.0`.
- **Depende de**: Neon PostgreSQL, clientes externos, auth, servicios de dominio.

## api-endpoints
- **Responsabilidad**: `app/api/v1/endpoints/` (22 ficheros) — capa HTTP; 17
  ejecutan SQL directo (SQL-en-router).
- **Depende de**: `db_connection`, servicios de dominio.

## data-manager
- **Responsabilidad**: gestión de datos del campeonato; `data_manager_v2.py`
  (facade) + paquete DDD `data_manager/<resp>/{domain,application,infrastructure}`.
- **Depende de**: `db_connection`, Neon.

## data-sync-service
- **Responsabilidad**: `data_sync_service.py` + `sync/*` + `task_service.py`;
  orquesta la sincronización asíncrona por pasos.
- **Depende de**: clientes externos, `data_manager`, Neon.

## analytics-and-assistant
- **Responsabilidad**: cálculo analytics (`analytics/application/calculations.py`)
  y asistente LLM (`assistant/` + `assistant_service.py` shim).
- **Depende de**: Neon, `llm_adapter` (Gemini/Groq).

## auth-and-security
- **Responsabilidad**: `app/auth/` (`routes.py`, `token_store.py`,
  `session_store.py`, `jwt_utils.py`, `dependencies.py`) + `AuthMiddleware`;
  JWT access/refresh, sesión Futmondo por usuario. Exige `JWT_SECRET` no-default.
- **Depende de**: API Futmondo, Neon.

## external-clients
- **Responsabilidad**: `futmondo_client.py` (API Futmondo), `sofascore_client.py`
  (API Sofascore vía `curl_cffi`), `llm_adapter.py` (Gemini/Groq).
- **Depende de**: APIs externas Futmondo / Sofascore / LLM.

## photo-service
- **Responsabilidad**: `photo_service.py` + `/api/v1/photos/{player_id}`; servir
  fotos de jugadores.
- **Depende de**: almacenamiento/fuente de fotos, Neon.

## proxy-nginx
- **Responsabilidad**: reverse proxy nginx local (`proxy/nginx.conf`), sólo
  `docker-compose`.
- **Depende de**: frontend y backend.

## cron-jobs
- **Responsabilidad**: app Fly.io one-shot `futmondo-cron` que ejecuta
  `scripts/sync_data.py` y sale; crons `daily-sync.yml` / `sofascore-sync.yml`.
  Comparte Dockerfile del backend.
- **Depende de**: backend (código/servicios), APIs externas, Neon.
