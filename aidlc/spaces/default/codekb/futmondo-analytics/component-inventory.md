# Component Inventory — Futmondo Analytics

> Artefacto CodeKB (architect). Base: `developer-scan.md`. Store STALE tras FOCUSED SCAN del backend `backend/`.
> Los nombres de componente (encabezados `###`) son leídos verbatim por el guard de rescan y deben coincidir con `analyzed.components` en `reverse-engineering-timestamp.md`.

## Componentes de despliegue

### backend

- **Tipo**: servicio web (service) — Python 3.12 — FastAPI (`app.main:app`).
- **Responsabilidad**: API interna (auth + `/api/v1/*`), middleware de autenticación JWT (`AuthMiddleware`, whitelist de rutas públicas), gestión de la sesión Futmondo por usuario (en memoria), orquestación de sync asíncrono (en memoria), cálculo de finanzas/analytics, integración con Futmondo/Sofascore/IA, servicio de fotos, capa de datos PostgreSQL (SQL directo, sin ORM).
- **Depende de**: `Neon PostgreSQL` (persistencia de usuarios, refresh tokens, campeonatos y datos de dominio), `API Futmondo` y `API Sofascore` (integraciones externas), proveedores IA.
- **Consumido por**: `angular-app`, `cron`.
- **Estado en memoria (verificado este run, deuda del intent)**: `SessionStore` y `TaskManager` son singletons de proceso, no durables (ver subcomponentes y `architecture.md`). Las credenciales Futmondo (`email`/`password`) se guardan en claro en `UserSession`.
- **Evidencia**: `backend/app/main.py`, `app/auth/` (`routes.py`, `session_store.py`, `token_store.py`, `jwt_utils.py`, `dependencies.py`, `models.py`), `app/api/v1/endpoints/` (~24 routers), `app/services/` (12 módulos), `app/core/config.py`, `app/models/`, `scripts/init_db.py`.

### angular-app

- **Tipo**: aplicación (application) — TypeScript — Angular 22 PWA.
- **Responsabilidad**: UI/PWA de la analítica Futmondo (17 features), autenticación de cliente (interceptor + guards), consumo de la API v1, gráficos, chat del asistente y modo oscuro. Arranque `bootstrapApplication(App, appConfig)`; routing 100 % lazy por ruta.
- **Depende de**: `backend` (REST `/auth/*`, `/api/v1/*`), librerías Angular 22 + Material, `chart.js`/`ng2-charts`, `marked`, `rxjs`.
- **Consumido por**: usuario final (browser/iPhone).
- **Evidencia** (preservada del análisis previo): `angular-app/package.json` (`version 2.1.7`), `angular.json`, `src/main.ts`, `src/app/app.config.ts`, `src/app/app.ts`, `src/app/features/**`.

### cron

- **Tipo**: proceso worker one-shot (Fly) — reutiliza la imagen de `backend`.
- **Responsabilidad**: ejecutar `python scripts/sync_data.py` de forma programada (sync diaria y de Sofascore) en máquina Fly efímera (app `futmondo-cron`).
- **Depende de**: `backend/Dockerfile` (mismo build), `Neon PostgreSQL`, `API Futmondo`, `API Sofascore`.
- **Consumido por**: workflows programados (`daily-sync.yml`, `sofascore-sync.yml`).
- **Evidencia**: `cron/fly.toml`, `backend/scripts/sync_data.py`.

### proxy

- **Tipo**: nginx reverse proxy (`nginx:alpine`) — sólo entorno local.
- **Responsabilidad**: enrutar tráfico local (docker-compose) hacia `angular-app` y `backend` bajo `futmondo.localhost`.
- **Depende de**: `angular-app`, `backend`.
- **Consumido por**: desarrollador en local.
- **Evidencia**: `proxy/nginx.conf`, `docker-compose.yml`.

## Subcomponentes internos relevantes (backend) — verificado este run

Inventario a nivel de router/servicio; endpoints detallados se cruzan con `api-documentation.md`.

### AuthMiddleware + auth routes

- **Responsabilidad**: emisión/validación de JWT (HS256, `jwt_utils.py`), whitelist de rutas públicas, login/refresh/logout (`routes.py`), gestión de la cookie de refresh.
- **Depende de**: `SessionStore`, `token_store`, `FutmondoClient`.
- **Evidencia**: `backend/app/auth/routes.py`, `jwt_utils.py`, middleware en `app/main.py`.

### SessionStore

- **Responsabilidad**: almacén en memoria de la sesión Futmondo por usuario (`dict[str, UserSession]`, `threading.Lock` global + locks por usuario). `UserSession` guarda `email`/`password` **en claro**, `token`, `user_id`, TTL 12h. Singleton de proceso, **no durable**.
- **Consumido por**: `auth/routes` (`store_session`), `_helpers.get_user_futmondo_client`.
- **Evidencia**: `backend/app/auth/session_store.py`.

### TaskManager

- **Responsabilidad**: registro en memoria del estado/progreso de las tareas de sync asíncrono (`dict[str, Task]`, cap 20, staleness 10 min). Singleton de proceso, **no durable**; el hilo daemon muere con el proceso.
- **Consumido por**: `api/v1/endpoints/sync.py` (`trigger`, `task/{id}`).
- **Evidencia**: `backend/app/services/task_manager.py`.

### token_store

- **Responsabilidad**: persistencia de identidad y tokens en Neon — `app_users`, `refresh_tokens` (hash SHA-256, `revoked`, `expires_at`), `user_championships`; migraciones ad-hoc (`init_auth_tables()`).
- **Evidencia**: `backend/app/auth/token_store.py`.

### db_connection

- **Responsabilidad**: capa de acceso a datos multi-backend (SQLite / PostgreSQL-Neon / Turso-LibSQL), SQL directo con cursores, `ThreadedConnectionPool`, adaptación manual de placeholders (`?`↔`%s`). Sin ORM.
- **Consumido por**: `token_store`, `data_manager_v2`, `data_sync_service`, y servicios de dominio.
- **Evidencia**: `backend/app/services/db_connection.py`.

### Integration clients

- **Responsabilidad**: `futmondo_client.py` (API Futmondo, `requests.Session`), `sofascore_client.py` (Sofascore vía `curl_cffi`), `assistant_service.py` (IA). Actúan como anti-corruption layer.
- **Evidencia**: `backend/app/services/`.

## Referencias cruzadas

- Endpoints por componente: `api-documentation.md`.
- Relaciones e interacciones: `architecture.md`.
- Dependencias externas/internas detalladas: `dependencies.md`.
