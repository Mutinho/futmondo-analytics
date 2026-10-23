# Developer Code Scan — Intent 261023-latencia-market-favorito

Escaneo brownfield **enfocado en latencia** que MERGEA sobre un store CURRENT
(`261020-mercado-pujas`, `kind: partial`). Objetivo: caracterizar con evidencia
de fichero/función POR QUÉ `GET /api/v1/market/today` (~1.6 s) y
`GET /api/v1/favorites/my` (~3.4 s) son lentos mientras `GET /api/v1/analytics/balances`
(~0.4 s) es rápido, e inventariar qué pre-sincroniza `data_sync_service` en Neon
y qué camino de lectura-desde-sync reutilizar.

## Developer Code Scan Results

### Hallazgo núcleo — camino de petición por endpoint

El coste dominante NO es la base de datos (Neon), sino el **número de llamadas
HTTP en vivo** a la API de Futmondo que cada endpoint hace **síncronamente por
petición** (`client.session.post(..., timeout=15)` vía `FutmondoClient`). Las
lecturas de Neon están agrupadas (`GROUP BY`, `LIMIT`, un único
`get_connection()` por request) y son baratas.

| Endpoint | Fichero/función | Llamadas Futmondo EN VIVO por request | Lecturas Neon | Latencia medida | Dónde se va el tiempo |
|---|---|---|---|---|---|
| `GET /api/v1/analytics/balances` | `balances.py::get_balances` | **1** (`get_matchday_standings` → `/2/championship/teams`) | `transactions` (2× `GROUP BY`), `teams`, `team_prizes` (`GROUP BY`) | **~0.4 s** | 1 round-trip externo + reads agregados baratos → rápido (patrón de referencia) |
| `GET /api/v1/market/today` | `market.py::get_market_today` → `_build_market_response` | **1** (SIEMPRE: `POST /1/market/players` para las pujas EN VIVO del usuario), **+1 condicional** si la caché `market_today` está vacía (fallback a `/1/market/players` para el catálogo) | `market_today` (caché), `transactions` (LIMIT 200), `sofascore_cache` (full), `player_favorites`, `team_standings`, `player_championship_stats`+`players`, `user_championships`, `team_prizes` | **~1.6 s** | 1 llamada en vivo obligatoria (pujas del usuario) + lecturas agregadas. La caché evita el catálogo pero NO las pujas en vivo |
| `GET /api/v1/favorites/my` | `favorites.py::get_my_favorites` | **hasta 3**: `get_championship_players` (`/5/league/championshipplayers`, **lista COMPLETA de jugadores**, pesada), `get_matchday_standings` (`/2/championship/teams`), `get_userteam_roster` (`/1/userteam/roster`) | `player_favorites` (1 SELECT), `sofascore_cache` (vía `build_sofascore_map`) | **~3.4 s** | 2-3 llamadas en vivo encadenadas; la más cara es `get_championship_players` (payload grande) que se descarga ENTERA solo para filtrar favoritos |

Conclusión: la latencia es **proporcional al número de llamadas Futmondo en vivo
por request** (0.4 s ≈ 1 llamada; 1.6 s ≈ 1 llamada + más proceso;
3.4 s ≈ 2-3 llamadas, una de ellas pesada). `balances` es rápido porque lee
**datos ya sincronizados** en Neon y solo hace 1 llamada en vivo
(`teamValue`/standings).

### Evidencia por endpoint

**`/analytics/balances` (patrón rápido de referencia)** — `balances.py`:
- 1 llamada en vivo: `client.get_matchday_standings(championship_id)` solo para
  `teamValue` por equipo.
- Todo lo demás son lecturas de `transactions` (compras/ventas agregadas por
  `GROUP BY`), `teams` (nombres), `team_prizes` (premios agregados). Datos
  **pre-sincronizados** por `data_sync_service`.
- SQL-en-router (patrón heredado, NO ampliar).

**`/market/today`** — `market.py::get_market_today` + `_build_market_response`:
- Lee primero la caché `market_today` (`SELECT raw_json ... WHERE championship_id
  AND market_date = today`). Si hay filas, NO llama a Futmondo para el catálogo.
- PERO siempre hace una llamada en vivo `POST /1/market/players` para obtener las
  **pujas actuales del usuario** (`live_user_players`), porque la caché guarda el
  catálogo SIN pujas (privacidad entre usuarios). Ese es el ~1 round-trip
  obligatorio.
- Si la caché está vacía: fallback a `/1/market/players` (catálogo) y lo guarda
  vía `assistant_service._save_market_to_db`.
- Resto: `transactions` (LIMIT 200 en batch, NO 24 queries), `sofascore_cache`
  (tabla completa en memoria), `player_favorites`, `team_standings`,
  `player_championship_stats`+`players`, `user_championships`, `team_prizes`.
