# API Documentation — Futmondo Analytics

> Nota de alcance (run 261019-presupuesto-selector-cam): refresco incremental
> para F2 (Presupuesto nativo + selector de campeonato). Se **verificaron leyendo
> el código** los endpoints que F2 consume (`/api/v1/analytics/balances`,
> `/api/v1/user/championships`, `/api/v1/championships`); el resto del contrato de
> API se **preserva** del escaneo previo (shallow). El cliente nativo iOS reutiliza
> estos endpoints sin cambios de servidor.

Backend FastAPI (`title="Futmondo API"`, `version="2.0.0"`). Dos espacios de
rutas: `/auth/*` (sin prefijo `/api/v1`) y `/api/v1/*`. La protección se aplica
en `AuthMiddleware` (`main.py`): toda ruta bajo `/api/v1` exige
`Authorization: Bearer <access_token>` salvo las de `AUTH_EXCLUDED_PATHS`.

## Autenticación — contrato real (clave para F1)

### `POST /auth/login`

- **Body** (`LoginRequest`, pydantic): `{ "email": str, "password": str }` — son
  las credenciales de **Futmondo** del usuario.
- **Comportamiento**: valida contra la API de Futmondo (`FutmondoClient.login()`).
  Si falla → `401` con `detail` en castellano
  (`"Credenciales incorrectas..."`). Si acierta: upsert de `app_users`, emite
  access + refresh token, cachea la sesión Futmondo, persiste sesión durable
  (best-effort) y auto-detecta campeonatos.
- **Respuesta (200, JSON)**:
  ```json
  {
    "access_token": "<JWT access>",
    "token_type": "bearer",
    "expires_in": 3600,
    "user_id": "<hex>",
    "email": "<email>",
    "display_name": "<local-part del email>"
  }
  ```
- **Side-effect de transporte**: además fija la cookie `HttpOnly`
  `futmondo_refresh_token` (`_set_refresh_cookie`): `httponly=True`,
  `secure=COOKIE_SECURE` (default `true`), `samesite="lax"`,
  `max_age=2592000` (30 días), `path="/auth"`. El refresh token **NO** aparece en
  el body JSON: hoy viaja **solo** por esta cookie.

### `POST /auth/refresh`

- **Entrada**: cookie `futmondo_refresh_token` (parámetro `Cookie(...)`). **No**
  acepta hoy el refresh token por body ni por header.
- **Comportamiento**: sin cookie → `401` (`"No refresh token"`). Verifica firma
  (`verify_token(expected_type="refresh")`), comprueba no-revocado/no-expirado
  por hash en `refresh_tokens` (`is_refresh_token_valid`), relee email/uid del
  usuario y emite un nuevo access token. Dispara rehidratación de sesión durable
  best-effort.
- **Respuesta (200, JSON)**:
  `{ "access_token": "<JWT>", "token_type": "bearer", "expires_in": 3600 }`.

### `POST /auth/logout`

- **Entrada**: cookie `futmondo_refresh_token` (opcional).
- **Comportamiento**: revoca el refresh token (`revoke_refresh_token` por hash),
  elimina la sesión Futmondo en memoria, purga la sesión durable y el handle
  cifrado, y limpia la cookie (`_clear_refresh_cookie`).
- **Respuesta (200)**: `{ "success": true, "message": "Sesión cerrada" }`.

### Implicación D-01 para F1

Un cliente nativo iOS no tiene almacén de cookies de navegador ni participa del
mismo origen CORS. El contrato actual entrega el refresh token **solo** por
cookie `HttpOnly`, por lo que F1 requiere un **ajuste aditivo del backend** para
transportar el refresh token también fuera de la cookie (p. ej. en el body de
`/auth/login` y aceptarlo en el body/header de `/auth/refresh`), preservando el
camino cookie existente para el navegador. El refresh token en iOS debe guardarse
en **Keychain** (nunca en claro). La verificación/firma/revocación
(`jwt_utils.py`, `refresh_tokens`) se reutiliza sin cambios.

## Protección de `/api/v1/*`

`AuthMiddleware.dispatch` (`main.py`):
- Rutas que no empiezan por `/api/v1` ni `/auth` → pasan sin auth.
- `AUTH_EXCLUDED_PATHS` = `/auth/login`, `/auth/refresh`, `/auth/logout`,
  `/health`, `/`, `/docs`, `/openapi.json`, `/redoc` → sin auth.
- Resto de `/api/v1/*`: exige `Authorization: Bearer`; sin header → `401`
  `{"detail": "Not authenticated"}`; token inválido/expirado → `401`
  `{"detail": "Token expired or invalid"}`. Al validar, adjunta
  `request.state.user = { user_id, email, futmondo_uid }`.

