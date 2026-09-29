# Component Inventory — futmondo-analytics

Lista completa de componentes lógicos con responsabilidad y dependencias. Los
nombres de encabezado `###` de esta lista se usan **verbatim** en
`analyzed.components` del bloque Scope of Analysis
(`reverse-engineering-timestamp.md`). Los tamaños/deuda no se repiten aquí; ver
`code-quality-assessment.md`.

### backend-app-core

- **Responsabilidad**: bootstrap ASGI FastAPI (`main.py`): CORS, `AuthMiddleware`
  JWT, montaje de ~20 routers, arranque idempotente de esquemas durables, mount
  estático de fotos; configuración en `core/config.py` (`JWT_SECRET` NFR1.1).
- **Dependencias**: `api-v1-endpoints`, `auth-jwt`, `services-*`, `stores-durable`.
- **Evidencia**: `backend/app/main.py`, `backend/app/core/config.py`.

### api-v1-endpoints

- **Responsabilidad**: routers HTTP delgados bajo `/api/v1/*` que delegan en la
  capa de servicios; incluye el router `assistant` y helpers (`_helpers.py`,
  `_sofascore_helpers.py`).
- **Dependencias**: `services-analytics`, `services-prizes`, `assistant-service`,
  clientes de integración, `db-connection`.
- **Evidencia**: `backend/app/api/v1/endpoints/` (~20 módulos-router).

### auth-jwt

- **Responsabilidad**: login/refresh/logout, emisión y verificación de JWT,
  almacén de tokens.
- **Dependencias**: `stores-durable`, `core/config.py`.
- **Evidencia**: `backend/app/auth/` (`routes.py`, `jwt_utils.py`, `token_store.py`).

### assistant-service

- **Responsabilidad**: asistente IA (god-file **objetivo del intent**):
  guardrails, respuestas factuales, `ContextBuilder`, `AssistantUsageTracker`,
  orquestación `ask()`/`ask_stream()` con fallback LLM Groq→Gemini. Superficie
  pública `get_assistant_service()` + `async ask(...)`.
- **Dependencias**: `db-connection`, LLM externos (Groq/Gemini).
- **Evidencia**: `backend/app/services/assistant_service.py`.

### services-analytics

- **Responsabilidad**: analítica derivada (bounded context DDD Oleada 1 de
  referencia): fachada + domain/ports + application + infrastructure.
- **Dependencias**: `db-connection` (vía adaptador), `data-manager-v2`.
- **Evidencia**: `backend/app/services/analytics/`, `analytics_service.py` (shim).

### services-prizes

- **Responsabilidad**: cálculo de premios (patrón secundario Oleada 1): cálculo
  puro + writer de persistencia.
- **Dependencias**: `db-connection`.
- **Evidencia**: `backend/app/services/prizes/` (`calculator.py`, `team_prizes_writer.py`).

### data-manager-v2

- **Responsabilidad**: acceso/gestión de datos del dominio (god-file); superficie
  de lectura consumida por `analytics/`.
- **Dependencias**: `db-connection`.
- **Evidencia**: `backend/app/services/data_manager_v2.py`.

### data-sync-service

- **Responsabilidad**: sincronización asíncrona de 11 pasos desde Futmondo y
  Sofascore hacia la BD (god-file); reemplazo transaccional atómico.
- **Dependencias**: `futmondo-client`, `sofascore-client`, `db-connection`,
  `sync-step-status`, `task-service`.
- **Evidencia**: `backend/app/services/data_sync_service.py`.

### integration-clients

- **Responsabilidad**: clientes de integración saliente Futmondo y Sofascore, con
  excepciones tipadas por modo de fallo.
- **Dependencias**: `requests`, `curl_cffi`, `integration_errors`.
- **Evidencia**: `backend/app/services/futmondo_client.py`, `sofascore_client.py`,
  `futmondo_service.py`, `integration_errors.py`.

### services-support

- **Responsabilidad**: soporte de dominio: tareas (`task_manager.py`,
  `task_service.py`), sesión (`session_service.py`), fotos (`photo_service.py`,
  god-file menor), inicialización (`data_initializer*.py`), estado de pasos
  (`sync_step_status.py`).
- **Dependencias**: `db-connection`, `stores-durable`.
- **Evidencia**: `backend/app/services/` (módulos citados).

### db-connection

- **Responsabilidad**: gestión de conexión y cursor; `adapt_params` para
  compatibilidad de placeholders SQLite (`?`) / PostgreSQL.
- **Dependencias**: `psycopg2-binary`.
- **Evidencia**: `backend/app/services/db_connection.py`.

### stores-durable

- **Responsabilidad**: repositorios durables de sesión y tarea (esquema
  idempotente, sweep de tareas interrumpidas al arranque).
- **Dependencias**: `db-connection`.
- **Evidencia**: `backend/app/stores/`.

### frontend-angular-app

- **Responsabilidad**: SPA/PWA Angular 22 (core/services, features, shared) que
  consume la API; fuera del alcance de cambio del intent (solo sube ratchet de
  cobertura).
- **Dependencias**: `api-v1-endpoints` (vía HTTP/proxy nginx).
- **Evidencia**: `angular-app/src/app/`, `angular-app/package.json`,
  `angular-app/angular.json`.
