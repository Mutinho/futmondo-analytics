# Escaneo de código — Handoff del Developer (Reverse Engineering)

> Primer eslabón del pipeline de reverse-engineering. Escaneo FULL (primera vez),
> profundidad STANDARD, proyecto BROWNFIELD. Repo raíz: `/home/javi/futmondo-analytics`
> (repo único, workspace root). Intent activo: analizar arquitectura/código,
> seguridad, fiabilidad, rendimiento/coste y calidad de ingeniería.
> Los nombres de fichero, identificadores y tokens de código se mantienen literales.

## Developer Code Scan Results

Aplicación web multi-usuario (PWA) de análisis de fantasy football (Futmondo).
Arquitectura de 3 componentes desplegables: frontend Angular 22 (`angular-app/`),
backend FastAPI/Python 3.12 (`backend/`) y un proxy nginx (`proxy/`, solo local),
más un proceso cron one-shot (`cron/`) reutilizando la imagen del backend.
Persistencia en Neon PostgreSQL (con capa de abstracción que también soporta
SQLite y Turso/libSQL). Integraciones externas: API Futmondo (`requests`) y API
no oficial de Sofascore (`curl_cffi` con `impersonate="chrome"` para evadir el
fingerprinting TLS).

### Scan Coverage

- **Analyzed deeply**:
  - `./` (raíz: `README.md`, `docker-compose.yml`, `.env.example`, `.gitignore`)
  - `backend/` (`Dockerfile`, `requirements.txt`, `entrypoint.sh`, `run.py`, `pytest.ini`, `conftest.py`, `ruff.toml`, `fly.toml`, `nixpacks.toml`)
  - `backend/app/main.py`
  - `backend/app/core/config.py`, `backend/app/core/constants.py`
  - `backend/app/auth/` (`routes.py`, `jwt_utils.py`, `token_store.py`, `dependencies.py`, `session_store.py`, `models.py`)
  - `backend/app/services/db_connection.py`, `backend/app/services/futmondo_client.py`, `backend/app/services/sofascore_client.py`, `backend/app/services/task_manager.py`
  - `backend/app/api/v1/endpoints/` (deep: `sync.py`, `sofascore_sync.py`, `market.py`, `reset_db.py`, `_helpers.py`; listado completo de los 23 endpoints)
  - `backend/tests/` (los 6 ficheros de test)
  - `backend/scripts/sync_data.py` (cron multi-championship), `backend/scripts/sync_sofascore_local.py` (skim del header)
  - `angular-app/` (`package.json`, `angular.json`, `karma.conf.js`, `eslint.config.js`, `nginx.prod.conf`, `fly.toml`)
  - `angular-app/src/app/core/` (`interceptors/auth.interceptor.ts`, `services/auth.service.ts`, guards)
  - `.github/workflows/` (`ci.yml`, `fly-deploy.yml`, `daily-sync.yml`, `sofascore-sync.yml`)
  - `proxy/nginx.conf`, `cron/fly.toml`
- **Skimmed only**:
  - `backend/app/services/data_manager_v2.py` (166 KB), `backend/app/services/data_sync_service.py` (84 KB), `backend/app/services/assistant_service.py` (51 KB), `backend/app/services/analytics_service.py` (34 KB), `backend/app/services/photo_service.py` (23 KB) — capa de datos/lógica pesada; conocida por interfaz y llamadas desde endpoints/sync, no leída línea a línea.
  - `angular-app/src/app/features/**` (17 features Angular) — inventariadas a nivel de directorio/fichero, no leídas en profundidad.
  - `backend/scripts/migrate_to_turso.py`, `migrate_data_to_turso.py`, `fetch_user_finances_data.py`, `export_user_transactions.py` (scripts de migración/util heredados).
  - `docs/**` (documentación de contexto y planes previos).

### Packages Found

- **angular-app** — application — TypeScript/Angular 22 — PWA frontend (SPA + service worker), Material 22, Chart.js, chat con marked. `package.json` v2.1.7.
- **backend** — application — Python 3.12 — API FastAPI, capa de servicios (sync, analytics, clientes externos, asistente IA), auth JWT. Sin `pyproject.toml`/`setup.py`: dependencias en `requirements.txt`.
- **backend/scripts** — scripts — Python — jobs one-shot: `sync_data.py` (sync Futmondo multi-championship, entrypoint del cron), `sync_sofascore_local.py` (batch Sofascore), migraciones a Turso, exportadores.
- **cron** — deployable — Fly.io app `futmondo-cron` — reutiliza `backend/Dockerfile`; proceso `python scripts/sync_data.py`.
- **proxy** — config — nginx (solo docker-compose local); en producción el proxy vive dentro de la imagen del frontend (`angular-app/nginx.prod.conf`).