La dependencia `get_current_user` (`dependencies.py`) implementa la misma
validación para endpoints que la declaran explícitamente.

### `GET /api/v1/user/me`

- Requiere Bearer. Lee `request.state.user` (puesto por el middleware); si falta
  → `401`. Devuelve el usuario desde `app_users`:
  ```json
  {
    "success": true,
    "user": { "id", "email", "futmondo_user_id", "display_name",
              "created_at", "last_login" }
  }
  ```
- Si el usuario no existe en DB → `404`.

### Endpoints de datos que consume F2 (Presupuesto + selector de campeonato)

Todos protegidos por Bearer (bajo `/api/v1`). Verificados leyendo
`balances.py`, `user.py` y `championships.py`.

#### `GET /api/v1/analytics/balances`

- **Router**: `balances.py` (montado bajo el prefijo `/api/v1/analytics`).
- **Query**: `championship_id` (opcional; default `CHAMPIONSHIP_ID` de `config`).
  El frontend lo pasa desde el campeonato activo.
- **Comportamiento**: lee `team_value` de la API de Futmondo vía la sesión del
  usuario (`get_user_futmondo_client`), calcula por equipo compras/ventas desde
  la tabla `transactions` (SQL-en-endpoint, patrón heredado a NO ampliar), lee la
  config del campeonato (`get_championship_config`) para `initial_budget` y
  `excluded_teams`, y deriva `balance`, `total_spent`, `total_income`,
  `purchases_count`, `sales_count`, `team_value`, `performance`
  (`teamValue + balance - initial_budget`), `max_bid` y `prizes`.
- **Respuesta (200)**: forma del modelo Angular `BalancesResponse`:
  ```json
  {
    "success": true,
    "championship_id": "<id>",
    "initial_budget": 200000000,
    "teams": [
      { "team_id", "team_name", "balance", "initial_budget", "total_spent",
        "total_income", "purchases_count", "sales_count", "team_value",
        "performance", "max_bid", "prizes" }
    ]
  }
  ```
- **Fallback de presupuesto**: `INITIAL_BUDGET = 200_000_000` por defecto.

#### `GET /api/v1/analytics/balances/{team_id}` (detalle de equipo)

- Mismo router; detalle de altas/bajas de un equipo. El servicio Angular lo
  consume como `getTeamDetail(teamId, championshipId?)`. Forma del modelo
  `TeamDetailResponse`: `success`, `team_id`, `team_name`, `balance`,
  `initial_budget`, `total_spent`, `total_income`, `purchases[]`, `sales[]`
  (cada `Transaction`: `player_id`, `player_name`, `price`, `date`, `from?`,
  `to?`). *(La ruta exacta se deriva del `BudgetService` Angular; el cuerpo del
  handler de detalle no se transcribió campo a campo en este run.)*

#### `GET /api/v1/user/championships`

- **Router**: `user.py`. Requiere Bearer; `request.state.user` lo pone el
  middleware. Sin usuario → `401`.
- **Comportamiento**: lee `user_championships` del usuario (SQL-en-endpoint),
  ordenado por `name`.
- **Respuesta (200)**:
  ```json
  {
    "success": true,
    "championships": [
      { "championship_id", "name", "initial_budget", "has_clauses",
        "excluded_teams": [], "money_per_point", "money_per_ranking",
        "dream_team_bonus", "mvp_bonus", "ranking_mode", "users_to_rank" }
    ]
  }
  ```
- **Relacionado**: `POST /api/v1/user/championships` (upsert de un campeonato,
  body `ChampionshipConfig` pydantic con defaults, p. ej. `initial_budget=200000000`,
  `ranking_mode="flop"`, `users_to_rank=-1`).

#### `GET /api/v1/championships` (legacy, fallback)

- **Router**: `championships.py`. Devuelve la lista de campeonatos del usuario
  autenticado leyendo `user_championships` (subconjunto de campos:
  `championship_id`, `name`, `has_clauses`, `initial_budget`, `excluded_teams`).
  Sin usuario → `{"success": true, "championships": []}`; error → `500` con
  `detail`. Es el **fallback** que usa `ChampionshipService` cuando
  `/api/v1/user/championships` falla.

> Contrato para el cliente nativo F2: el servicio Angular `ChampionshipService`
> carga `/api/v1/user/championships` con fallback a `/api/v1/championships` y
> persiste el campeonato activo en `localStorage`
> (`futmondo_active_championship`); el selector nativo debe reproducir ese
> patrón de carga con su propio almacén local (no `localStorage`). El
> `BudgetService` pasa `championship_id` como query param a `/analytics/balances`.

### Endpoints de Mercado que consume F3 (vista de Mercado nativa)

Todos bajo el prefijo `/api/v1/market`, protegidos por Bearer. Verificados
leyendo `backend/app/api/v1/endpoints/market.py` en el run de F3. El detalle de
Sofascore vive en un router **aparte** (`/api/v1/sofascore`).

