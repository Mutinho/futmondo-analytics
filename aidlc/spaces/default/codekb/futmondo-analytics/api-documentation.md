# API Documentation — Futmondo Analytics

> Refresco enfocado en latencia. Se documentan los contratos de los 3 endpoints
> del intent (shape a PRESERVAR en cualquier mejora de rendimiento). Otros
> endpoints en el store previo.

## `GET /api/v1/market/today` (~1.6 s)

- **Query**: `championship_id` (default `CHAMPIONSHIP_ID`).
- **Auth**: Bearer; resuelve `FutmondoClient` vía `get_user_futmondo_client`.
- **Ruta**: lee caché `market_today`; SIEMPRE 1 llamada en vivo
  `POST /1/market/players` (pujas del usuario); +1 condicional si la caché está
  vacía (catálogo). Lecturas Neon: `transactions`, `sofascore_cache`,
  `player_favorites`, `team_standings`, `player_championship_stats`+`players`,
  `user_championships`, `team_prizes`.
- **Response** `{ success, championship_id, total_in_market, computer_players,
  players[], user_info }`:
  - `players[]`: `player_id, slug, name, team, team_logo, position, position2,
    value, market_price, change, current_bid, current_bid_id, average, points,
    home_average, away_average, matches, photo, expiration, suggested_bid,
    bid_confidence, bid_based_on, overpay_pct, sofascore_id, sofascore_rating,
    sofascore_goals, sofascore_assists, sofascore_appearances, sofascore_url,
    starter_pct, is_favorite`.
  - `user_info`: `balance, team_value, max_bid, active_bids_total,
    active_bids_count, available_for_bids`.
- **Errores**: `500` en fallo genérico; `HTTPException` propagada.

## `GET /api/v1/favorites/my` (~3.4 s)

- **Query**: `championship_id` (default `CHAMPIONSHIP_ID`).
- **Auth**: Bearer.
- **Ruta**: `SELECT player_id FROM player_favorites` (barato); luego **2-3
  llamadas en vivo** a Futmondo: `get_championship_players`
  (`/5/league/championshipplayers`, lista COMPLETA), `get_matchday_standings`,
  `get_userteam_roster`. Enriquecimiento Sofascore desde `sofascore_cache`.
- **Response** `{ success, players[], total }`:
  - `players[]`: `player_id, name, slug, position, position2, team, team_logo,
    value, change, points, average, home_average, away_average, matches, rating,
    sofascore_rating, sofascore_url, starter_pct, status, position_order`.
  - Orden: `position_order` asc, luego `value` desc. Sin favoritos →
    `{ success: true, players: [], total: 0 }`.
- **Errores**: `401` sesión no recuperable (actionable); `500` genérico.

### Endpoints de mutación de favoritos (mismo router)

- `POST /api/v1/favorites/unfollow?championship_id&player_id` → proxy a
  `/5/championship/unmarkfavorite` + `DELETE FROM player_favorites`. `{ success,
  message }`.
- `POST /api/v1/favorites/mark?championship_id&player_id` → proxy a
  `/5/championship/markfavorite` + `INSERT ... ON CONFLICT DO NOTHING`.

## `GET /api/v1/analytics/balances` (~0.4 s — patrón rápido de referencia)

- **Query**: `championship_id`.
- **Ruta**: 1 llamada en vivo `get_matchday_standings` (teamValue) + lecturas
  agregadas de Neon (`transactions` GROUP BY, `teams`, `team_prizes`).
- **Response** `{ success, championship_id, initial_budget, teams[] }`, cada
  team: `team_id, team_name, balance, initial_budget, total_spent, total_income,
  purchases_count, sales_count, team_value, performance, max_bid, prizes`.
- Sub-rutas: `GET /analytics/balances/{team_id}` (detalle altas/bajas),
  `GET /analytics/prizes/{team_id}` (premios por jornada).

## Integración Futmondo (vía `FutmondoClient`, timeout 15 s/llamada)

| Método | Endpoint Futmondo | Usado por |
|---|---|---|
| `get_matchday_standings` | `/2/championship/teams` | balances, market, favorites, roster, sync |
| `get_championship_players` | `/5/league/championshipplayers` | favorites (lista completa, pesada) |
| `get_userteam_roster` | `/1/userteam/roster` | favorites, roster, sync |
| `get_market_players` / POST directo | `/1/market/players` | market/today (pujas + catálogo) |
| `place_bid`/`cancel_bid` | `/1/market/bid`, `/1/market/cancelbid` | market |
