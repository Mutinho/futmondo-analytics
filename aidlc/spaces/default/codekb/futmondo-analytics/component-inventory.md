# Component Inventory — Futmondo Analytics

## Backend (FastAPI)

| Componente | Fichero | Responsabilidad | Dependencias clave |
|---|---|---|---|
| FastAPI app + AuthMiddleware | `app/main.py` | Monta CORS, middleware de auth sobre `/api/v1/*`, routers, fotos estáticas, `/health` | `jwt_utils.verify_token`, routers, `token_store.init_auth_tables` |
| Auth routes | `app/auth/routes.py` | `/auth/login`, `/auth/refresh`, `/auth/logout`; set/clear cookie `HttpOnly`; auto-detección de campeonatos | `FutmondoClient`, `jwt_utils`, `token_store`, `session_store`, `session_service`, `SessionRepository` |
| JWT utils | `app/auth/jwt_utils.py` | Crear/verificar access (60 min) y refresh (30 días) HS256; `hash_token` | `PyJWT`, `config.JWT_SECRET` |
| Auth dependency | `app/auth/dependencies.py` | `get_current_user(request)` desde header Bearer | `jwt_utils.verify_token` |
| Token store | `app/auth/token_store.py` | Tablas `app_users`, `refresh_tokens`, `user_championships`; save/revoke/validate refresh; upsert/get user; migraciones idempotentes | `db_connection.get_db`, `psycopg2`/`sqlite3` |
| Session store (memoria) | `app/auth/session_store.py` | Caché por usuario de `FutmondoClient` (TTL 12h); **nunca** retiene password | `FutmondoClient`, `threading` |
| Auth models | `app/auth/models.py` | `LoginRequest`, `TokenResponse`, `Refresh*` (pydantic) | `pydantic` |
| Session service / repo | `app/services/session_service.py`, `app/stores/session_repository.py` | Sesión durable + rehidratación con handle cifrado | `credential_protection`, `config.FUTMONDO_CRED_KEY` |
| Credential protection | `app/security/credential_protection.py` | Cifra/descifra el handle de re-auth en reposo (sin password en claro) | `FUTMONDO_CRED_KEY` |
| Futmondo client | `app/services/futmondo_client.py` (~27 KB) | Cliente de la API Futmondo: `login()`, `_make_request`, errores tipados | `requests`, `integration_errors` |
| Sofascore client | `app/services/sofascore_client.py` (~16 KB) | Cliente de la API Sofascore (ratings) | `curl_cffi` (stack), `integration_errors` |
| Integration errors | `app/services/integration_errors.py` | Jerarquía tipada recoverable/fatal; constructor sin material de credencial (NFR3) | — |
| Task service / repo | `app/services/task_service.py`, `app/stores/task_repository.py` | Tareas de sync durables + barrido de interrumpidas al arranque | `db_connection` |
| Sync service | `app/services/data_sync_service.py` (~15 KB) | **God-file heredado (deuda, NO ampliar)**: orquestación de sync | — |
| Data manager | `app/services/data_manager_v2.py` (~33 KB) + `data_manager/` | **God-file heredado (deuda, NO ampliar)**; parte extraída a adapters DDD | — |
| Photo service | `app/services/photo_service.py` (~23 KB) | Descarga/servido de fotos de jugador | `requests` |
| Config | `app/core/config.py` | Env vars; `resolve_jwt_secret` (fail-fast NFR1.1); `FUTMONDO_CRED_KEY` | `python-dotenv` |
| DB connection | `app/services/db_connection.py` | Abstracción PostgreSQL/SQLite (`db_type`, `adapt_params`) | `psycopg2`, `sqlite3` |

## Frontend (Angular)

| Componente | Fichero | Responsabilidad | Relevancia F1 |
|---|---|---|---|
| AuthService | `src/app/core/services/auth.service.ts` | `login/refresh/logout/tryRecoverSession`; **access token en memoria** (`accessToken`), user en `localStorage` (no el token); refresh por cookie (`withCredentials`) | **Referencia directa del flujo que iOS debe replicar con Keychain** |
| authInterceptor | `src/app/core/interceptors/auth.interceptor.ts` | Añade `Authorization: Bearer`; `withCredentials` en `/auth/*`; reintento con refresh en `401`; logout en `403` | Modela el manejo de 401/refresh que el cliente nativo debe implementar |
| authGuard | `src/app/core/guards/auth.guard.ts` | `CanActivateFn`: recupera sesión al arrancar / redirige a `/login` | — |
| LoginComponent | `src/app/features/login/login.component.ts` | Formulario email/password (Material) → `AuthService.login` | **Referencia de UX de login para la pantalla nativa** |
| App config | `src/app/app.config.ts` | Registra `authInterceptor`, router con preloading, service worker | — |
| Feature services | `analytics/budget/stats/market/roster/sync/...service.ts` | Consumo de `/api/v1/*` | Consumidores del access token |
| Feature components | `features/{budget,market,finances,calculator,...}` | UI de cada funcionalidad | — |

## Modelo de datos de auth (tablas)

- `app_users(id PK, futmondo_email UNIQUE, futmondo_user_id, display_name, created_at, last_login)`
- `refresh_tokens(token_hash PK, user_id FK, expires_at, revoked, created_at)`
- `user_championships(user_id, championship_id, name, initial_budget, has_clauses, excluded_teams, money_per_point, money_per_ranking, dream_team_bonus, mvp_bonus, ranking_mode, users_to_rank, is_pro, futmondo_team_id, PK(user_id, championship_id))`

## Sources

- `backend/app/main.py`, `backend/app/auth/{routes,jwt_utils,dependencies,token_store,session_store,models}.py`
- `backend/app/services/{integration_errors,futmondo_client,session_store}.py`, `backend/app/core/config.py`
- `angular-app/src/app/core/services/auth.service.ts`
- `angular-app/src/app/core/interceptors/auth.interceptor.ts`
- `angular-app/src/app/core/guards/auth.guard.ts`
- `angular-app/src/app/features/login/login.component.ts`
- `angular-app/src/app/app.config.ts`

## Assumptions & Open Questions

- Tamaños de servicio indicados en KB desde el listado de directorio (bytes),
  no por conteo de líneas de cada fichero. `sofascore_client.py` usa `curl_cffi`
  según el stack del `README.md`/`requirements.txt`; no se abrió su cuerpo
  completo en este escaneo (sí `futmondo_client.py` y `integration_errors.py`).
