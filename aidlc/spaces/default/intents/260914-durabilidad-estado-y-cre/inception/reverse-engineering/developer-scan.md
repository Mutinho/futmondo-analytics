# Escaneo de código (Developer) — Futmondo Analytics (backend)

> Escaneo FOCALIZADO del backend FastAPI (`backend/`) para el intent
> **durabilidad del estado y credenciales Futmondo (FR1 + FR5)**.
> Profundidad de etapa: Standard. Breadth: FOCUSED. El frontend Angular
> (`angular-app/`) queda fuera del foco. Store previo: STALE — este escaneo se
> fusionará; la cobertura profunda permanece dentro de `backend/`.

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply** (todo dentro de `backend/`):
  - `backend/app/auth/session_store.py`
  - `backend/app/services/task_manager.py`
  - `backend/app/auth/token_store.py`
  - `backend/app/auth/routes.py`
  - `backend/app/auth/jwt_utils.py`
  - `backend/app/auth/dependencies.py`
  - `backend/app/auth/models.py`
  - `backend/app/services/db_connection.py`
  - `backend/app/core/config.py`
  - `backend/app/main.py`
  - `backend/app/api/v1/endpoints/sync.py`
  - `backend/app/api/v1/endpoints/_helpers.py`
  - `backend/app/services/futmondo_client.py` (cabecera: constructor, `login`, gestión de `token`/`user_id`/`session`)
  - `backend/requirements.txt`, `backend/Dockerfile`, `backend/ruff.toml`, `backend/pytest.ini`, `backend/conftest.py`, `backend/nixpacks.toml`, `backend/fly.toml`
  - `backend/scripts/init_db.py`
- **Skimmed only** (a nivel de directorio/fichero, sin lectura profunda):
  - `backend/app/services/` de dominio de datos: `data_manager_v2.py` (~166 KB), `data_sync_service.py` (~84 KB), `analytics_service.py`, `assistant_service.py`, `sofascore_client.py`, `photo_service.py`, `futmondo_service.py`, `data_initializer*.py`
  - Resto de `backend/app/api/v1/endpoints/` fuera de auth/sync (`market.py`, `balances.py`, `player_finances.py`, `analytics.py`, `roster.py`, `transactions.py`, `favorites.py`, `clausulable_players.py`, `sofascore_sync.py`, `user.py`, `reset_db.py`, etc.)
  - `backend/scripts/` (scripts de migración/exportación puntuales), `backend/tests/` (inventariados, no ejecutados), `backend/static/photos/` (activos)
  - `angular-app/` — fuera de foco por diseño (breadth FOCUSED)

### Packages Found

- `app` — paquete raíz de la aplicación — Python 3.12 — FastAPI app + middleware de auth
- `app.auth` — módulo — Python — autenticación: JWT, sesiones Futmondo por usuario, almacén de refresh tokens, dependencias FastAPI
- `app.services` — módulo — Python — servicios de dominio, integración externa (Futmondo/Sofascore), acceso a BD y TaskManager
- `app.api.v1.endpoints` — módulo — Python — routers FastAPI por área funcional (auth vive fuera, en `app.auth.routes`)
- `app.core` — módulo — Python — configuración (`config.py`) y constantes
- `app.models` — módulo — Python — modelos de datos ligeros (`models.py`)

### Build System

- **Type**: contenedor Docker (backend) + Python/pip; despliegue en Fly.io (`fly.toml`, región `cdg`); config alternativa Railway/Nixpacks (`nixpacks.toml`, Python 3.11).
- **Config Files**: `backend/Dockerfile` (base `python:3.12-slim`, `uvicorn app.main:app`), `backend/requirements.txt`, `backend/fly.toml`, `backend/nixpacks.toml`, `backend/entrypoint.sh`, `backend/run.py`, `backend/ruff.toml`, `backend/pytest.ini`, `backend/conftest.py`.
- **Build Dependencies**: `app.main` → routers de `app.api.v1.endpoints.*` + `app.auth.routes`; auth → `jwt_utils`/`token_store`/`session_store` → `db_connection`/`futmondo_client`; sync → `task_manager`/`data_sync_service`/`data_manager_v2`/`db_connection`.
- **Nota de coherencia**: Dockerfile usa Python 3.12; `nixpacks.toml` fija `python311`. Divergencia de versión de runtime entre plataformas de despliegue.

### APIs Discovered

