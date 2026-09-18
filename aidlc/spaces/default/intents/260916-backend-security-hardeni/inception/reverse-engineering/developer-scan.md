# Developer Scan — Backend Security Hardening (security-patch)

> Handoff del link 1 (developer) al link 2 (architect) del stage Reverse Engineering.
> El architect sintetiza los 9 artefactos del CodeKB a partir de este documento.
> Idioma de conversación: castellano. Identificadores, rutas y nombres de framework en su forma original.

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply**:
  - `backend/app/main.py` (app FastAPI, `AuthMiddleware`, `AUTH_EXCLUDED_PATHS`, montaje de routers, endpoint `GET /api/v1/photos/{player_id}`, `/health`)
  - `backend/app/core/config.py` (resolución de entorno, guard `resolve_jwt_secret`/`is_cron_worker` NFR1.1, `DATABASE_TYPE`, `FUTMONDO_CRED_KEY`)
  - `backend/app/core/constants.py`
  - `backend/app/auth/token_store.py` (`is_refresh_token_valid` — bug FR9, tablas auth, refresh tokens)
  - `backend/app/auth/session_store.py` (cache en memoria de sesiones, sin password en claro)
  - `backend/app/auth/routes.py` (`/auth/login`, `/auth/refresh`, `/auth/logout`, `_auto_detect_championships`)
  - `backend/app/api/v1/endpoints/market.py` (`place_bid` FR6, `cancel_bid`, `get_market_today`)
  - `backend/app/api/v1/endpoints/reset_db.py` (`/reset`, `/populate`, guard `_require_db_admin`/`ENABLE_DB_ADMIN` FR18)
  - `backend/app/api/v1/endpoints/_helpers.py` (`get_user_futmondo_client`, `get_championship_config`)
  - `angular-app/src/app/features/market/bid-dialog.component.ts` (validación de precio SÓLO en frontend — evidencia FR6)
  - `docker-compose.yml` (`SSL_VERIFY=0` — FR8), `backend/fly.toml`, `.env.example`
  - `.github/workflows/ci.yml` (gate de PR), `.github/workflows/fly-deploy.yml` (verify + deploy + smoke)
  - `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`, `angular-app/package.json`
  - `backend/tests/test_db_admin_guard.py`, `test_jwt_startup.py`, `test_auth_characterization.py` (tests de guards existentes)

