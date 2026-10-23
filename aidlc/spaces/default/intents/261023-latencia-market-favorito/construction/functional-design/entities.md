# Entities — Optimización de latencia (read-from-sync)

Modelo de las **lecturas** (no se crean tablas nuevas; se leen las ya
sincronizadas). Fuente de verdad: bloque `yaml`. Technology-agnostic.

```yaml
entities:
  - name: SyncedPlayerRow
    description: >
      Fila de jugador leída de las tablas ya sincronizadas por DataSyncService,
      usada para servir favorites/my y el catálogo de market/today sin la
      llamada viva. NO es una tabla nueva: es la proyección de lectura sobre
      player_championship_stats JOIN players (+ sofascore_cache).
    source_tables:
      - players (name, slug, position, position2, team, team_logo, value, change, points, average, home_average, away_average, matches, status, position_order)
      - player_championship_stats (championship_id, player_id, owner_team_id → free-agent = owner nulo/none)
      - sofascore_cache (sofascore_id, rating, sofascore_url, por nombre/slug)
    attributes:
      - { name: playerId, source: players.player_id }
      - { name: value, source: players.value }
      - { name: change, source: players.change }
      - { name: points, source: players.points }
      - { name: average/home/away/matches, source: players }
      - { name: sofascoreRating/url, source: sofascore_cache }
      - { name: starterPct/status/position/position2, source: players }
      - { name: positionOrder, source: players.position_order, notes: "clave de orden" }
      - { name: rating, source: players (campo plano, distinto de sofascore_rating), notes: "mapear explícitamente; si la columna sincronizada no lo trae, caracterización fija el valor que hoy devuelve el contrato para no romperlo (BR6.1)" }
      - { name: status, source: players.status, notes: "verificar columna sincronizada; caracterización congela el shape" }
      - { name: isFreeAgent, source: "player_championship_stats.owner_team_id IS NULL/none" }
    constraints:
      - "Favoritos = filas cuyo player_id está en player_favorites(championship_id,user_id) Y es free-agent."

  - name: UserBidsState
    description: >
      Pujas activas del usuario en un campeonato. VERIFICADO en código
      (market.py líneas 362-390, comentario "Cache has NO bids (stripped for
      privacy). Fetch this user's bids live."): las pujas activas del usuario NO
      están en Neon. market_today cachea el catálogo SIN pujas (privacidad);
      transactions sólo guarda compras/ventas CERRADAS, no pujas activas. No
      existe tabla de pujas. Por tanto las pujas activas del usuario sólo pueden
      obtenerse del POST /1/market/players vivo.
    source:
      - "ÚNICA fuente: POST /1/market/players (llamada viva). No hay fuente en Neon (verificado)."
    attributes:
      - { name: currentBid/currentBidId, notes: "por jugador, del bid vivo" }
      - { name: activeBidsTotal, notes: "Σ price de las pujas vivas" }
      - { name: activeBidsCount }
    constraints:
      - "No es sincronizable sin cambio de esquema (fuera de alcance por requisitos)."
      - "Se mantiene UNA llamada viva targeted (sólo pujas del usuario), NO la descarga del catálogo completo. El coste pesado nunca fue esta llamada."

  - name: MarketTodayReadModel
    description: >
      Catálogo de mercado servido desde market_today (cacheado) + pujas del
      usuario desde UNA llamada viva targeted (POST /1/market/players, sólo las
      pujas del usuario) + user_info derivado de BD combinado con esas pujas.
    source_tables: [market_today, team_standings (team_value), player_championship_stats JOIN players, transactions, team_prizes]
    live_dependency: "POST /1/market/players (irreducible sin cambio de esquema): aporta current_bid/current_bid_id por jugador y active_bids_* de user_info."
    notes: "Contrato de respuesta idéntico al actual (success, championship_id, total_in_market, computer_players, players[] con current_bid/current_bid_id, user_info{...})."

  - name: SyncAvailability
    description: Señal de si hay datos sincronizados suficientes para servir desde sync (FR4).
    logic: "has_synced = (SELECT COUNT(*) de jugadores sincronizados del campeonato) > 0. Si 0 → fallback a ruta viva + log."
```

## Resumen

- No se crean tablas: se **lee** de las ya sincronizadas (`players`,
  `player_championship_stats`, `sofascore_cache`, `market_today`,
  `team_standings`, `player_favorites`, `transactions`, `team_prizes`).
- `SyncedPlayerRow` alimenta favoritos (y el catálogo de market).
- `UserBidsState`: las pujas activas del usuario **NO** están en Neon
  (verificado en código); se mantiene **una** llamada viva targeted
  (`POST /1/market/players`) sólo para ellas, preservando el contrato. El
  catálogo de market sigue viniendo de `market_today`.
- `SyncAvailability` decide el fallback del **catálogo** (0 filas → vivo).