- **API interna (FastAPI, área auth)** — `app/auth/routes.py`, prefijo `/auth`:
  - `POST /auth/login` — valida credenciales contra Futmondo (`FutmondoClient.login`), hace upsert del usuario, emite access+refresh JWT, fija cookie HttpOnly `futmondo_refresh_token`, guarda la sesión Futmondo en memoria (`store_session`) y auto-detecta campeonatos.
  - `POST /auth/refresh` — verifica firma + no-revocado del refresh token (cookie) y emite nuevo access token. **No reconstruye la sesión Futmondo en memoria.**
  - `POST /auth/logout` — revoca refresh token, elimina sesión en memoria, limpia cookie.
- **API interna (FastAPI, área sync)** — `app/api/v1/endpoints/sync.py`, prefijo `/api/v1/sync`:
  - `POST /trigger` — lanza sync asíncrono en `threading.Thread` (daemon); crea `Task` en `TaskManager`; 409 si ya hay tarea activa; usa `get_user_futmondo_client(request)`.
  - `GET /task/{task_id}` — polling del estado/progreso de la tarea (desde memoria del `TaskManager`).
  - `GET /status`, `GET /last-sync` — leen metadatos de sync desde BD (`sync_metadata`).
- **Middleware de auth** — `app/main.py` `AuthMiddleware`: exige `Bearer` en `/api/v1/*`; excluye `/auth/*`, `/health`, `/`, `/docs`, `/openapi.json`, `/redoc`; inyecta `request.state.user`.
- **API externa consumida** — Futmondo (`FutmondoClient`, base `https://api.futmondo.com`): `POST /5/login/with_mail`, `POST /2/user/activechampionships`, `POST /2/championship/teams`, y endpoints de datos (standings, roster, transacciones) usados por `data_sync_service`. Autenticación por `token`+`userid` en el cuerpo (`header`).

### Frameworks & Libraries

- `fastapi` — >=0.104.0 — framework web/API
- `uvicorn[standard]` — >=0.24.0 — servidor ASGI
- `pydantic` — >=2.5.0 — modelos/validación (`app.auth.models`)
- `PyJWT` (`jwt`) — ==2.9.0 — firma/verificación JWT HS256
- `psycopg2-binary` — >=2.9.9 — cliente PostgreSQL (Neon) + `ThreadedConnectionPool`
- `libsql-experimental` — ==0.0.55 — backend Turso/LibSQL (ruta alternativa, réplica embebida)
- `requests` — >=2.31.0 — HTTP del `FutmondoClient` (usa `requests.Session`)
- `curl_cffi` — >=0.16.0 — cliente HTTP para Sofascore (declarado; usado en `sofascore_client`, skimmed)
- `python-dotenv` — >=1.0.0 — carga `.env`
- `google-genai` ==1.14.0, `groq` ==0.25.0 — asistente IA (fuera de foco)
- Test: `pytest` >=8.0.0, `pytest-cov` >=5.0.0, `httpx` >=0.27.0 (para `TestClient`)

### Test Coverage

- **Test Directories**: `backend/tests/`
- **Test Frameworks**: `pytest` (config en `pytest.ini`: `testpaths=tests`, `pythonpath=.`, se ejecuta desde `backend/`)
- **Coverage Config**: `pytest-cov` presente; cobertura informativa, **sin piso bloqueante todavía** (activable con `--cov=app`).
- **Tests relevantes al intent** (red de seguridad / characterization-first): `test_auth_characterization.py`, `test_jwt_startup.py`, `test_db_admin_guard.py`, `test_db_engine_characterization.py`, `test_finance_characterization.py`, `test_analytics_service.py`, `test_sofascore_sync_characterization.py`. `conftest.py` provee `clean_jwt_env` y fija `sys.path`. **No hay tests directos de `SessionStore` ni de `TaskManager`** (estado en memoria sin cobertura).

### Code Quality Indicators

- **Linting**: `ruff` (config `backend/ruff.toml`), `select=["E","F","I"]`, en modo TOLERANTE/advisory en CI (continue-on-error) por fase de saneamiento; ignora `E501/E402/E722`.
- **CI/CD**: GitHub Actions (referenciado en README y reglas de proyecto); el gate ejecuta `pytest` + `ruff` advisory. Despliegue Fly.io on-merge; healthcheck `/health`.
- **Documentation**: docstrings de módulo/función presentes y descriptivos en el área auth/sync; OpenAPI automático de FastAPI en `/docs`. `README.md` raíz documenta arquitectura y endpoints.

### Technical Debt Signals

- **Estado 100% en memoria, no durable (núcleo del intent)**:
  - `SessionStore` (`app/auth/session_store.py`) — singleton de proceso: `dict[str, UserSession]` con `threading.Lock` global + locks por usuario. **Se pierde entero al reiniciar/redeploy** o al escalar a más de una máquina. `fly.toml` fija `min=max=1` máquina, tapando el problema multi-instancia pero no el de reinicio.
  - `TaskManager` (`app/services/task_manager.py`) — singleton de proceso: `dict[str, Task]`, cap de 20 tareas, staleness a 10 min. El estado y progreso del sync async **no sobrevive a un reinicio**; una tarea en curso queda huérfana (el hilo daemon muere con el proceso). Sin persistencia ni idempotencia.