- **Skimmed only** (nivel directorio, sin lectura profunda por scope security-patch/minimal):
  - `backend/app/services/` (god-files `data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB, `assistant_service.py` ~51 KB, `analytics_service.py`, `futmondo_client.py`, `photo_service.py`, `sofascore_client.py`) — sólo se verificó que `SSL_VERIFY`/`verify=` no se consultan y el flujo de `place_bid` hacia `client.session.post`
  - `backend/app/stores/`, `backend/app/services/session_service.py`, `task_service.py`, `task_manager.py` (durabilidad — intent anterior, no tocado por estas FR)
  - Resto de endpoints `backend/app/api/v1/endpoints/*` (analytics, balances, sync, roster, etc.)
  - `angular-app/src/app/**` salvo el diálogo de puja; `backend/scripts/**`; `backend/static/photos/players/**` (~800 PNG de datos, no código)
  - `.kiro/**`, `aidlc/**`, `docs/**` (herramienta AI-DLC y documentación, fuera del código de aplicación)

### Packages Found

- `backend/app` — aplicación FastAPI (Python 3.12). Submódulos: `api/v1/endpoints` (routers HTTP), `auth` (JWT + sesión), `core` (config/constantes), `services` (lógica de negocio + clientes externos), `stores` (repositorios de durabilidad), `security` (protección de credenciales), `models`.
- `backend/scripts` — scripts one-shot (sync, migraciones a Turso, exportaciones). No forman parte del servicio web.
- `angular-app` — frontend Angular 22 (PWA). Features standalone; el diálogo de puja vive en `features/market/`.
- `proxy`, `angular-app/nginx*.conf` — reverse proxy nginx (local y prod).
- `cron/` — configuración Fly.io del worker cron (sync programado; nunca emite JWT — ver NFR1.1).

### Build System

- **Backend**: pip + `requirements.txt`; imagen `backend/Dockerfile` (+ `nixpacks.toml`); arranque `entrypoint.sh`/`run.py`. Deploy Fly.io (`backend/fly.toml`, app `futmondo-api`, puerto 8000, check `/health`, `shared-cpu-1x`/256 MB).
- **Frontend**: npm (`npm@11.12.1`), Angular CLI (`ng build`/`ng test`); Node fijado en `.nvmrc` = `22.22.3`. Deploy Fly.io (`angular-app/fly.toml`, nginx).
- **Config/Dependencias clave**: `DATABASE_URL` → PostgreSQL (Neon) es el modo productivo; fallback SQLite/Turso. `SSL_VERIFY` sólo declarado en `docker-compose.yml`.

### APIs Discovered

Middleware `AuthMiddleware` (en `main.py`) protege todo `/api/v1/*` y `/auth/*` salvo `AUTH_EXCLUDED_PATHS = {"/auth/login","/auth/refresh","/auth/logout","/health","/","/docs","/openapi.json","/redoc"}`. Requiere `Authorization: Bearer <access>` verificado con `verify_token(..., expected_type="access")`.

Endpoints relevantes a las FR:
- `POST /api/v1/market/bid` — `place_bid` (**FR6**). Params query: `championship_id`, `player_id`, `player_slug`, `price: int`, `is_clause`. **NO valida `price`** (rango/positividad); lo pasa directo al proxy Futmondo `POST {base_url}/1/market/bid`.
- `GET /api/v1/photos/{player_id}` — `get_player_photo` (**FR7**). Definido a nivel de app en `main.py`; su path `/api/v1/photos/...` NO está en `AUTH_EXCLUDED_PATHS`, por lo que el middleware SÍ exige Bearer token (no es público). Nota: la ruta `/static/photos/*` (StaticFiles montado) no empieza por `/api/v1` ni `/auth`, así que el middleware la deja pasar sin auth (redirecciones 302 del endpoint apuntan ahí).
- `POST /api/v1/database/reset` y `POST /api/v1/database/populate` — (**FR18**). `_require_db_admin()` lanza 404 salvo `ENABLE_DB_ADMIN ∈ {1,true,yes,on}`. Guard YA implementado y con test (`test_db_admin_guard.py`).
- `POST /auth/refresh` — usa `is_refresh_token_valid(token_hash)` de `token_store.py` (**FR9**).

Todos los routers se montan en `main.py` (prefijos `/api/v1/...`); `matchdays` se monta también en `/v1/matchdays`. Router auth sin prefijo `/api/v1` (vive en `/auth/*`).

### Frameworks & Libraries

- Backend: `fastapi>=0.104.0`, `uvicorn[standard]`, `pydantic>=2.5.0`, `PyJWT==2.9.0`, `requests>=2.31.0`, `curl_cffi>=0.16.0`, `psycopg2-binary`, `libsql-experimental==0.0.55` (no compila fuera de 3.12), `python-dotenv`, `google-genai`, `groq`. Test: `pytest>=8.0.0`, `pytest-cov`, `httpx` (para `TestClient`).
- Frontend: Angular 22 (`@angular/*` `^22.1.0`), Angular Material 22, `chart.js`, `ng2-charts`, `marked`, `rxjs ~7.8.0`; devDeps `vitest ^4.0.8`, `jsdom`, `prettier ^3.8.1`, `typescript ~6.0.2`.

### Test Coverage

- **Test Directories**: `backend/tests/` (pytest, ejecutado desde `backend/` con `pytest.ini`: `testpaths=tests`, `pythonpath=.`). Frontend: specs `*.spec.ts` con `ng test` (Vitest + jsdom).
- **Test Frameworks**: pytest + pytest-cov (backend); Vitest vía `@angular/build:unit-test` (frontend).
- **Coverage Config**: sin piso bloqueante — NO existe `cov-fail-under`/`fail_under`/`coverageThreshold` en el repo (ratcheting diferido, decisión de equipo).
- **Cobertura ya existente relevante a las FR**:
  - FR18: `test_db_admin_guard.py` — 404 por defecto, 404 con valor no-afirmativo, 200 con `ENABLE_DB_ADMIN=1` (con doble de `DataManagerV2`).
  - FR9: `test_auth_characterization.py` — **caracteriza el bug** de `is_refresh_token_valid` (token aware futuro → `False` erróneo; naive futuro → `True`). Estos tests documentan el fallo y deberán actualizarse cuando FR9 se corrija.
  - NFR1.1 (contexto FR): `test_jwt_startup.py` cubre `resolve_jwt_secret`.
  - Sin cobertura directa de `place_bid` (FR6) ni de la publicidad del endpoint `/photos` (FR7); FR8 no tiene test (es config).

### Code Quality Indicators

- **Linting**: backend `ruff` (`backend/ruff.toml`: `select=["E","F","I"]`, `ignore=["E501","E402","E722"]`, `line-length=100`) — advisory en CI (`continue-on-error`). Frontend ESLint flat config — advisory.
- **CI/CD**: `.github/workflows/ci.yml` (PR→main): gitleaks + pytest + ng test BLOQUEANTES; ruff/ESLint/pip-audit/npm audit advisory. `fly-deploy.yml` (push→main): job `verify` (gitleaks + pytest **sin `--cov`** + ng test) → deploy backend → deploy frontend → smoke `/health` (5 reintentos). Crons `daily-sync.yml`, `sofascore-sync.yml` (máquinas Fly one-shot).
- **Documentation**: README extenso, `docs/DEPLOY.md`, `docs/ROLLBACK.md`, `docs/PR-GATE.md`; docstrings en inglés, texto de usuario/HTTPException `detail` en castellano.

### Technical Debt Signals

- **FR6**: `place_bid` acepta `price: int = Query(...)` sin validar rango/positividad; la única validación (min = valor de mercado, max = puja máxima, > 0) vive en `bid-dialog.component.ts` (frontend), evadible llamando la API directamente.
- **FR8**: `SSL_VERIFY=0` está en `docker-compose.yml` (entorno local) pero **NO se lee en ningún módulo Python** (grep sobre `backend/**` da 0 usos; `verify=` en `futmondo_client.py` no lo consulta). El flag está huérfano: no llega a producción hoy porque nadie lo consume, pero no está aislado/documentado de forma inequívoca. `backend/fly.toml [env]` no lo declara.
- **FR9**: en `token_store.is_refresh_token_valid`, la línea de expiración usa un ternario de precedencia ambigua mezclando `datetime.now(timezone.utc)` con `expires_at` naive/aware: `if expires_at and datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc) if expires_at.tzinfo is None else expires_at:`. Con un `expires_at` aware (caso real PostgreSQL/Turso vía `.isoformat()` con offset) evalúa el `else` → devuelve el propio datetime (truthy) → `return False`, rechazando tokens ACTIVOS futuros.
- **FR18**: guard ya correcto; sólo faltaría reforzar/consolidar la cobertura si el diseño lo pide (ya existe test).
- SQL crudo disperso en auth/routers sin capa repositorio (`token_store.py`, `routes._auto_detect_championships`, `_helpers.get_championship_config`); god-files `data_manager_v2.py` (~166 KB) y `data_sync_service.py` (~84 KB). No ampliar ese patrón.
- Imports dinámicos dentro de funciones (p. ej. `import requests` dentro de `get_player_photo`); `refresh` ya migró a import estático (comentario team.md sobre evitar `__import__`).

## Handoff Summary

- **Intent-relevant finding**: Las cinco FR aterrizan casi por completo en el backend FastAPI y su estado actual difiere entre sí:
  - **FR6 (validar `price`)**: PENDIENTE. `market.py::place_bid` (líneas del `@router.post("/bid")`) no valida; sólo el frontend `bid-dialog.component.ts` valida.
  - **FR7 (`/photos/{player_id}` auth)**: ya está protegido — la ruta `/api/v1/photos/...` NO está en `AUTH_EXCLUDED_PATHS` (`main.py`), luego el `AuthMiddleware` exige Bearer. Trabajo probable = documentar/confirmar (¿debe ser pública para `<img>` sin token?) más que cambiar código; ojo con `/static/photos/*` que sí queda fuera del middleware.
  - **FR8 (`SSL_VERIFY=0`)**: flag sólo en `docker-compose.yml`, sin lector en Python y ausente de `fly.toml`; hoy inocuo pero no aislado explícitamente.
  - **FR9 (`is_refresh_token_valid`)**: bug real de precedencia con datetimes naive/aware en `token_store.py`, ya caracterizado por tests que habrá que actualizar al corregir.
  - **FR18 (`/database/reset`|`/populate`)**: guard `ENABLE_DB_ADMIN` YA implementado y testeado (404 por defecto); posible refuerzo/consolidación de test.
- **Risks / follow-up**:
  - El job `verify` de `fly-deploy.yml` (push→main) corre `pytest -q` **sin `--cov`**; ya incluye gitleaks (hueco FR5 cerrado). No es idéntico al gate de PR, pero es defensa en profundidad.
  - Corregir FR9 exige actualizar deliberadamente los tests de caracterización que hoy congelan el fallo (`test_auth_characterization.py`).
  - Restricción dura de coste 0 € (Neon/Fly/GitHub Actions free): cualquier propuesta debe mantenerse en tiers gratuitos.
  - `libsql-experimental==0.0.55` sólo compila en Python 3.12 (relevante para reproducir la suite local; los tests usan fakes SQLite).
  - Mantener la nueva validación/lógica tras capas estrechas; no ampliar SQL-en-router ni los god-files existentes.
