# Inventario de Componentes — futmondo-analytics

## Componentes del Backend (`backend/app`)

Lista completa de componentes con responsabilidades y dependencias. Los contratos HTTP
están en `api-documentation.md`; los patrones y ubicaciones en `code-structure.md`.

### backend-app-main
- **Ubicación**: `backend/app/main.py`
- **Responsabilidad**: composición de la app FastAPI, `AuthMiddleware` +
  `AUTH_EXCLUDED_PATHS`, montaje de todos los routers (~24), endpoint
  `GET /api/v1/photos/{player_id}` (FR7) y `/health`. **Arranque resiliente**: la init de
  tablas (auth/durable-session/durable-task) degrada a `logger.warning` en vez de abortar el
  boot (decisión de resiliencia, no swallow silencioso); en startup barre tareas
  interrumpidas vía `task_service.get_task_service()`.
- **Depende de**: `backend-app-auth` (verificación de token), `backend-app-api-endpoints`
  (routers), `backend-app-core` (config/constantes), `backend-app-services`
  (`task_service`, clientes), `backend-app-stores` (`session_repository`, `task_repository`).

### backend-app-auth
- **Ubicación**: `backend/app/auth/` (`routes.py`, `token_store.py`, `session_store.py`)
- **Responsabilidad**: login/refresh/logout, emisión y verificación de JWT, cache en memoria
  de sesiones (sin password en claro) y persistencia/validación de refresh tokens.
  Contiene el bug FR9 en `token_store.is_refresh_token_valid` (precedencia naive/aware).
- **Depende de**: Neon PostgreSQL (SQL crudo directo), `backend-app-services` (cliente
  Futmondo para login), `backend-app-core`.

### backend-app-api-endpoints
- **Ubicación**: `backend/app/api/v1/endpoints/` (`market.py`, `reset_db.py`, `_helpers.py`,
  `player_finances.py`, `balances.py`, `matchdays.py`, `analytics.py`, `sync.py`, `roster`, ...)
