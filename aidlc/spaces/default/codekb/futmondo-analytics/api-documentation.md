# API Documentation — Futmondo Analytics

> Merge CURRENT. Contratos previos **preservados**; refresco del flujo de datos
> del sync de jugadores y de la ruta `favorites/my` (fast-path sync / fallback
> vivo) para el intent `261023-sync-jugador-completo`. El shape de respuesta se
> PRESERVA byte-for-byte en cualquier mejora.

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
- **Fuente de los campos ricos**: `team_logo`, `change`, `home_average`,
  `away_average`, `matches` vienen hoy de `market_today` (el catálogo del día),
  no del sync de jugadores. El intent busca que estos campos existan en el sync
  para TODOS los jugadores.
- **Errores**: `500` en fallo genérico; `HTTPException` propagada.

## `GET /api/v1/favorites/my` (fast-path sync / fallback vivo)

- **Query**: `championship_id` (default `CHAMPIONSHIP_ID`).
- **Auth**: Bearer.
- **Ruta**:
  1. **Fast-path**: `sync_read.read_favorites(db, championship_id, user_id)` lee
     desde Neon sincronizado: `player_favorites` (ids), `players`+
     `player_championship_stats` (set de agentes libres: `owner_team_id IS
     NULL`), `market_today` (left lookup por `player_id`+fecha de hoy para
     `change/home/away/matches/points/team/team_logo`), `player_performance`
     (SUM `points`), `sofascore_cache`. Si hay ≥1 fila free-agent sincronizada
     (`has_synced=True`), responde desde el sync.
  2. **Fallback vivo** (`_get_favorites_live`, pre-refactor): en sync-miss
     (0 filas) descarga el catálogo completo en vivo
     (`get_championship_players`, `/5/league/championshipplayers`) +
     `get_matchday_standings` + `get_userteam_roster`, y lee
     `change/points/home_average/away_average/matches/logo` directamente del
     objeto por jugador. Enriquecimiento Sofascore desde `sofascore_cache`.
- **Response** `{ success, players[], total }`:
  - `players[]`: `player_id, name, slug, position, position2, team, team_logo,
    value, change, points, average, home_average, away_average, matches, rating,
    sofascore_rating, sofascore_url, starter_pct, status, position_order`.
  - Orden: `position_order` asc, luego `value` desc. Sin favoritos →
    `{ success: true, players: [], total: 0 }` (no es sync-miss).
  - **Gap actual**: para un agente libre fuera del mercado del día, el fast-path
    devuelve `change=0`, `home_average=None`, `away_average=None`, `matches=0`,
    `team_logo=''`, `points` solo si `player_performance` tiene filas (vacío para
    agentes libres). Verificado en prod: 32/33 favoritos con esos campos vacíos.
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
- Sub-rutas: `GET /analytics/balances/{team_id}`, `GET /analytics/prizes/{team_id}`.

## Sync completo de jugadores — contrato de datos (escritura)

`DataSyncService.sync_players_full` → `PlayersFullSyncOrchestrator.sync()` lee el
catálogo vivo y persiste:

| Tabla | Campos persistidos hoy | Fuente (objeto vivo) |
|---|---|---|
| `players` | `name,role,role2,real_team_id,real_team_name,slug,photo_url,value` | `name,role,role2,teamId,team,slug,photo,value` |
| `player_championship_stats` | `owner_team_id,owner_team_name,owner_user_id,clause_price,suggested_clause,average_last_five,average_overall,clause_date` | `userteam*`, `clause{price,suggestedClause,date}`, `average{averageLastFive,average}` |
| `player_favorites` | `championship_id,user_id,player_id` | `fav==true && !userteamId` |
| `sync_metadata` | `data_type='players'`, conteo, duración, estado | — |

**NO persiste** (gap del intent): `points`, `change`, `home_average`,
`away_average`, `matches`, `team_logo`. Fuentes actuales de esos campos:
`player_performance` (`points`, por jornada; vacío para agentes libres) y
`market_today` (el resto, ~30 jugadores del día).

## Integración Futmondo (vía `FutmondoClient`, timeout 15 s/llamada)

| Método | Endpoint Futmondo | Usado por | Nota para el intent |
|---|---|---|---|
| `get_championship_players` | `/5/league/championshipplayers` | sync players, favorites (fallback) | **fuente del sync; INCÓGNITA: ¿trae points/change/medias-detalle/logo por jugador?** El adapter solo lee `name/role/team/value/clause/average` |
| `get_player_summary` | `/1/player/summary` | detalle jugador | candidata por-jugador si el catálogo no trae los campos |
| `get_player_fullprofile` | `/1/player/fullprofile` | histórico de precios | candidata por-jugador (prices array) |
| `get_market_players` / POST directo | `/1/market/players` | market/today (pujas + catálogo) | ya trae todos los campos ricos, pero solo para el mercado del día |
| `get_matchday_standings` | `/2/championship/teams` | balances, market, favorites, roster, sync | — |
| `get_userteam_roster` | `/1/userteam/roster` | favorites, roster, sync | trae `logo` por jugador del roster |

> **INCÓGNITA CRÍTICA (Functional Design)**: no hay evidencia en código de que
> `/5/league/championshipplayers` devuelva `points`/`change`/`average` detallado/
> `team_logo` por jugador. Verificar con una llamada cruda (token server-side)
> antes de diseñar el enriquecimiento; si no los trae, la fuente debe ser otra
> (`/1/player/summary`, `/1/player/fullprofile` o Sofascore), lo que cambia el
> diseño y el coste del sync.
