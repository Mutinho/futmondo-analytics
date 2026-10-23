# Business Rules — Optimización de latencia

Fuente de verdad: bloque `yaml`. `BRx.y` son claves de trazabilidad.

```yaml
rules:
  # Grupo 1 — Capa de lectura (arquitectura)
  - id: BR1.1
    statement: "La lectura-desde-sync vive en un módulo nuevo estrecho y testeable (p. ej. services/sync_read/favorites_read.py y market_read.py); el SQL vive ahí, NO en el router ni en los god-files."
    category: constraint
    applies_to: FavoritesReader, MarketReader
    trigger: "Implementación."
    logic: "Routers favorites.py/market.py llaman funciones de la capa nueva; nunca se amplían data_sync_service.py/data_manager_v2.py ni el patrón SQL-en-router."
    violation: "Ampliar un god-file o meter SQL nuevo en el router (prohibido por memoria)."
    source: FR5.1, C1

  # Grupo 2 — favorites/my desde sync
  - id: BR2.1
    statement: "favorites/my lee los jugadores favoritos desde player_championship_stats JOIN players (+ sofascore_cache), filtrando por player_favorites(championship_id,user_id) y por free-agent; ELIMINA la llamada viva get_championship_players."
    category: calculation
    applies_to: FavoritesReader
    trigger: "GET /api/v1/favorites/my."
    logic: "fav_ids = SELECT player_id FROM player_favorites WHERE championship_id,user_id; players = SELECT ... FROM player_championship_stats pcs JOIN players p ... LEFT JOIN sofascore_cache ... WHERE p.player_id IN fav_ids AND free-agent."
    violation: "Seguir llamando a get_championship_players en la carga normal."
    source: FR1.1, FR1.2
  - id: BR2.2
    statement: "El orden de favorites/my se preserva: position_order asc, luego value desc."
    category: policy
    applies_to: FavoritesReader
    trigger: "Al componer la respuesta."
    logic: "ORDER BY position_order ASC, value DESC (o equivalente en memoria tras el fetch)."
    violation: "Orden distinto al contrato actual."
    source: FR1.3

  # Grupo 3 — Fallback sync-miss
  - id: BR3.1
    statement: "Para favorites/my y para el CATÁLOGO de market/today: si el SELECT sincronizado del campeonato devuelve 0 jugadores, fallback a la ruta viva actual (correcta aunque más lenta) y se registra (log); si devuelve filas, se sirve desde sync. El endpoint NUNCA devuelve vacío por ausencia de caché."
    category: policy
    applies_to: FavoritesReader, MarketReader
    trigger: "Tras el SELECT de jugadores sincronizados."
    logic: "has_synced = count>0. not has_synced → ruta viva + logger.info('sync-miss fallback', championship_id)."
    violation: "Devolver vacío por falta de sync, o no registrar el fallback."
    source: FR4.1, FR4.2
  - id: BR3.2
    statement: "En market/today, si el catálogo está sincronizado pero la llamada viva de pujas del usuario falla, se sirve el catálogo con pujas vacías degradadas (current_bid=0, active_bids_*=0) y se registra el fallo; NUNCA se falla la respuesta entera ni se devuelve el catálogo sin los campos de puja del contrato."
    category: policy
    applies_to: MarketReader
    trigger: "Fallo/timeout de POST /1/market/players con catálogo ya disponible."
    logic: "Estado DEGRADED: los campos de puja existen en el contrato con valor cero; logger.warning. (Mismo comportamiento tolerante que hoy, donde el except deja user_bids_map vacío.)"
    violation: "Fallar market/today entero por un fallo de la llamada de pujas, u omitir los campos de puja del contrato."
    source: FR4.2, NFR5

  # Grupo 4 — market/today: catálogo desde sync, pujas del usuario en vivo (verificado)
  - id: BR4.1
    statement: "market/today sirve el CATÁLOGO desde market_today (cacheado, sin llamada viva para el catálogo). Las PUJAS del usuario se obtienen con UNA llamada viva targeted (POST /1/market/players) porque no existen en Neon (verificado en market.py: la caché las elimina por privacidad y no hay tabla de pujas). Esa llamada es irreducible sin cambio de esquema, que está fuera de alcance."
    category: calculation
    applies_to: MarketReader, UserBidsState
    trigger: "GET /api/v1/market/today."
    logic: "catálogo ← market_today (fallback vivo sólo si 0 filas, BR3.1); current_bid/current_bid_id y active_bids_* ← POST /1/market/players del usuario. NO se descarga el catálogo completo en vivo (ese era el coste pesado)."
    violation: "Servir current_bid/active_bids_* vacíos u omitidos (rompe contrato), o reintroducir la descarga viva del catálogo completo."
    source: FR2.1, FR3.1
  - id: BR4.2
    statement: "La coherencia de las pujas bajo concurrencia se garantiza porque las pujas se leen EN VIVO de Futmondo (fuente autoritativa) en cada market/today, igual que bid/cancelbid escriben contra Futmondo: no hay caché de pujas que pueda desincronizarse. NO se cachea el estado de pujas del usuario en proceso."
    category: constraint
    applies_to: UserBidsState
    trigger: "Cada GET market/today y tras bid/cancelbid."
    logic: "Sin caché de pujas → sin version-skew: la siguiente lectura refleja la operación recién hecha por construcción."
    violation: "Cachear pujas del usuario y servir un total obsoleto tras una operación."
    source: FR2.2, NFR2

  # Grupo 5 — user_info coherente
  - id: BR5.1
    statement: "user_info se compone de dos partes con fuentes distintas: la parte NO ligada a pujas (balance base, team_value, max_bid) se deriva de la BD sincronizada; la parte ligada a pujas (active_bids_total, active_bids_count) y el derivado available_for_bids = max_bid − active_bids_total provienen de las pujas EN VIVO. Como active_bids_total es siempre el valor vivo (sin caché), available_for_bids refleja la operación recién hecha; no hay riesgo de sesgo por caché obsoleta."
    category: calculation
    applies_to: MarketReader
    trigger: "Respuesta de market/today (también la inmediata tras una operación)."
    logic: "available_for_bids = max_bid(BD) − active_bids_total(vivo). Nunca se mezcla un active_bids_total cacheado con un balance fresco."
    violation: "Calcular available_for_bids con un active_bids_total obsoleto/cacheado."
    source: FR2.2

  # Grupo 6 — Contrato intacto
  - id: BR6.1
    statement: "Las respuestas de favorites/my y market/today mantienen EXACTAMENTE su forma y campos actuales (documentados en codeKB); ningún consumidor (Angular, iOS) requiere cambios."
    category: constraint
    applies_to: FavoritesReader, MarketReader
    trigger: "Al serializar la respuesta."
    logic: "Mismos campos/orden/tipos que hoy; caracterización congela el shape antes de cambiar la fuente."
    violation: "Cambiar/renombrar/quitar un campo del contrato."
    source: FR3.1, NFR6

  # Grupo 7 — Errores y seguridad
  - id: BR7.1
    statement: "El fallo de integración externa (cuando se use la ruta viva de fallback) se señala como excepción tipada propagada, nunca None silencioso, y sin credenciales en el mensaje."
    category: policy
    applies_to: FavoritesReader, MarketReader
    trigger: "Fallo de la ruta viva de fallback."
    logic: "except <Typed>: raise antes del except Exception; mensaje con modo de fallo + contexto no sensible (status/endpoint)."
    violation: "Tragar el fallo o filtrar credenciales."
    source: NFR5
```

## Resumen de reglas

| Grupo | Tema | Reglas |
|---|---|---|
| BR1 | Capa de lectura (sin god-files, SQL fuera del router) | BR1.1 |
| BR2 | favorites/my desde sync (elimina llamada viva) + orden | BR2.1, BR2.2 |
| BR3 | Fallback sync-miss (0 filas → vivo + log) + fallo de pujas degradado | BR3.1, BR3.2 |
| BR4 | market/today catálogo desde sync + pujas en vivo (verificado) | BR4.1, BR4.2 |
| BR5 | user_info coherente tras operar | BR5.1 |
| BR6 | Contrato de respuesta intacto | BR6.1 |
| BR7 | Errores tipados / sin credenciales | BR7.1 |
