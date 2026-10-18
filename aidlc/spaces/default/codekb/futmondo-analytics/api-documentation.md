# API Documentation — futmondo-analytics

## Superficie REST interna (FastAPI)

- **Total**: **59 operaciones** de ruta en `backend/app/api/v1/endpoints/`
  (22 ficheros) + `backend/app/auth/routes.py`.
  - 38 `@router.get`, 18 `@router.post`, 2 `@router.delete`, 1 `@router.put`.
- **Prefijos montados en `main.py`** bajo `/api/v1`:
  `matchdays`, `initialize`, `database`, `statistics`, `player-finances`,
  `user-stats`, `clausulable-players`, `sync`, `analytics`, `market`, `roster`,
  `favorites`, `transactions`, `sofascore`, `user`, `assistant`, más
  `championships` y `phantoms` directamente bajo `/api/v1`, y
  `/api/v1/photos/{player_id}`.

### Endpoints principales (muestreo representativo)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/auth/login` | POST | Login con credenciales Futmondo |
| `/auth/refresh` | POST | Renovar access token (cookie HttpOnly) |
| `/auth/logout` | POST | Revocar sesión |
| `/api/v1/user/me` | GET | Info del usuario logado |
| `/api/v1/user/championships` | GET/POST/DELETE | CRUD campeonatos del usuario |
| `/api/v1/championships` | GET | Lista campeonatos del usuario |
| `/api/v1/analytics/balances` | GET | Presupuestos por equipo |
| `/api/v1/market/today` | GET | Mercado + puja sugerida + Sofascore |
| `/api/v1/market/bid` | POST | Pujar por jugador |
| `/api/v1/sync/trigger` | POST | Lanzar sync async (devuelve `task_id`) |
| `/api/v1/sync/task/{id}` | GET | Polling de progreso del sync |
| `/api/v1/player-finances/` | GET | Finanzas por usuario |
| `/api/v1/photos/{player_id}` | GET | Servir foto de jugador |

## Autenticación y contrato de seguridad

- **Auth sin prefijo `/api/v1`**: `/auth/login`, `/auth/refresh`, `/auth/logout`.
- **Modelo de token**: JWT **access** (1h, en memoria del navegador) + **refresh**
  (30d, cookie **HttpOnly**).
- **`AuthMiddleware`** (Starlette `BaseHTTPMiddleware`) exige `Bearer` en todo
  `/api/v1/*` salvo `AUTH_EXCLUDED_PATHS`: `/health`, `/`, `/docs`,
  `/openapi.json`, `/redoc` y las rutas `/auth/*`.
- **Health público**: `/health` (HTTP 200), consumido por el smoke test del
  deploy.

## APIs externas consumidas

- **API Futmondo** — `backend/app/services/futmondo_client.py` — validación de
  credenciales y datos de campeonato.
- **API Sofascore** — `backend/app/services/sofascore_client.py` vía
  **`curl_cffi`** — ratings/odds.
- **LLM** — Gemini (`google-genai`) con fallback a **Groq**, en
  `backend/app/services/assistant/infrastructure/llm_adapter.py`.

## Cliente Angular → API

- **12 servicios** en `core/services/*.service.ts` (`auth`, `analytics`,
  `budget`, `stats`, `evolution`, `roster`, `favorites`, `sync`, `assistant`,
  `championship`, …) sobre `HttpClient`.
- **`authInterceptor`**: inyecta `Bearer`, maneja refresh en 401 (cola con
  `BehaviorSubject`) y fuerza logout en 403.
- La migración a app nativa consumiría **este mismo contrato** `/api/v1/*` +
  `/auth/*` sin cambios de backend (ver `architecture.md`). Nota: el refresh
  cookie-based + `withCredentials` es el riesgo de portabilidad nativa #1 (ver
  `code-quality-assessment.md`).