- Resuelve `futmondo_team_id` desde `user_championships` (persistido) para
  evitar una llamada extra; solo cae a `_get_user_team_id` (vía standings en
  vivo) la primera vez.

**`/favorites/my` (el más lento)** — `favorites.py::get_my_favorites`:
- `SELECT player_id FROM player_favorites` (barato). Si vacío, corta.
- `client.get_championship_players(championship_id)` → **lista completa de
  jugadores del campeonato en vivo** (payload grande). Se descarga entera solo
  para quedarse con los `fav_ids` que son agentes libres.
- Dentro de un `try`: `get_matchday_standings` (en vivo) para hallar el
  `user_team_id`, luego `get_userteam_roster` (en vivo) para enriquecer
  `team_map`.
- Enriquecimiento Sofascore desde caché (`build_sofascore_map`, barato).
- NO existe caché de catálogo reutilizable aquí: a diferencia de `/market/today`,
  `favorites` NO lee de `market_today` ni de ninguna tabla pre-sincronizada de
  jugadores; va siempre en vivo.

### Qué pre-sincroniza `data_sync_service` en Neon (reutilizable)

`DataSyncService.sync_all` (`data_sync_service.py`, god-file ~15 KB, delega en
orquestadores DDD bajo `services/sync/`) pre-sincroniza a Neon:

| Dato | Orquestador | Tabla(s) destino (observadas) |
|---|---|---|
| players | `sync_players_full` | `players`, `player_championship_stats`, `player_favorites` (vía `_save_favorites`) |
| transactions | `sync_transactions` | `transactions` (con `market_value_at_purchase`, bids) |
| clauses | `sync_clauses` | cláusulas |
| punishments/bonuses | `sync_punishments_bonuses` | castigos/bonos |
| dream teams / MVP | `sync_dream_teams_mvps` | dream team / mvp |
| player performance | `sync_player_performance` | rendimiento por jornada |
| rosters | `sync_rosters` | rosters por jornada |
| team standings | `sync_round_rankings` | `team_standings` (incl. `team_value`) |
| match odds | `sync_match_odds` | odds |
| prizes | `sync_prizes` | `team_prizes` |
| market (catálogo) | `assistant_service._save_market_to_db` (desde `/market/today`) | `market_today` (caché por `championship_id`+`market_date`) |
| sofascore | (sync sofascore, `sofascore_sync.py`) | `sofascore_cache` |

Camino de lectura-desde-sync que YA existe y se puede reutilizar para recortar
llamadas en vivo:
- `market_today` ya cachea el catálogo de mercado del día (lo usa `/market/today`).
- `players` / `player_championship_stats` ya tienen el catálogo de jugadores
  sincronizado — candidato para que `/favorites/my` lea de Neon en vez de
  `get_championship_players` en vivo.
- `team_standings` tiene `team_value` por equipo/jornada — `/market/today` ya lo
  usa para evitar pedir standings.
- NO se observa una caché TTL por-campeonato genérica ni una capa de
  invalidación; la frescura hoy depende del sync en background (modal de 11
  pasos) y de `market_date` para `market_today`.

### Contratos de respuesta a preservar (un cambio futuro debe mantenerlos)

**`GET /api/v1/market/today`** → `{ success, championship_id, total_in_market,
computer_players, players[], user_info }`.
- `players[]` (campos que emite el backend): `player_id, slug, name, team,
  team_logo, position, position2, value, market_price, change, current_bid,
  current_bid_id, average, points, home_average, away_average, matches, photo,
  expiration, suggested_bid, bid_confidence, bid_based_on, overpay_pct,
  sofascore_id, sofascore_rating, sofascore_goals, sofascore_assists,
  sofascore_appearances, sofascore_url, starter_pct, is_favorite`.
- `user_info`: `balance, team_value, max_bid, active_bids_total,
  active_bids_count, available_for_bids`.

**`GET /api/v1/favorites/my`** → `{ success, players[], total }`.
- `players[]`: `player_id, name, slug, position, position2, team, team_logo,
  value, change, points, average, home_average, away_average, matches, rating,
  sofascore_rating, sofascore_url, starter_pct, status, position_order`.
- Orden: por `position_order` asc, luego `value` desc. Lista vacía → `{ success:
  true, players: [], total: 0 }`.

### Restricciones (memoria del proyecto — NO ampliar)

- **God-files**: `data_sync_service.py` (~15 KB) y `data_manager_v2.py` (~33 KB,
  + paquete `data_manager/`) NO se amplían; cualquier lógica nueva va tras una
  capa/función estrecha testeable (p. ej. un lector read-from-sync separado).
- **SQL-en-router**: el patrón de SQL crudo dentro de los endpoints
  (`market.py`, `balances.py`, `favorites.py`) es deuda heredada; NO se amplía el
  patrón (nuevo código tras función/capa estrecha).
- Excepciones de integración tipadas y propagadas (`integration_errors`), nunca
  `None` silencioso; nunca credenciales en mensajes/`repr`/`exc_info`.

