# Frontend Components — N/A (intent backend)

Este intent es **puramente backend**: optimiza la latencia de
`GET /api/v1/market/today` y `GET /api/v1/favorites/my` sirviendo desde datos ya
sincronizados en Neon, **sin cambiar el contrato de respuesta**. Por tanto **no
hay componentes de frontend nuevos ni modificados**.

- Los consumidores actuales (Angular `angular-app` y la app nativa iOS) siguen
  llamando a los mismos endpoints con la misma forma de respuesta (BR6.1 /
  FR3.1). No requieren ningún cambio.
- No se añaden, renombran ni retiran campos; no cambia el orden de
  `favorites/my` (`position_order` asc, `value` desc).

## Límite de servicio backend (en lugar de componentes de UI)

La frontera nueva es una **capa de lectura** en el backend, no de UI:

| Módulo nuevo (capa estrecha testeable) | Responsabilidad | Contrato que preserva |
|---|---|---|
| `services/sync_read/favorites_read.py` (`FavoritesReader`) | Lee favoritos free-agent desde `player_championship_stats` JOIN `players` (+ `sofascore_cache`), filtrado por `player_favorites`; ordena `position_order` asc, `value` desc; fallback vivo en sync-miss | `/favorites/my` → `{success, players[(player_id,name,slug,position,position2,team,team_logo,value,change,points,average,home_average,away_average,matches,rating,sofascore_rating,sofascore_url,starter_pct,status,position_order)], total}` |
| `services/sync_read/market_read.py` (`MarketReader`) | Catálogo desde `market_today`; pujas del usuario (`current_bid`/`current_bid_id` + `active_bids_*`) desde UNA llamada viva targeted `POST /1/market/players` (no sincronizable — verificado); `user_info` combina base de BD con esas pujas; fallback vivo del catálogo en sync-miss; pujas degradadas a cero si su llamada falla | `/market/today` → `{success, championship_id, total_in_market, computer_players, players[~30 campos, incl. current_bid/current_bid_id], user_info{balance, team_value, max_bid, active_bids_total, active_bids_count, available_for_bids}}` |

El SQL vive en estos módulos, **no** en los routers ni en los god-files
(`data_sync_service.py`, `data_manager_v2.py`) — BR1.1.
