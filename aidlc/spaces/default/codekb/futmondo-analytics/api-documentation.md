# API Documentation — Futmondo Analytics

> Artefacto CodeKB (architect). Base: `developer-scan.md` (`backend/app/main.py`, `app/auth/routes.py`, `app/api/v1/endpoints/sync.py`). Store STALE. El FOCUSED SCAN de este run reanalizó en profundidad las superficies **auth** y **sync**; el resto de la superficie API se preserva del análisis previo.

## Superficie de API interna (FastAPI)

Aplicación `app.main:app`. Dos superficies: **auth sin prefijo** y **API v1 protegida**.

### Autenticación — `/auth/*` (sin prefijo `/api/v1`) — verificado este run

Definida en `app/auth/routes.py`. Rutas excluidas de `AuthMiddleware`.

| Endpoint | Método | Contrato / comportamiento |
|----------|--------|---------------------------|
| `/auth/login` | POST | Valida credenciales contra Futmondo (`FutmondoClient.login`); upsert de `app_users`; emite access JWT (body) + refresh JWT (cookie HttpOnly `futmondo_refresh_token`); guarda la sesión Futmondo en memoria (`store_session`, con `email`/`password` en claro, TTL 12h); auto-detecta campeonatos. |
| `/auth/refresh` | POST | Verifica firma + no-revocado del refresh token (cookie) contra `refresh_tokens`; emite nuevo access token. **No reconstruye la sesión Futmondo en memoria** → tras un reinicio el JWT es válido pero los endpoints que necesitan el cliente Futmondo fallan con 403. |
| `/auth/logout` | POST | Revoca el refresh token (`revoked`), elimina la sesión en memoria y limpia la cookie. |

### Middleware de auth (`app/main.py` `AuthMiddleware`)

- Exige `Authorization: Bearer <access token>` en `/api/v1/*`.
- Rutas públicas (excluidas): `/auth/login`, `/auth/refresh`, `/auth/logout`, `/health`, `/`, `/docs`, `/openapi.json`, `/redoc`.
- Inyecta `request.state.user` para los handlers protegidos.

### API v1 — `/api/v1/*` (protegida por `AuthMiddleware`, Bearer JWT)

Routers montados por dominio en `main.py`: `matchdays`, `initialize`, `database` (reset_db), `statistics`, `player-finances`, `user-stats`, `clausulable-players`, `sync`, `analytics` (+ `balances`, `phantoms`), `championships`, `market`, `roster`, `favorites`, `transactions`, `sofascore` (sync + detail), `user`, `assistant`.

#### Área sync — `/api/v1/sync/*` (verificado este run)

| Endpoint | Método | Contrato / comportamiento |
|----------|--------|---------------------------|
| `/api/v1/sync/trigger` | POST | Lanza sync asíncrono en `threading.Thread` (daemon); crea un `Task` en `TaskManager` (memoria); responde **409** si ya hay una tarea activa; usa `get_user_futmondo_client(request)` (puede devolver 403 si la sesión no existe). Devuelve `task_id`. |
| `/api/v1/sync/task/{task_id}` | GET | Polling del estado/progreso de la tarea, leído desde memoria del `TaskManager` (se pierde al reiniciar). |
| `/api/v1/sync/status` | GET | Metadatos de sync desde BD (`sync_metadata`). |
| `/api/v1/sync/last-sync` | GET | Última sync desde BD (`sync_metadata`). |

#### Otros endpoints representativos (evidencia previa + README)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/user/me` | GET | Info del usuario logado |
| `/api/v1/user/championships` | GET/POST/DELETE | CRUD de campeonatos del usuario |
| `/api/v1/championships` | GET | Lista campeonatos del usuario |
| `/api/v1/analytics/balances` | GET | Presupuestos por equipo |
| `/api/v1/market/today` | GET | Mercado + puja sugerida + Sofascore |
| `/api/v1/market/bid` | POST | Pujar por jugador (validación min/max) |
| `/api/v1/player-finances/` | GET | Finanzas por usuario |

### Endpoints no-API / infraestructura

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Raíz |
| `/health` | GET | Healthcheck (usado por smoke test y healthchecks Fly) |
| `/api/v1/photos/{player_id}` | GET | Fotos de jugador con fallback SVG |
| `/static/photos` | — | Montaje estático de fotos |

### CORS

Whitelist: `https://futmondo-app.fly.dev`, `http://futmondo.localhost`, `http://localhost:4200`, `http://localhost:3000` (más `EXTRA_CORS_ORIGIN`).

### Contrato de autenticación

Todos los `/api/v1/*` requieren `Authorization: Bearer <access token>`. El access token vive en memoria del navegador (1h); el refresh token (30 días) en cookie HttpOnly. El backend mantiene una sesión Futmondo por usuario (TTL ~12h) **en memoria de proceso**; hoy no se reconstruye tras un reinicio (deuda del intent activo, ver `architecture.md`).

## API externa consumida (backend como cliente)

| Integración | Cliente | Mecanismo |
|-------------|---------|-----------|
| API Futmondo (`https://api.futmondo.com`) | `backend/app/services/futmondo_client.py` | HTTP (`requests.Session`) con `token`+`userid` del usuario en el cuerpo. Endpoints: `POST /5/login/with_mail`, `POST /2/user/activechampionships`, `POST /2/championship/teams`, y endpoints de datos (standings, roster, transacciones) usados por `data_sync_service`. |
| API Sofascore | `backend/app/services/sofascore_client.py` | HTTP vía `curl_cffi` (impersonación de navegador) |
| IA (assistant) | `backend/app/services/assistant_service.py` | SDKs `google-genai`, `groq` |

## Referencias cruzadas

- Flujos de negocio (login, refresh, sync) como diagramas de secuencia: `architecture.md` → **Interaction Diagrams**.
- Responsabilidades de cada router/servicio: `component-inventory.md`.