### Scan Coverage

#### Analizado en profundidad (leído y entendido este run)

- `backend/app/api/v1/endpoints/market.py` — `get_market_today`,
  `_build_market_response`, `_calculate_suggested_bid`, `_get_user_team_id`,
  `place_bid`, `cancel_bid`; caché `market_today`, llamada en vivo de pujas.
- `backend/app/api/v1/endpoints/favorites.py` — `get_my_favorites` (hasta 3
  llamadas en vivo), `unfollow_player`, `mark_favorite`.
- `backend/app/api/v1/endpoints/balances.py` — `get_balances` (patrón rápido),
  `get_team_transactions`, `get_team_prizes`.
- `backend/app/api/v1/endpoints/roster.py` — `sell_players` (usa
  `get_matchday_standings` + `get_userteam_roster` en vivo).
- `backend/app/api/v1/endpoints/sync.py` — triggers de sync, `_check_phantoms`
  (standings + roster en vivo por equipo).
- `backend/app/services/data_sync_service.py` — `sync_all` y delegación a
  orquestadores `services/sync/*`.
- `backend/app/services/futmondo_client.py` — `_make_request` (timeout 15 s,
  errores tipados), `get_championship_players`, `get_matchday_standings`,
  `get_userteam_roster`, `get_market_players`.
- `backend/app/api/v1/endpoints/_helpers.py` — `get_user_futmondo_client`
  (sesión durable), `get_championship_config`, `clean_float`.
- `backend/app/api/v1/endpoints/_sofascore_helpers.py` — `build_sofascore_map`,
  `lookup_sofascore`, `calculate_starter_pct`, `get_current_matchday`.
- `backend/app/services/db_connection.py` — pool PostgreSQL/Neon,
  `get_connection`, `adapt_params`.

#### Solo ojeado (sin lectura profunda)

- `backend/app/stores/` (`task_repository.py`, `session_repository.py`) — por
  nombre/responsabilidad; no en la ruta de latencia de los 3 endpoints.
- `backend/app/services/` resto (`photo_service.py`, `assistant_service.py`,
  `session_service.py`, `task_service.py`, `sofascore_client.py`, `prizes/`,
  `analytics/`, `assistant/`, `data_manager/`, `data_initializer*`) — por
  firma/import; `assistant_service._save_market_to_db` referenciado desde
  `market.py`.
- `backend/app/services/sync/*` — orquestadores DDD referenciados desde
  `data_sync_service`, no abiertos fichero a fichero.
- `angular-app/src/app/features/market/` — preservado del store previo
  (CURRENT); re-confirmado por contrato, no re-leído línea a línea.

#### Dejado fuera (no abierto)

- Resto de `backend/` fuera de los endpoints/servicios de la ruta de latencia.
- Resto de `angular-app/` fuera de `features/market/`.
- Instalación de AI-DLC (`.kiro/`, `.claude/`, `.codex/`, `.cursor/`, `.aidlc/`,
  `aidlc/`) y secciones AI-DLC de `AGENTS.md`/`.gitignore`.
- Build outputs / deps / caches (`node_modules/`, `.angular/`, `dist/`,
  `coverage/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `ios/.build/`).
- `.github/workflows/`, `docs/`, `cron/`, `proxy/`, `spikes/`, `scripts/`.

## Handoff Summary

- **Intent-relevant finding**: la latencia de `/market/today` (~1.6 s) y
  `/favorites/my` (~3.4 s) frente a `/analytics/balances` (~0.4 s) se explica por
  el **número de llamadas HTTP en vivo a Futmondo por request**, no por Neon.
  `balances` hace **1** llamada y lee datos ya sincronizados; `market/today` hace
  **1 obligatoria** (pujas en vivo del usuario) pese a cachear el catálogo en
  `market_today`; `favorites/my` hace **2-3** encadenadas, la peor
  `get_championship_players` (`/5/league/championshipplayers`, lista completa) que
  se descarga entera solo para filtrar favoritos.
- **Palanca de mejora ya disponible**: existe un camino read-from-sync
  (`market_today`, `players`/`player_championship_stats`, `team_standings`); se
  puede leer el catálogo de jugadores desde Neon para evitar
  `get_championship_players` en vivo en `/favorites/my`, y evaluar cachear las
  pujas del usuario para `/market/today` (hoy siempre en vivo). NO existe una
  caché TTL por-campeonato genérica reutilizable.
- **Risks / follow-up**: cualquier cambio debe PRESERVAR el shape de
  `/market/today` y `/favorites/my` (documentados arriba), NO ampliar los
  god-files (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón
  SQL-en-router — el lector read-from-sync debe ir tras una capa/función estrecha
  testeable. La frescura de un read-from-sync depende del sync en background; una
  caché de pujas del usuario necesitaría invalidación tras `bid`/`cancelbid`.