- **Responsabilidad**: routers HTTP de la API v1.
  - **Área de sincronización/fiabilidad**: `sync.py` (`POST /sync/trigger`, `GET /sync/task/{id}`)
    orquesta el worker `data_sync_service` y consume `record_degraded_step` para dejar los
    pasos no críticos (`prizes`/`phantoms`, ~L120-200) en `DEGRADED` sin fallar la tarea
    (FR3.1).
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
  `db_connection.py`, `sync_step_status.py`, `task_manager.py`, `task_service.py`,
  `photo_service.py`, `data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB / 1915
  líneas, `assistant_service.py`, `analytics_service.py`)
- **Responsabilidad**: lógica de negocio, clientes de APIs externas (Futmondo, Sofascore),
  conexión a BD, degradación de pasos y durabilidad de tareas.
  - **Worker de sync + manejo de errores (área FR3.2/FR4, intent activo)**:
    `data_sync_service.py` orquesta la sincronización; concentra **29** ramas
    `except Exception` (muchas `logger.error(..., exc_info=True)` + `return {"status":"error"}`).
    Contiene los puntos de escritura del caché (transactions, player_favorites, team_prizes)
    y el **punto de corromper-datos**: `DELETE FROM team_prizes ... NOT IN (...)` (L1846) con
    `except → warning` tras un `commit()` previo (L1859). Ver `code-quality-assessment.md`.
  - **Cliente Futmondo** (`futmondo_client.py`): proxy JSON autenticado por usuario;
    `_make_request` traga `Timeout`/`RequestException`/`JSONDecodeError` a `None` (**hueco
    central de FR4**: sin excepción tipada).
  - **Cliente Sofascore** (`sofascore_client.py`): GET vía `curl_cffi`; distingue
    `SofascoreIPBanError` (fatal, re-lanzado) del 404 recuperable (`None`). **Patrón de
    referencia** para FR4.
  - **Conexión a BD** (`db_connection.py`): `get_connection()` hace `rollback()` + `raise`
    (fatal, no traga); `ThreadedConnectionPool` (5-20) reintenta 3 veces conexiones muertas y
    recrea el pool; `_test_connection()` re-lanza en fallo de arranque. Contiene 9 ramas
    amplias.
  - **Helper de degradación** (`sync_step_status.py`): `StepStatus`/`record_degraded_step`
    (seam FR3.1) — marca `DEGRADED` para fallos NO críticos (registra, NO re-lanza).
  - **Durabilidad de tareas** (`task_service.py`, `task_manager.py`): `TaskService._cache_call`
    separa autoridad-DB (debe tener éxito → `TaskPersistenceError`) de caché best-effort
    (`TaskManager`, traga y loguea, nunca falla la operación).
  - **Productor de premios (fórmula)**: `data_sync_service.sync_prizes()` (~1577-1885)
    calcula todos los términos por (equipo, jornada) con gating
    `award_round_prizes = is_closed AND round_fully_played AND NOT pseudo-ronda`, UPSERTea
    `team_prizes` (única fuente de verdad) con limpieza defensiva `DELETE ... NOT IN`.
  - **Analítica derivada**: `analytics_service.py` (media/pstdev con `statistics`).
  - Contiene los god-files (deuda; ver `code-quality-assessment.md`). No consume `SSL_VERIFY`.
- **Depende de**: `backend-app-stores`, APIs Futmondo/Sofascore, Neon PostgreSQL (vía
  `db_connection`), config en `user_championships`.

### backend-app-stores
- **Ubicación**: `backend/app/stores/` (`task_repository`, `session_repository`), más
  `session_service.py`, `task_service.py`, `task_manager.py`
- **Responsabilidad**: capa estrecha de repositorios de durabilidad (intent previo).
  `task_repository` es la **autoridad** de estado de tareas en BD; `task_manager` es caché
  best-effort. Patrón a seguir para nueva persistencia; no ampliar SQL-en-router. Candidato
  natural para alojar un repositorio estrecho de `team_prizes`.
- **Depende de**: Neon PostgreSQL (fallback SQLite/Turso), `backend-app-services`
  (`db_connection`).

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
    401 + `withCredentials` para `/auth/*` — cubierto por spec);
    `core/guards/auth.guard.ts` (protección de rutas);
    `core/preloading/idle-preloading-strategy.ts` (precarga por inactividad, con spec).
  - **`features/` (por pantalla)**: `market` (incl. `bid-dialog.component.ts`, que valida el
    precio de puja SÓLO en frontend — evidencia FR6), `finances`, `budget`
    (`budget-overview` + `prizes-dialog`), `calculator`, `analytics`, `evolution`,
    `statistics`. Todas consumen la superficie de lectura del backend; ninguna recalcula
    premios.
  - **`shared/`**: UI y utilidades reutilizables.
- **Nota**: el estado de tests/cobertura del frontend (evolucionado en intents previos) vive
  en `code-quality-assessment.md`.
- **Depende de**: backend HTTP `/api/*`, `/auth/*`.

### proxy-nginx
- **Ubicación**: `proxy/`, `angular-app/nginx*.conf`
- **Responsabilidad**: reverse proxy local y de producción; sirve la SPA y enruta `/api/*` y
  `/auth/*` al backend.
- **Depende de**: `backend-app-main`.

### cron-worker
- **Ubicación**: `cron/`, `backend/scripts/`
- **Responsabilidad**: sync programado (máquinas Fly one-shot); dispara la sincronización que
  ejecuta el worker `data_sync_service` (incl. `sync_prizes`). Los scripts one-shot
  (`migrate_to_turso.py`, `migrate_data_to_turso.py`, `sync_sofascore_local.py`, etc.) usan
  `except Exception as e` con log (no `except: pass`). Nunca emite JWT (NFR1.1).
- **Depende de**: `backend-app-services`.

## Componentes de Entrega / CI-CD (`.github/workflows/`)

Componentes de pipeline; su estado de calidad y las deudas de cobertura/paridad viven en
`code-quality-assessment.md`.

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
  `needs:` en cadena) → `smoke-test` contra `/health` (5 reintentos, HTTP 200).
- **Depende de**: `backend`, `angular-app`, Fly.io.

### cron-sync-workflows
- **Ubicación**: `.github/workflows/daily-sync.yml`, `.github/workflows/sofascore-sync.yml`
- **Responsabilidad**: sync programado a coste ~0 en máquinas Fly one-shot. `daily-sync.yml`
  (04:30 UTC + manual): despliega imagen cron, ejecuta sync completo, poll hasta `stopped`,
  verifica exit code. `sofascore-sync.yml` (05:00 UTC + manual): reutiliza la imagen cron,
  corre `scripts/sync_sofascore_local.py`, destrucción garantizada (`trap cleanup EXIT`).
- **Depende de**: imagen cron (`cron-worker`), Fly.io.
