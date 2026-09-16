# Code Structure — Futmondo Analytics

> Artefacto CodeKB (architect). Base: `developer-scan.md`. Store STALE tras FOCUSED SCAN del backend `backend/`. La prosa del frontend se preserva del análisis previo.

## Organización de alto nivel (raíz del repo)

```
futmondo-analytics/
├── angular-app/   # Frontend Angular 22 (PWA)
├── backend/       # Backend FastAPI (Python 3.12)
├── cron/          # Proceso worker one-shot (reutiliza backend/Dockerfile)
├── proxy/         # nginx reverse proxy (local)
├── docs/          # Documentación y backlogs
├── .github/       # workflows de CI/CD
├── stitch_*       # mockups de diseño estáticos (fuera del código de app)
└── docker-compose.yml
```

## `backend/` (servicio web, Python 3.12) — verificado en profundidad este run

- `app/main.py` — montaje de routers (`app.api.v1.endpoints.*` + `app.auth.routes`), `AuthMiddleware` (whitelist de rutas públicas, inyecta `request.state.user`), endpoints raíz/`/health`/fotos, CORS.
- `app/auth/` — módulo de autenticación (verificado):
  - `routes.py` — `POST /auth/login` (valida contra Futmondo, upsert usuario, emite JWT, cookie HttpOnly, `store_session`, auto-detección de campeonatos), `POST /auth/refresh` (verifica refresh token, emite access token; **no** reconstruye sesión Futmondo), `POST /auth/logout` (revoca refresh, elimina sesión, limpia cookie).
  - `session_store.py` — `SessionStore` singleton de proceso: `dict[str, UserSession]` con `threading.Lock` global + locks por usuario; `UserSession` guarda `email`/`password` **en claro**, `token`, `user_id`, TTL 12h.
  - `token_store.py` — gestiona `app_users`, `refresh_tokens` (hash SHA-256, `revoked`, `expires_at`) y `user_championships`; `init_auth_tables()` con `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE` en `try/except`.
  - `jwt_utils.py` — firma/verificación JWT HS256 (PyJWT); guard de arranque endurecido (cubierto por `test_jwt_startup.py`).
  - `dependencies.py` — dependencias FastAPI de auth.
  - `models.py` — modelos Pydantic del área auth.
- `app/api/v1/endpoints/` — **~24 routers** (uno por dominio). Verificados en profundidad:
  - `sync.py` — `POST /trigger` (crea `Task` en `TaskManager`, lanza `threading.Thread` daemon, 409 si hay tarea activa, usa `get_user_futmondo_client(request)`), `GET /task/{task_id}` (polling desde memoria), `GET /status`, `GET /last-sync` (metadatos desde BD `sync_metadata`).
  - `_helpers.py` — `get_user_futmondo_client(request)`: reconstruye/obtiene el cliente Futmondo desde la sesión en memoria; devuelve **403** si la sesión no existe (p. ej. tras reinicio).
  - Resto (skimmed): `market.py`, `balances.py`, `player_finances.py`, `analytics.py`, `roster.py`, `transactions.py`, `favorites.py`, `clausulable_players.py`, `sofascore_sync.py`, `user.py`, `reset_db.py`, etc.
- `app/services/` — **12 módulos** de servicio. Verificados: `task_manager.py` (`TaskManager` singleton de proceso, `dict[str, Task]`, cap 20, stale 10 min), `db_connection.py` (abstractor multi-backend SQLite/PostgreSQL-Neon/Turso, SQL directo con cursores, `ThreadedConnectionPool`, adaptación `?`↔`%s`), `futmondo_client.py` (cabecera: constructor, `login`, gestión de `token`/`user_id`/`session` con `requests.Session`). Skimmed: `data_manager_v2.py` (~166 KB), `data_sync_service.py` (~84 KB), `analytics_service.py`, `assistant_service.py`, `sofascore_client.py`, `photo_service.py`, `futmondo_service.py`, `data_initializer*.py`.
- `app/core/` — `config.py` (configuración/settings) y constantes.
- `app/models/` — modelos de datos ligeros (`models.py`).
- `scripts/` — `init_db.py` (verificado) y scripts de sync/migración puntuales (`sync_data.py`, usado por cron; skimmed).
- `tests/` — 7 ficheros `pytest`, `conftest.py` (provee `clean_jwt_env`, fija `sys.path`).
- Config: `requirements.txt`, `pytest.ini`, `ruff.toml`, `nixpacks.toml` (heredado, Python 3.11), `Dockerfile` (Python 3.12), `fly.toml` (región `cdg`), `entrypoint.sh`, `run.py`, `conftest.py`.

