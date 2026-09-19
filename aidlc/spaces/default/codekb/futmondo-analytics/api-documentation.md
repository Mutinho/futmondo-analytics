# Documentación de APIs — futmondo-analytics

## Modelo de Autenticación

`AuthMiddleware` (en `backend/app/main.py`) protege todo `/api/v1/*` y `/auth/*` salvo las
rutas de `AUTH_EXCLUDED_PATHS`:

```
AUTH_EXCLUDED_PATHS = {"/auth/login","/auth/refresh","/auth/logout","/health","/","/docs","/openapi.json","/redoc"}
```

Las rutas protegidas exigen `Authorization: Bearer <access>`, verificado con
`verify_token(..., expected_type="access")`. Nota de superficie: `/static/photos/*`
(StaticFiles) NO empieza por `/api/v1` ni `/auth`, así que el middleware la deja pasar sin
auth; las redirecciones 302 del endpoint de fotos apuntan ahí.

## Cliente HTTP del Frontend (Angular 22)

El frontend consume la superficie backend mediante servicios `HttpClient` en
`angular-app/src/app/core/services/*.service.ts` (11 servicios: `analytics`, `assistant`,
`auth`, `budget`, `championship`, `evolution`, `favorites`, `roster`, `stats`, `sync`).
Todas las peticiones pasan por `core/interceptors/auth.interceptor.ts`, que implementa el
lado cliente del modelo de auth:

- Añade `Authorization: Bearer <access>` a las peticiones a `/api/*`.
- EXCLUYE `/auth/*` del Bearer y usa `withCredentials: true` para enviar la cookie
  `HttpOnly` de refresh.
- Ante `401`, ENCOLA las peticiones en vuelo mientras dispara un único refresh; al resolver,
  reintenta las encoladas con el nuevo token.
- Ante fallo de refresh o `403`, fuerza logout.

Este comportamiento está caracterizado por `auth.interceptor.spec.ts` (único contrato de
cliente hoy cubierto por test; ver `code-quality-assessment.md`). El resto de servicios
`core/services/*` NO tienen spec.

## Endpoints de Premios y Finanzas

Superficie de LECTURA sobre los premios ya persistidos en `team_prizes`. Ningún endpoint
recalcula: todos leen y suman lo que produjo `data_sync_service.sync_prizes()` (ver
`architecture.md`). Contratos observados:

| Método + Ruta | Handler | Auth | Descripción |
|---|---|---|---|
| `GET /api/v1/player-finances/` | `player_finances.get_player_finances` | Bearer | Finanzas agregadas por usuario. `total_money = initial_budget + points_money + transaction_profit + (dream_team + mvp) + ranking_money + net_adjustment`. Lee premios vía `dm.get_prizes_by_team` (dict `ranking|mvp|points|dream_team|total`). Orden desc; budget por defecto 200M; 500 en error. |
| `GET /api/v1/analytics/balances` | `balances.get_balances` | Bearer | Saldos por equipo; suma `ranking_prize + mvp_prize + points_prize + dream_team_prize` de `team_prizes` al balance y expone `prizes` por equipo. |
| `GET /api/v1/analytics/balances/{team_id}` | `balances` | Bearer | Saldo de un equipo concreto. |
| `GET /api/v1/analytics/prizes/{team_id}` | `balances` | Bearer | Desglose de premios por jornada de un equipo. Etiqueta las pseudo-jornadas adelantadas (matchday negativo) como "Adelantada" y las ordena al final. |
| `GET /api/v1/matchdays/teams` | `matchdays` | Bearer | Equipos del campeonato. |
| `GET /api/v1/matchdays/teams/{team_id}/rounds` | `matchdays` | Bearer | Rondas de un equipo. |
| `GET /api/v1/matchdays/evolution` | `matchdays` | Bearer | Evolución por jornada; DB-first con fallback a la API de Futmondo. |
| `GET /api/v1/analytics/*` | `analytics` (~12 endpoints) | Bearer | Analítica avanzada (trends, classification-full, custom-classification, heatmap, players/form, players/value-trend, users/consistency, users/market-activity, market/watchlist, clauses/network, opportunities/streaks, projections/matchday). Delegan en `AnalyticsService`; `classification-full` y `watchlist` llevan **SQL inline** (deuda; ver `code-quality-assessment.md`). |