- **Credenciales Futmondo en claro en memoria (núcleo del intent)**:
  - `UserSession` guarda `email` y `password` **en texto plano** en el objeto en memoria (`session_store.py`). El docstring de `_helpers.get_user_futmondo_client` menciona re-crear la sesión desde credenciales guardadas, pero **tras reinicio esas credenciales ya no existen**: el código real devuelve **HTTP 403** ("Sesión de Futmondo expirada"), forzando re-login. Es decir, la reconstrucción prometida no ocurre — hay deuda entre el comentario y el comportamiento.
  - `/auth/refresh` renueva el access JWT pero **no reconstruye la sesión Futmondo**: tras un reinicio el usuario tiene JWT válido pero cualquier endpoint que necesite el cliente Futmondo falla con 403 hasta re-login.
- **Persistencia actual (lo que SÍ es durable)**: sólo va a BD la identidad de usuario y los tokens de refresh:
  - `token_store.py` crea/gestiona `app_users`, `refresh_tokens` (hash SHA-256, flag `revoked`, `expires_at`) y `user_championships`. Los refresh tokens **sí** persisten y soportan revocación; los datos de dominio (transacciones, jugadores, standings) persisten vía `data_manager_v2`.
- **Capa de acceso a datos** (`db_connection.py`): abstracción propia multi-backend (SQLite / PostgreSQL-Neon / Turso-LibSQL), **SQL directo con cursores**, sin ORM. Adaptación manual de placeholders (`?`↔`%s`) y de sintaxis. Migraciones ad-hoc: `token_store.init_auth_tables()` con `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE` envueltos en `try/except: pass` (sin herramienta de migraciones tipo Alembic; sin versionado de esquema).
- **Otras señales**: `except Exception: pass` en varios puntos (migraciones, auto-detección de campeonatos); imports diferidos dentro de funciones (patrón repetido); `refresh` usa `__import__(...)` dinámico para obtener `get_db`; posible bug de precedencia en la comparación de expiración de `is_refresh_token_valid` (ternaria sin paréntesis). Divergencia de versión Python 3.12 (Docker) vs 3.11 (Nixpacks). Guard de arranque JWT ya endurecido y cubierto por tests (`test_jwt_startup.py`, NFR1.1).

## Handoff Summary

- **Intent-relevant finding**: Todo el estado sensible al intent vive **en memoria de un único proceso** y no es durable. `SessionStore` (`backend/app/auth/session_store.py`) mantiene `UserSession` con `email`/`password` **en claro** y TTL de 12h; `TaskManager` (`backend/app/services/task_manager.py`) mantiene tareas de sync (`dict`, cap 20, stale 10 min) sólo en RAM. Un reinicio/redeploy en Fly.io borra ambos: los refresh JWT persisten en BD (`refresh_tokens` en Neon), pero la sesión Futmondo no se reconstruye — `_helpers.get_user_futmondo_client` devuelve **403** forzando re-login, y `/auth/refresh` renueva el access token sin recrear el cliente Futmondo. La persistencia hoy es sólo `app_users` + `refresh_tokens` + `user_championships` + datos de dominio, vía SQL directo (sin ORM) sobre el abstractor multi-backend `db_connection.py` (SQLite/PostgreSQL-Neon/Turso), con migraciones ad-hoc `CREATE IF NOT EXISTS`/`ALTER` en `try/except`.
- **Risks / follow-up**:
  - **FR5 (credenciales)**: guardar `password` en claro en memoria es la deuda de seguridad central; cualquier diseño de durabilidad debe decidir cifrado en reposo / almacén de secretos y evitar reintroducir el patrón en BD.
  - **FR1 (durabilidad de estado)**: persistir sesión y estado de tareas requiere elegir backend (Neon ya disponible; Turso es ruta alternativa) y respetar la regla de **coste 0€** del proyecto (tiers gratuitos Neon/Fly.io).
  - `fly.toml` fija 1 máquina (min=max=1): oculta el problema multi-instancia pero no el de reinicio; una solución no debe asumir instancia única.
  - No existen tests de `SessionStore`/`TaskManager`: la metodología del repo es characterization-first; conviene congelar comportamiento antes de refactorizar.
  - Divergencia de runtime Python (3.12 Docker vs 3.11 Nixpacks) a normalizar si el diseño toca dependencias.
