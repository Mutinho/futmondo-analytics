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
  - **Área de premios/finanzas (intent activo)**: `player_finances.get_player_finances`
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
  - **Productor de premios (fórmula del intent)**: `data_sync_service.sync_prizes()`
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
- **Responsabilidad**: SPA/PWA Angular 22. Features del área de premios/finanzas:
  `features/finances/finances.component.ts` (presentación de finanzas por usuario),
  `features/budget/budget-overview/budget-overview.component.ts` y su
  `prizes-dialog.component.ts` (saldos y desglose de premios por jornada),
  `features/calculator/calculator.component.ts` (cálculo/simulación) y
  `features/analytics/*` (gráficos Chart.js). Además,
  `features/market/bid-dialog.component.ts` valida el precio de la puja SÓLO en frontend
  (evidencia FR6). Todas consumen la superficie de lectura del backend; ninguna recalcula
  premios.
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