### Build System

- **Type**: multi-build. Backend: pip + Docker (`python:3.12-slim`). Frontend: npm (`npm@11.12.1`) + Angular CLI 22 (`@angular/build:application`). Orquestación local: Docker Compose. Despliegue: Fly.io (`flyctl deploy` por app).
- **Config Files**: `backend/requirements.txt`, `backend/Dockerfile`, `backend/nixpacks.toml` (residuo Railway), `backend/fly.toml`, `backend/pytest.ini`, `backend/ruff.toml`, `angular-app/package.json`, `angular-app/angular.json`, `angular-app/karma.conf.js`, `angular-app/eslint.config.js`, `docker-compose.yml`, `cron/fly.toml`.
- **Build Dependencies**: frontend independiente del backend en build; en runtime el frontend proxya `/api` y `/auth` a `https://futmondo-api.fly.dev` (`angular-app/nginx.prod.conf`). Compose: `proxy` depende de `backend` (healthy) + `frontend`; `frontend` depende de `backend` (healthy).

### APIs Discovered

- **REST (FastAPI)** — `backend/app/main.py` — 23 routers montados bajo `/api/v1/*` + router de auth bajo `/auth/*`. Endpoints notables:
  - `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout` (`backend/app/auth/routes.py`) — login valida credenciales contra Futmondo, emite JWT access (60 min, en memoria) + refresh (30 días, cookie HttpOnly `futmondo_refresh_token`, `path=/auth`, `samesite=lax`, `secure` por `COOKIE_SECURE`).
  - `POST /api/v1/sync/trigger` → `GET /api/v1/sync/task/{task_id}` — sync asíncrona por hilo en background + polling (`sync.py` + `task_manager.py`). Pasos ejecutados en `_run_sync_in_background`: players, transactions, clauses, punishments_bonuses, dream_teams, player_performance, rosters, team_standings, match_odds, prizes, phantoms (11 pasos; los 2 últimos "non-critical" con try/except).
  - `POST /api/v1/sync/sofascore` (`sofascore_sync.py`) — DELETE total de `sofascore_cache` seguido de re-poblado jugador a jugador vía Sofascore.
  - `POST /api/v1/market/bid`, `/cancelbid` (`market.py`) — proxy de pujas a `/1/market/bid` de Futmondo; `price` como query param entero.
  - `POST /api/v1/database/reset`, `POST /api/v1/database/populate` (`reset_db.py`) — destructivos; protegidos tras `ENABLE_DB_ADMIN` (404 por defecto).
  - `GET /api/v1/photos/{player_id}` (`main.py`) — servido sin auth (path fuera de `/api/v1`? — está bajo `/api/v1/photos` y NO en `AUTH_EXCLUDED_PATHS`; ver deuda técnica).
  - `POST /api/v1/assistant/*` — chat IA (Gemini/Groq), persistencia en `assistant_conversations`.
- **API externa consumida — Futmondo** — `backend/app/services/futmondo_client.py` — cliente `requests.Session`; endpoints versionados heterogéneos (`/5/login/with_mail`, `/2/user/activechampionships`, `/1/market/players`, `/1/player/summary`, etc.); patrón `{header:{token,userid}, query:{...}, answer:{}}`. Timeouts 10-15 s. Token de sesión Futmondo en memoria por usuario.
- **API externa consumida — Sofascore** — `backend/app/services/sofascore_client.py` — `curl_cffi` `impersonate="chrome"`; throttle 750 ms; `BASE_URL` hardcodeado; sin API key (API no oficial, riesgo de baneo de IP — exit code 2 tratado en `sofascore-sync.yml`).

### Frameworks & Libraries

