# API Documentation — futmondo-analytics

## External / Internal API Surfaces

Las APIs HTTP se montan en `backend/app/main.py` bajo los prefijos `/api/v1/*` y
`/auth/*`. Todas las `/api/v1/*` exigen **Bearer JWT** vía `AuthMiddleware`.
Excluidas de auth: `/auth/login|refresh|logout`, `/health`, `/`, `/docs`,
`/openapi.json`, `/redoc` y el mount público `/static/photos/*`.

### Auth endpoints (`/auth/*`)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/auth/login` | POST | Login con credenciales Futmondo; valida contra API Futmondo y emite JWT. |
| `/auth/refresh` | POST | Renueva access token desde refresh cookie HttpOnly. |
| `/auth/logout` | POST | Revoca la sesión. |

- **Access token** (1h): en memoria del navegador. **Refresh token** (30 días):
  cookie HttpOnly.

### API v1 endpoints (`/api/v1/*`, Bearer JWT)

Relevantes al intent (Calculadora / finanzas):

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/player-finances/` | GET | **Cálculo de finanzas por usuario**: agrega `initial_budget + transaction_profit + ranking + mvp + dream_team + points + net_adjustment`; lee el dinero de premio desde `team_prizes` (única fuente de verdad). Consumido por la pantalla `finances`, **no** por la Calculadora. |
| `/api/v1/roster/sell` | POST | Alta/baja al mercado; **consumido por la Calculadora** (`sellPlayers()`). |
| `/api/v1/roster/*` | GET/POST | Plantilla y acciones de roster (`getMyRoster`, `getOnSale`). |
| `/api/v1/market/today` | GET | Balance + pujas activas (`active_bids_total`, `active_bids_count`); **consumido por la Calculadora**. |

Resto de routers (inventariados por nombre/tamaño): `matchdays`, `initialize`,
`database` (reset), `statistics`, `user-stats`, `clausulable-players`, `sync`,
`analytics`, `balances`, `championships`, `phantoms`, `market`, `favorites`,
`transactions`, `sofascore` (sync + detail), `user`, `assistant`.

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/sync/trigger` | POST | Lanza sync async; devuelve `task_id`. |
| `/api/v1/sync/task/{id}` | GET | Polling de progreso del sync (11 pasos). |
| `/api/v1/photos/{player_id}` | GET | Autenticado; redirige 302 al mount público `/static/photos/*`. |

### Internal contracts (dominio)

- `prizes/calculator.py:calculate_round_prizes()` — **función pura, sin I/O**;
  reglas BR1.1-BR3.2 (points siempre; ranking/MVP/dream-team sólo si la ronda está
  cerrada; split proporcional flop/top; empates compartidos).
- `prizes/team_prizes_writer.py:replace_team_prizes()` — **reemplazo transaccional
  atómico** de `team_prizes`.
- Puertos DDD con inversión de dependencias: `analytics/domain/ports.py`,
  `assistant/domain/ports.py`.

### Outbound integrations

| Integración | Cliente | Mecanismo |
|-------------|---------|-----------|
| API Futmondo | `futmondo_client.py` | HTTP, auth por usuario; credenciales cifradas. |
| API Sofascore | `sofascore_client.py` | HTTP vía `curl_cffi`. |
| Gemini / Groq | asistente IA | SDK `google-genai` / `groq`. |

## Contracts & Failure Behaviour

- Auth: `/api/v1/*` responde 401 sin Bearer válido (excluidos arriba). Las fotos
  autenticadas redirigen 302 al mount público.
- Sync: estado por paso `StepStatus` (OK / DEGRADED); un paso recuperable degrada y
  continúa, uno fatal aborta sin dejar datos a medias (regla afirmada).
- Dinero de premio: contrato de consistencia — `team_prizes` es única fuente de
  verdad y se repuebla por reemplazo atómico; ver `architecture.md` (Interaction
  Diagrams).

## Sources

- `developer-scan.md`: APIs Discovered, Handoff Summary.
- `README.md`: tabla de endpoints principales, modelo de auth.