Notas de montaje: `matchdays` se monta bajo `/api/v1/matchdays` (y adicionalmente `/v1/matchdays`);
`balances.py` expone rutas bajo el prefijo `analytics` (de ahí `GET /api/v1/analytics/prizes/{team_id}`).
`player_finances` cuelga de `/api/v1/player-finances`.

### Modelo de datos de premios (fuente de verdad)

Tabla `team_prizes(championship_id, team_id, matchday, ranking_prize, mvp_prize, position,
points_prize, dream_team_prize, synced_at)`, con UPSERT por
`ON CONFLICT (championship_id, team_id, matchday)`. Config de premios leída de
`user_championships`: `money_per_ranking`, `mvp_bonus`, `ranking_mode` (`flop`|otro),
`users_to_rank`, `money_per_point`, `dream_team_bonus`.

## Endpoints Relevantes a Intents Anteriores (security-hardening)

Superficie HTTP relevante a las FR de seguridad (contratos y estado; la evidencia de deuda
vive en `code-quality-assessment.md`):

| Método + Ruta | Handler | Auth | FR | Estado |
|---|---|---|---|---|
| `POST /api/v1/market/bid` | `market.place_bid` | Bearer | FR6 | Params query `championship_id, player_id, player_slug, price: int, is_clause`. **NO valida `price`**; proxya a `POST {base_url}/1/market/bid` de Futmondo. |
| `POST /api/v1/market/cancel` | `market.cancel_bid` | Bearer | — | Cancelación de puja. |
| `GET /api/v1/market/today` | `market.get_market_today` | Bearer | — | Mercado del día con puja sugerida + Sofascore. |
| `GET /api/v1/photos/{player_id}` | `get_player_photo` (en `main.py`) | Bearer | FR7 | La ruta `/api/v1/photos/...` NO está en `AUTH_EXCLUDED_PATHS` → el middleware SÍ exige token (no es pública). Redirige 302 a `/static/photos/*` (esa sí sin auth). |
| `POST /api/v1/database/reset` | `reset_db` | Bearer | FR18 | `_require_db_admin()` lanza 404 salvo `ENABLE_DB_ADMIN ∈ {1,true,yes,on}`. Guard implementado y con test. |
| `POST /api/v1/database/populate` | `reset_db` | Bearer | FR18 | Misma guarda `ENABLE_DB_ADMIN`. |
| `POST /auth/refresh` | `auth.routes` | Excluida (usa cookie) | FR9 | Usa `is_refresh_token_valid(token_hash)` de `token_store.py` (bug de precedencia naive/aware). |
| `POST /auth/login` | `auth.routes` | Excluida | — | Login contra Futmondo; emite JWT + set cookie refresh. |
| `POST /auth/logout` | `auth.routes` | Excluida | — | Revoca sesión/refresh token. |
| `GET /health` | app | Excluida | — | Healthcheck de despliegue Fly.io (smoke test). |

Todos los routers se montan en `main.py` con prefijos `/api/v1/...`. El router de auth no
usa prefijo `/api/v1` (vive en `/auth/*`).

## APIs Externas Consumidas

- **API Futmondo** — proxy autenticado por usuario (`_helpers.get_user_futmondo_client` →
  `futmondo_client.py`); ejemplos: `POST {base_url}/1/market/bid` (pujas) y los endpoints de
  datos que consume `sync_prizes` (standings, rounds, round_ranking, dream_team,
  round_lineup, round_matches).
- **API Sofascore** — `sofascore_client.py` (vía `curl_cffi`) para ratings de jugadores.