- **FastAPI** — `>=0.104.0` — framework API backend.
- **uvicorn[standard]** — `>=0.24.0` — servidor ASGI.
- **pydantic** — `>=2.5.0` — modelos/validación.
- **PyJWT** — `==2.9.0` — firma/verificación JWT (HS256).
- **psycopg2-binary** — `>=2.9.9` — PostgreSQL (pool `ThreadedConnectionPool` 5-20).
- **curl_cffi** — `>=0.16.0` — cliente Sofascore con impersonación TLS.
- **libsql-experimental** — `==0.0.55` — backend Turso/libSQL (embedded replica).
- **requests** — `>=2.31.0` — cliente Futmondo.
- **google-genai** — `==1.14.0`, **groq** — `==0.25.0` — asistente IA (Gemini + fallback Groq).
- **pytest / pytest-cov / httpx** — testing backend (httpx requerido por `TestClient`).
- **Angular** — `^22.1.0` (core, material, cdk, router, forms, service-worker), **chart.js** `^4.5.1` + **ng2-charts** `^10.0.0`, **marked** `^18.0.11`, **rxjs** `~7.8.0`, **typescript** `~6.0.2`. Test: Karma + Jasmine.

### Test Coverage

- **Test Directories**: `backend/tests/` (6 ficheros); frontend: tests dispersos junto al código (1 solo `.spec.ts`).
- **Test Frameworks**: pytest (backend), Karma + Jasmine (frontend).
- **Coverage Config**: backend `--cov=app` disponible pero SIN piso bloqueante (`pytest.ini`: "sin piso fijo/bloqueante todavía"). Frontend `karma-coverage` configurado (report html + text-summary), sin umbral.
- Backend tests presentes: `test_analytics_service.py` (con fakes de DataManager), `test_auth_characterization.py`, `test_db_admin_guard.py`, `test_jwt_startup.py`, `test_db_engine_characterization.py`, `test_finance_characterization.py` — suite de **caracterización** (congela comportamiento actual, metodología `custom` characterization-first, ver `conftest.py`).
- **Frontend**: solo `angular-app/src/app/core/interceptors/auth.interceptor.spec.ts` (1 test). `angular.json` configura `skipTests: true` en todos los schematics → los componentes/servicios nuevos nacen sin test. **Cobertura frontend efectivamente ~0** pese a que `ci.yml` marca `ng test` como bloqueante.

### Code Quality Indicators

- **Linting**: backend ruff (`ruff.toml`, `select=["E","F","I"]`, con `E501/E402/E722` ignorados en base heredada; modo ADVISORY en CI). Frontend ESLint (`eslint.config.js`, `ng lint` ADVISORY en CI). Formato: Prettier (`.prettierrc`) + ruff format.
- **CI/CD**: 4 workflows GitHub Actions. `ci.yml` (PR→main): gitleaks BLOQUEANTE, pytest BLOQUEANTE, `ng test` BLOQUEANTE; ruff/ESLint/pip-audit/npm audit ADVISORY. `fly-deploy.yml` (push→main): job `verify` (pytest + ng test) → deploy backend → deploy frontend → smoke test `/health`. `daily-sync.yml` y `sofascore-sync.yml`: crons one-shot en Fly con polling de estado y verificación de exit code. Docs de proceso en `docs/PR-GATE.md`, `docs/ROLLBACK.md`.
- **Documentation**: `README.md` completo, `docs/` rico (PROJECT_CONTEXT, planes de migración, DEPLOY, ROLLBACK). Comentarios en castellano con referencias a NFRs/FRs (endurecimiento previo ya aplicado).
- **Estructura**: backend por capas (api/services/auth/core/models) razonable; endpoints por dominio. Frontend por feature (17 features standalone) + core (services/interceptors/guards) + shared. Buena organización general.

### Technical Debt Signals