**Patrones de código (backend)**: router-per-domain montados en `main.py`; `AuthMiddleware` con whitelist de rutas públicas; clientes de integración dedicados (patrón adapter/ACL); singletons de proceso para estado transitorio (`SessionStore`, `TaskManager`); acceso a datos por SQL directo (sin ORM) con adaptación manual de dialecto; imports diferidos dentro de funciones (patrón repetido, incl. `__import__` dinámico de `get_db` en `refresh`); tests de caracterización sobre comportamiento existente.

## `angular-app/` (aplicación, TypeScript) — preservado del análisis previo

Estructura por capas Angular standalone (sin NgModules):

- `src/main.ts` — arranque: `bootstrapApplication(App, appConfig)`.
- `src/app/app.config.ts` — `ApplicationConfig`: `provideAnimationsAsync()`, `provideCharts(withDefaultRegisterables())`, `withPreloading(PreloadAllModules)`.
- `src/app/app.ts` — componente root `App`: shell de Material + CDK; incluye `AssistantFabComponent`.
- `src/app/app.routes.ts` — routing raíz 100 % lazy.
- `src/app/features/` — **17 features** con `*.routes.ts` lazy. Consumidores de gráficos: `features/evolution`, `features/stats`.
- `src/app/core/` — `services`, `interceptors` (`auth.interceptor.ts`), `guards`, `models`.
- `src/app/shared/` — `components` (incl. `assistant-fab.component.ts` → `assistant-chat.component.ts`, import estático de `marked`), `pipes`, `utils`, `styles`.
- Config: `angular.json` (builder `@angular/build:application`), `package.json`, `tsconfig*.json`, `eslint.config.js`; PWA/serve: `ngsw-config.json`, `nginx*.conf`, `Dockerfile`, `fly.toml`.

**Patrones de código (frontend)**: standalone components + signals; `ChangeDetectionStrategy.OnPush`; providers centralizados; interceptor HTTP para auth; routing lazy por feature.

## `cron/` y `proxy/`

- `cron/fly.toml` — app `futmondo-cron`; reutiliza `backend/Dockerfile` y ejecuta `python scripts/sync_data.py` en máquina Fly efímera.
- `proxy/nginx.conf` — reverse proxy para enrutado local (docker-compose) hacia frontend y backend.

## Clasificación de ficheros

| Categoría | Ubicaciones |
|-----------|-------------|
| Código de aplicación (frontend) | `angular-app/src/app/**` |
| Código de servicio (backend) | `backend/app/**`, `backend/scripts/**` |
| Tests | `backend/tests/**`, `angular-app/src/app/**/*.spec.ts` |
| Config de build/CI | `*/package.json`, `*/angular.json`, `*/tsconfig*.json`, `backend/requirements.txt`, `*/Dockerfile`, `*/fly.toml`, `.github/workflows/*.yml`, `docker-compose.yml` |
| Config de lint/formato | `angular-app/eslint.config.js`, `backend/ruff.toml`, `.prettierrc`, `.editorconfig` |
| Infra de servido/PWA | `*/nginx*.conf`, `angular-app/ngsw-config.json` |
| Documentación | `README.md`, `angular-app/README.md`, `docs/**` |
| Assets de diseño (no-código) | `stitch_*` |

## Referencias cruzadas

- Inventario de componentes con responsabilidades y dependencias: `component-inventory.md`.
- Versiones de frameworks/librerías: `technology-stack.md`.
- Deuda de estado en memoria y seguridad: `code-quality-assessment.md`.