#### `GET /api/v1/market/today`

- **Router**: `market.py` (`@router.get("/today")`, prefijo `/api/v1/market`).
- **Query**: `championship_id` (opcional; default `CHAMPIONSHIP_ID` de `config`).
  El frontend lo pasa desde el campeonato activo.
- **Comportamiento**: resuelve el `futmondo_team_id` del usuario (DB
  `user_championships`, fallback a la API Futmondo `/1/market/players` y persiste
  el resultado). Lee jugadores de la caché `market_today` (por `championship_id`
  + fecha de hoy); si no hay caché, los trae en vivo de Futmondo y los guarda.
  Las **pujas del usuario** siempre se leen en vivo (nunca de la caché compartida,
  por privacidad). Filtra solo jugadores del `computer`. Calcula `suggested_bid`
  por % de sobrepago histórico desde `transactions`
  (`seller_team_id='market_team'`, SQL-en-endpoint heredado). Enriquece con
  `sofascore_cache` (rating, goles, asistencias, `starter_pct`, `sofascore_url`)
  y favoritos (`player_favorites`). Ordena por `value` descendente.
- **Respuesta (200, JSON)**:
  ```json
  {
    "success": true,
    "championship_id": "<id>",
    "total_in_market": 120,
    "computer_players": 24,
    "players": [
      { "player_id", "slug", "name", "team", "team_logo", "position",
        "position2", "value", "market_price", "change", "current_bid",
        "current_bid_id", "average", "points", "home_average", "away_average",
        "matches", "photo", "expiration", "suggested_bid", "bid_confidence",
        "bid_based_on", "overpay_pct", "sofascore_id", "sofascore_rating",
        "sofascore_goals", "sofascore_assists", "sofascore_appearances",
        "sofascore_url", "starter_pct", "is_favorite" }
    ],
    "user_info": {
      "balance": 0, "team_value": 0, "max_bid": 0,
      "active_bids_total": 0, "active_bids_count": 0, "available_for_bids": 0
    }
  }
  ```
  El modelo Angular `MarketPlayer` consume un **subconjunto** de los campos de
  `players[]` (ignora `photo`, `sofascore_id/goals/assists/appearances`). El
  banner del Mercado usa `balance`, `active_bids_total`,
  `balance − active_bids_total`, `max_bid` y `available_for_bids`.
  `max_bid = balance + team_value*0.5`; `available_for_bids = max_bid − active_bids_total`.
- **Errores**: fallo interno → `500` con `detail`. Si no hay equipo resoluble,
  devuelve `{"success": true, "players": [], "message": ...}` o
  `{"success": false, "players": [], "error": ...}`.

#### `POST /api/v1/market/bid`

- **Router**: `market.py` (`@router.post("/bid")`).
- **Query** (sin body JSON de datos; el frontend envía `{}` como body):
  `championship_id`, `player_id`, `player_slug`, `price` (int), `is_clause`
  (bool, default `false`).
- **Comportamiento**: valida `price > 0` y `price <= PRICE_SANITY_CAP`
  (`5_000_000_000`) en el boundary → si no, `422` (guardrail de backend, NO el
  límite real de mercado, que valida Futmondo). Resuelve `user_team_id` (sin él
  → `400`). Proxya a Futmondo `POST /1/market/bid`.
- **Respuesta (200)**: `{ "success": true, "message": "Puja de …€ realizada correctamente", "player_id", "price" }`
  cuando Futmondo responde `answer.code == "api.general.ok"`; en caso contrario
  `{ "success": false, "message": <code>, "detail": <answer> }`. Excepción no
  controlada → `500`.

#### `POST /api/v1/market/cancelbid`

- **Router**: `market.py` (`@router.post("/cancelbid")`).
- **Query** (body `{}`): `championship_id`, `bid_id`.
- **Comportamiento**: resuelve `user_team_id` (sin él → `400`). Proxya a Futmondo
  `POST /1/market/cancelbid` con `query.bid = bid_id`.
- **Respuesta (200)**: `{ "success": true, "message": "Puja cancelada correctamente" }`
  si `answer.code == "api.general.ok"`; si no `{ "success": false, "message": <code> }`.
  Excepción → `500`.

#### `GET /api/v1/sofascore/player/{player_name}` (detalle Sofascore)

- **Router**: `sofascore_detail.py` (`@router.get("/player/{player_name}")`,
  prefijo `/api/v1/sofascore`). **No** pertenece a `/market/*`; lo consume el
  `SofascoreDetailDialogComponent`.
- **Path**: `player_name` (URL-encoded). **Query**: `championship_id` (opcional).
- **Comportamiento**: lee `sofascore_cache` por `player_name`;
  `starter_pct = round(matches_started/38*100)` (o `null`). Sin fila → `404`.
