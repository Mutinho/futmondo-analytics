# Inventario de Componentes — futmondo-analytics

## Componentes del Backend (`backend/app`)

Lista completa de componentes con responsabilidades y dependencias. Los contratos HTTP
están en `api-documentation.md`; los patrones y ubicaciones en `code-structure.md`.

### backend-app-main
- **Ubicación**: `backend/app/main.py`
- **Responsabilidad**: composición de la app FastAPI, `AuthMiddleware` +
  `AUTH_EXCLUDED_PATHS`, montaje de todos los routers, endpoint `GET /api/v1/photos/{player_id}`
  (FR7) y `/health`.
- **Depende de**: `backend-app-auth` (verificación de token), `backend-app-api-endpoints`
  (routers), `backend-app-core` (config/constantes).

### backend-app-auth
- **Ubicación**: `backend/app/auth/` (`routes.py`, `token_store.py`, `session_store.py`)
- **Responsabilidad**: login/refresh/logout, emisión y verificación de JWT, cache en memoria
  de sesiones (sin password en claro) y persistencia/validación de refresh tokens.
  Contiene el bug FR9 en `token_store.is_refresh_token_valid` (precedencia naive/aware).
- **Depende de**: Neon PostgreSQL (SQL crudo directo), `backend-app-services` (cliente
  Futmondo para login), `backend-app-core`.

### backend-app-api-endpoints
- **Ubicación**: `backend/app/api/v1/endpoints/` (`market.py`, `reset_db.py`, `_helpers.py`,
  `player_finances.py`, `balances.py`, `matchdays.py`, `analytics.py`, `sync`, `roster`, ...)
- **Responsabilidad**: routers HTTP de la API v1.
  - **Área de premios/finanzas**: `player_finances.get_player_finances`
    (agrega finanzas por usuario leyendo `team_prizes` vía `dm.get_prizes_by_team`);
    `balances.get_balances` y `balances/prizes/{team_id}` (suman/desglosan premios por
    jornada, con SQL crudo); `matchdays` (equipos/rondas/evolución, DB-first); `analytics`
    (~12 endpoints derivados, `classification-full` y `watchlist` con SQL inline). **Ninguno
    recalcula premios**: sólo leen/suman `team_prizes`.
  - **Área de seguridad**: `market.place_bid` (FR6, sin validación de `price`); `reset_db`
    con guarda `_require_db_admin`/`ENABLE_DB_ADMIN` (FR18);
    `_helpers.get_user_futmondo_client`/`get_championship_config` (resolución de cliente y
    config por usuario, con SQL crudo).
- **Depende de**: `backend-app-auth`, `backend-app-services`, `backend-app-stores`.

### backend-app-core
- **Ubicación**: `backend/app/core/` (`config.py`, `constants.py`)
- **Responsabilidad**: resolución de entorno (`DATABASE_TYPE`, `FUTMONDO_CRED_KEY`), guard
  `resolve_jwt_secret`/`is_cron_worker` (NFR1.1), constantes. Punto de aterrizaje esperado
  para aislar `SSL_VERIFY` (FR8).
- **Depende de**: variables de entorno / `.env`.

