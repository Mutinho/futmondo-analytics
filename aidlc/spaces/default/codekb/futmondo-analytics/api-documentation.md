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

## Endpoints Relevantes al Intent

Superficie HTTP relevante a las FR (contratos y estado; la evidencia de deuda vive en
`code-quality-assessment.md`):

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

Todos los routers se montan en `main.py` con prefijos `/api/v1/...`; `matchdays` se monta
adicionalmente en `/v1/matchdays`. El router de auth no usa prefijo `/api/v1` (vive en
`/auth/*`). Otros endpoints (`analytics`, `balances`, `sync`, `roster`, etc.) existen pero
quedan fuera del alcance profundo de este scan (ver `reverse-engineering-timestamp.md`).

## APIs Externas Consumidas

- **API Futmondo** — proxy autenticado por usuario (`_helpers.get_user_futmondo_client` →
  `futmondo_client.py`); ejemplo: `POST {base_url}/1/market/bid`.
- **API Sofascore** — `sofascore_client.py` (vía `curl_cffi`) para ratings de jugadores.