- **Respuesta (200)**:
  ```json
  {
    "success": true,
    "player": {
      "player_name", "sofascore_id", "sofascore_name", "team", "rating",
      "goals", "assists", "appearances", "matches_started", "starter_pct",
      "minutes_played", "yellow_cards", "red_cards", "tournament", "season",
      "successful_dribbles", "accurate_passes_pct", "shots_on_target",
      "tackles", "interceptions", "clean_sheets", "saves", "synced_at"
    }
  }
  ```

> Contrato para el cliente nativo F3: la vista de Mercado consume `GET /market/today`
> (pasando `championship_id` del campeonato activo), puja con `POST /market/bid`
> (todos los campos van en **query params**, body vacío) y cancela con
> `POST /market/cancelbid` (query `championship_id`/`bid_id`). El detalle Sofascore
> es un endpoint separado `/sofascore/player/{name}`. Todos exigen Bearer; el
> servidor no cambia para F3.

### Otros endpoints `/api/v1/*` (resumen, todos protegidos por Bearer)

| Prefijo (router) | Ejemplos | Propósito |
|---|---|---|
| `/api/v1/user` | `/me`, `/championships` | Usuario y config de campeonatos |
| `/api/v1/analytics` | `/balances` (balances router) | Presupuestos y analítica |
| `/api/v1/market` | `/today`, `/bid`, `/cancelbid` | Mercado, puja y cancelación (ver detalle arriba) |
| `/api/v1/sync` | `/trigger`, `/task/{id}`, phantoms, sofascore | Sync async durable |
| `/api/v1/player-finances` | `/` | Finanzas por usuario |
| `/api/v1/roster`, `/transactions`, `/favorites` | — | Plantilla, movimientos, favoritos |
| `/api/v1/clausulable-players`, `/statistics`, `/user-stats` | — | Clausulables y estadísticas |
| `/api/v1/matchdays`, `/initialize`, `/database` (reset_db) | — | Jornadas, init, admin DB |
| `/api/v1/assistant` | — | Asistente AI (Gemini/Groq) |
| `/api/v1/photos/{player_id}` | — | Foto de jugador (protegida; redirige 302 al mount público `/static/photos/*`) |

### Rutas públicas de servicio

- `GET /` → metadata del servicio. `GET /health` → `{"status":"healthy"}` (usado
  por el smoke test de `fly-deploy.yml`). `/static/photos/*` → mount estático
  **público intencional** de imágenes no sensibles (fuera de `/api/v1` y `/auth`).

## Sources

- `backend/app/api/v1/endpoints/balances.py` (balances; SQL-en-endpoint, performance)
- `backend/app/api/v1/endpoints/user.py` (`/me`, `/championships` GET/POST)
- `backend/app/api/v1/endpoints/championships.py` (legacy fallback)
- `backend/app/api/v1/endpoints/market.py` (`/today`, `/bid`, `/cancelbid`; añadido en el run de F3)
- `backend/app/api/v1/endpoints/sofascore_detail.py` (`/player/{name}`; añadido en el run de F3)
- `angular-app/src/app/features/market/{market,bid-dialog,confirm-dialog,sofascore-detail-dialog}.component.*` (consumo F3)
- `angular-app/src/app/core/services/{budget,championship}.service.ts`,
  `angular-app/src/app/core/models/budget.model.ts` (contrato de consumo)
- `backend/app/main.py` (AuthMiddleware, routers, `/health`, `/`, fotos)
- `backend/app/auth/routes.py` (login/refresh/logout, cookie)
- `backend/app/auth/jwt_utils.py` (ACCESS_TOKEN_EXPIRE_MINUTES=60)
- `backend/app/auth/dependencies.py`

## Assumptions & Open Questions

- Los contratos de request/response detallados de cada endpoint de datos (más
  allá de auth y `/user/me`) no se transcriben campo a campo; se enumeran por
  prefijo/propósito a partir de `main.py` y los nombres de fichero. F1 solo
  necesita el contrato de auth y `/user/me`, que sí están verificados leyendo el
  código. El intent de diseño nativo (261018) no re-verificó el backend: esta
  prosa es la del escaneo previo, preservada y marcada como shallow.
- En el run de F3 (`261020-mercado-pujas`) SÍ se verificaron leyendo el código
  los endpoints `/api/v1/market/{today,bid,cancelbid}` y
  `/api/v1/sofascore/player/{name}`. Aviso de contrato: en `/bid` y `/cancelbid`
  **todos los parámetros viajan como query params**, no en el body (el frontend
  envía `{}` como body). El detalle Sofascore NO es `/market/*` sino el router
  separado `/api/v1/sofascore`. El resto del backend sigue shallow.