### backend-app-services
- **Ubicación**: `backend/app/services/` (`futmondo_client.py`, `sofascore_client.py`,
  `photo_service.py`, `data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB,
  `assistant_service.py`, `analytics_service.py`)
- **Responsabilidad**: lógica de negocio y clientes de APIs externas (Futmondo, Sofascore).
  - **Productor de premios (fórmula)**: `data_sync_service.sync_prizes()`
    (~1577-1885) calcula todos los términos por (equipo, jornada) —points_prize,
    ranking_prize (modo flop/top sobre miembros activos), mvp_prize, dream_team_prize— con
    gating `award_round_prizes = is_closed AND round_fully_played AND NOT pseudo-ronda`, y
    UPSERTea `team_prizes` (única fuente de verdad) con limpieza defensiva `DELETE ... NOT IN`.
    Depende fuertemente de la API de Futmondo con `time.sleep()`.
  - **Analítica derivada**: `analytics_service.py` (media/pstdev con `statistics`), sin
    escritura de premios.
  - Contiene los god-files (deuda; ver `code-quality-assessment.md`). No consume `SSL_VERIFY`.
- **Depende de**: `backend-app-stores`, APIs Futmondo/Sofascore, config en `user_championships`.

### backend-app-stores
- **Ubicación**: `backend/app/stores/`, más `session_service.py`, `task_service.py`,
  `task_manager.py`
- **Responsabilidad**: capa estrecha de repositorios de durabilidad (intent previo). Patrón
  a seguir para nueva persistencia; no ampliar SQL-en-router. Candidato natural para alojar
  un repositorio estrecho de `team_prizes` si el diseño de premios extrae la persistencia.
- **Depende de**: Neon PostgreSQL (fallback SQLite/Turso).

### backend-app-security
- **Ubicación**: `backend/app/security/`
- **Responsabilidad**: protección de credenciales Futmondo (cifrado en reposo del material
  sensible; nunca password en claro).
- **Depende de**: `backend-app-core` (`FUTMONDO_CRED_KEY`).

## Componentes del Frontend y Soporte

### angular-app
- **Ubicación**: `angular-app/`
- **Responsabilidad**: SPA/PWA Angular 22 (componentes standalone, signals, service worker).
  - **`core/` (transversal)**: 11 servicios HTTP en `core/services/*.service.ts` (`analytics`,
    `assistant`, `auth`, `budget`, `championship`, `evolution`, `favorites`, `roster`,
    `stats`, `sync`); `core/interceptors/auth.interceptor.ts` (Bearer + refresh en cola ante
    401 + `withCredentials` para `/auth/*` — único contrato cubierto por spec);
    `core/guards/auth.guard.ts` (protección de rutas, SIN spec);
    `core/preloading/idle-preloading-strategy.ts` (precarga por inactividad, CON spec).
  - **`features/` (por pantalla)**: `market` (incl. `bid-dialog.component.ts`, que valida el
    precio de puja SÓLO en frontend — evidencia FR6), `finances`, `budget`
    (`budget-overview` + `prizes-dialog`), `calculator`, `analytics`, `evolution`,
    `statistics`. Todas consumen la superficie de lectura del backend; ninguna recalcula
    premios. SIN spec hoy.
  - **`shared/`**: UI y utilidades reutilizables (SIN spec).
- **Estado de tests (intent activo)**: `skipTests: true` global en `angular.json`; sólo 2
  specs sobre ~90 fuentes; sin infraestructura de cobertura. Detalle en
  `code-quality-assessment.md`.
- **Depende de**: backend HTTP `/api/*`, `/auth/*`.

### proxy-nginx
- **Ubicación**: `proxy/`, `angular-app/nginx*.conf`
- **Responsabilidad**: reverse proxy local y de producción; sirve la SPA y enruta `/api/*` y
  `/auth/*` al backend.
- **Depende de**: `backend-app-main`.

### cron-worker
- **Ubicación**: `cron/`, `backend/scripts/`
- **Responsabilidad**: sync programado (máquinas Fly one-shot); dispara la sincronización que
  ejecuta `sync_prizes`. Nunca emite JWT (NFR1.1).
- **Depende de**: `backend-app-services`.

## Componentes de Entrega / CI-CD (`.github/workflows/`)

Componentes de pipeline; su estado de calidad y las deudas de cobertura/paridad viven en
`code-quality-assessment.md` (artefacto propietario del intent activo).

### ci-workflow
- **Ubicación**: `.github/workflows/ci.yml`
- **Responsabilidad**: gate de Pull Request a `main` (job `quality`): gitleaks (BLOQUEANTE),
  `pytest tests -q --cov=app --cov-report=term-missing` (BLOQUEANTE, CON cobertura), `ruff`
  y `pip-audit` (advisory), `npm ci` + `ng test --watch=false` (BLOQUEANTE), `ng lint` y
  `npm audit` (advisory). Node fijado a `'22'`.
- **Depende de**: `backend` (pytest), `angular-app` (`npm ci`/`ng test`).

### fly-deploy-workflow
- **Ubicación**: `.github/workflows/fly-deploy.yml`
- **Responsabilidad**: despliegue por push a `main` (+ `workflow_dispatch`). Job `verify` =
  gitleaks@v2 (BLOQUEANTE) + `pytest tests -q` (BLOQUEANTE, **SIN `--cov`**) + `npm ci` +
  `ng test --watch=false` (BLOQUEANTE). Luego `deploy-backend` → `deploy-frontend` (Fly.io,
  `needs:` en cadena) → `smoke-test` contra `/health` (5 reintentos, HTTP 200). Objetivo del
  hueco FR17.1: los tests de `verify` se ejecutan pero no imponen cobertura.
- **Depende de**: `backend`, `angular-app`, Fly.io.

### cron-sync-workflows
- **Ubicación**: `.github/workflows/daily-sync.yml`, `.github/workflows/sofascore-sync.yml`
- **Responsabilidad**: sync programado a coste ~0 en máquinas Fly one-shot. `daily-sync.yml`
  (04:30 UTC + manual): despliega imagen cron, ejecuta sync completo, poll hasta `stopped`,
  verifica exit code. `sofascore-sync.yml` (05:00 UTC + manual): reutiliza la imagen cron,
  corre `scripts/sync_sofascore_local.py`, destrucción garantizada (`trap cleanup EXIT`).
- **Depende de**: imagen cron (`cron-worker`), Fly.io.