- **Ficheros gigantes (god files)**: `data_manager_v2.py` (166 KB / ~4.700 líneas), `data_sync_service.py` (84 KB), `assistant_service.py` (51 KB), `analytics_service.py` (34 KB). Superan con creces el objetivo de <300 líneas; concentran riesgo de cambio y son intestables sin fakes.
- **Manejo de errores demasiado amplio**: 159 `except Exception` y 6 `except:` desnudos en `backend/app`. Múltiples `except Exception: pass` silenciosos (p.ej. migraciones en `token_store.py:init_auth_tables`, `_ensure_conversations_table` en `assistant.py`, `_auto_detect_championships` en `auth/routes.py`). Enmascaran fallos.
- **Estado en memoria no durable**: `TaskManager` y `SessionStore` son singletons in-memory (`task_manager.py`, `session_store.py`). En Fly con `auto_stop_machines`/reinicios, cualquier restart pierde tareas de sync en curso y sesiones Futmondo → el usuario recibe 403 "sesión expirada" (`_helpers.get_user_futmondo_client`) y las tareas quedan huérfanas. Además `SessionStore` guarda email+password en claro en memoria.
- **Resto de config heredada / entornos mezclados**: `config.py` soporta 3 backends de BD (SQLite/Turso/PostgreSQL) con ramas muertas para el despliegue actual (Neon). `nixpacks.toml` (Railway) y scripts `migrate_to_turso.py` son residuo de plataformas anteriores. `constants.py`/`CHAMPIONSHIP_ID` con default hardcodeado y `LEAGUE_ID` fijo.
- **`docker-compose.yml` fija `SSL_VERIFY=0`** en el servicio backend (entorno local) — patrón de deshabilitar verificación TLS; confirmar que NO se propaga a producción.
- **Bug potencial de expiración de refresh token**: `token_store.is_refresh_token_valid` tiene una expresión condicional ambigua (ternario sin paréntesis mezclando naive/aware datetimes) que puede evaluar mal la expiración.
- **Doble montaje de rutas**: `matchdays` se monta bajo `/api/v1/matchdays` y también `/v1/matchdays` ("to avoid redirect loops") — superficie duplicada.
- **`entrypoint.sh`** arranca `cron` + uvicorn pero el `Dockerfile` usa `CMD uvicorn ...` (entrypoint.sh no referenciado) — script muerto/confuso.
- **`ARG`/imágenes**: `42874.jpg`, `IMG_9904.PNG`, dirs `stitch_*` y `:Zone.Identifier` en la raíz del repo — artefactos de diseño/Windows versionados innecesariamente.

## Handoff Summary

- **Intent-relevant finding**: La **sync asíncrona de 11 pasos** (`backend/app/api/v1/endpoints/sync.py::_run_sync_in_background`) es el punto más frágil de fiabilidad: corre en un `threading.Thread(daemon=True)` con estado SOLO en memoria (`task_manager.py`), sin persistencia ni idempotencia. Un reinicio de la máquina Fly (política de restart/auto-stop) durante el sync pierde la tarea y la sesión Futmondo del usuario (`session_store.py`), y `TaskManager.get_active_task` marca como fallidas las tareas >10 min. Los pasos `prizes` y `phantoms` capturan excepciones y las degradan a "non-critical", ocultando fallos parciales. La integración Sofascore (`sofascore_sync.py`) hace `DELETE FROM sofascore_cache` ANTES de repoblar → si el repoblado falla a mitad (baneo de IP de Sofascore, exit code 2 en `sofascore-sync.yml`), la caché queda vacía o incompleta (borrado no transaccional respecto al fetch externo).
- **Intent-relevant finding (seguridad)**: Endurecimiento ya presente y correcto (JWT fail-fast `config.py::resolve_jwt_secret`, endpoints destructivos tras `ENABLE_DB_ADMIN` con 404, refresh HttpOnly, CORS con whitelist, gitleaks bloqueante). Puntos a revisar: (1) `session_store.py` guarda contraseñas Futmondo en claro en memoria; (2) `docker-compose.yml` fija `SSL_VERIFY=0`; (3) `GET /api/v1/photos/{player_id}` NO figura en `AUTH_EXCLUDED_PATHS` pero conviene confirmar su exposición real; (4) `market.py::place_bid` recibe `price` sin validación de rango/positividad en el backend (solo el frontend valida min/max).
- **Intent-relevant finding (calidad/CI)**: Asimetría fuerte de tests — backend con 6 ficheros de caracterización y `--cov` (sin piso), frontend con **un único `.spec.ts`** y `skipTests: true` global en `angular.json`, pese a que `ci.yml` marca `ng test` como bloqueante (el gate pasa con cobertura casi nula). ruff/ESLint/pip-audit/npm audit son ADVISORY (no bloquean) por decisión escalonada documentada (R-05).
- **Risks / follow-up**: (1) `data_manager_v2.py` (166 KB) y `data_sync_service.py` (84 KB) son god-files intestables sin fakes; refactor de alto riesgo. (2) Config multi-backend de BD (SQLite/Turso/PostgreSQL) con ramas muertas y residuo Railway (`nixpacks.toml`) → confirmar Neon como único backend y podar. (3) 159 `except Exception` + 6 bare-except silencian errores; priorizar los `except: pass` en arranque/migraciones. (4) Coste 0€ es una regla de proyecto vigente (`project.md`): Fly `min_machines_running=1` (256 MB) + crons one-shot; cualquier propuesta debe respetar tiers gratuitos (Neon free / Fly free allowance / GitHub Actions free). (5) Posible bug de comparación de expiración en `token_store.is_refresh_token_valid` (ternario ambiguo naive/aware) — validar con test dedicado.
