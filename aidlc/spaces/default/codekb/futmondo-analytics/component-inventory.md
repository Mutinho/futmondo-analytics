# Component Inventory — Futmondo Analytics

> Merge CURRENT: se **preservan** los componentes del store previo
> (`261023-latencia-market-favorito` / `261020-mercado-pujas`) y se **extiende**
> con los del flujo player-sync de este run. Los nombres de componente son
> verbatim (comparación literal del guard de rerun).

## Backend — player-sync (analizado en profundidad este run)

| Componente | Fichero | Responsabilidad |
|---|---|---|
| Players full sync orchestrator | `backend/app/services/sync/players_full/orchestrator.py` | `PlayersFullSyncOrchestrator.sync()`: lee `get_championship_players`, arma records/stats, persiste batch + stats + favoritos + metadata, limpia huérfanos. **No extrae points/change/medias-detalle/logo** |
| Players full sync adapter | `backend/app/services/sync/players_full/infrastructure/players_full_adapter.py` | `DataManagerPlayersFullAdapter`: delega verbatim a `DataManagerV2`; aloja el SQL crudo de `save_favorites` (DDL + delete-then-insert + `execute_values`) |
| Players full sync port | `backend/app/services/sync/players_full/domain/ports.py` | `PlayersFullSyncDataPort` (Protocol estructural, sin SQL) |
| Players data adapter | `backend/app/services/data_manager/players/infrastructure/players_adapter.py` | `PlayersAdapter` (único SQL): `save_players_batch`→`players`, `save_player_championship_stats`→`player_championship_stats`, `delete_orphan_players` (NOT IN/`<> ALL`), `get_all_players_with_points` (LEFT JOIN `player_performance`), `get_player_by_id` |
| Players service | `backend/app/services/data_manager/players/application/players.py` | `PlayersService`: orquestador fino sobre `PlayersDataPort` |
| Players data port | `backend/app/services/data_manager/players/domain/ports.py` | `PlayersDataPort` (Protocol) |
| Performance data adapter | `backend/app/services/data_manager/performance/infrastructure/performance_adapter.py` | `PerformanceAdapter`: `save_player_performance(_batch)`→`player_performance` (única fuente de `points`), `get_player_performance_history` |
| Performance data port | `backend/app/services/data_manager/performance/domain/ports.py` | `PerformanceDataPort` (Protocol) |
| Schema lifecycle adapter | `backend/app/services/data_manager/schema_lifecycle/infrastructure/schema_lifecycle_adapter.py` | `SchemaLifecycleAdapter`: DDL verbatim de `players`/`player_performance`/`player_championship_stats` (`ensure_schema_updates`); punto donde añadir columnas nuevas |
| Schema lifecycle service | `backend/app/services/data_manager/schema_lifecycle/application/schema_lifecycle.py` | `SchemaLifecycleService`: orquestador fino sobre `SchemaLifecycleDataPort` |
| Favorites read-from-sync | `backend/app/services/sync_read/favorites_read.py` | `read_favorites`: free-agents desde `player_championship_stats`+`players`, enriquece con `market_today`+`player_performance`+Sofascore; devuelve `(players, has_synced)` |
| Market read-from-sync | `backend/app/services/sync_read/market_read.py` | `read_market_catalog` (lee `market_today.raw_json`), `available_for_bids` (derivación pura) |
| Favorites router | `backend/app/api/v1/endpoints/favorites.py` | `GET /my` (fast-path `read_favorites` + fallback `_get_favorites_live`), `POST /mark`, `POST /unfollow` |
| Futmondo client | `backend/app/services/futmondo_client.py` (~27 KB) | `get_championship_players`, `get_player_summary`, `get_player_fullprofile`, `get_market_players`, `get_userteam_roster`; `_make_request` (timeout 15 s, errores tipados) |

### Tablas de Neon relevantes al player-sync (DDL confirmada este run)

- `players(player_id PK, name, role, real_team_id, real_team_name, slug,
  photo_url, photo_local_path, created_at, last_updated)` — el batch UPSERT
  añade también `role2` y `value`. **Sin** columnas points/change/logo/medias.
- `player_championship_stats(id PK, championship_id, player_id, owner_team_id,
  owner_team_name, owner_user_id, clause_price, suggested_clause,
  average_last_five, average_overall, clause_date?, updated_at,
  UNIQUE(championship_id, player_id))`.
- `player_performance(id PK, championship_id, player_id, team_id, matchday,
  points, value, minutes_played, goals, assists, yellow_cards, red_cards,
  was_starter, was_best_player, recorded_at, UNIQUE(championship_id,player_id,
  team_id,matchday))` — **única fuente de `points`** (por jornada×equipo).
- `player_favorites(id PK, championship_id, user_id, player_id, synced_at,
  UNIQUE(championship_id,user_id,player_id))` (DDL en el adapter de favoritos).
- `market_today` (externa a este DDL, poblada por `assistant_service`): única
  fuente de `change/home_average/away_average/matches/team_logo` por jugador.

## Backend — ruta de latencia (preservado del store previo)

| Componente | Fichero | Responsabilidad | Latencia |
|---|---|---|---|
| Market router | `backend/app/api/v1/endpoints/market.py` | `GET /today` (caché `market_today` + 1 llamada en vivo de pujas), `POST /bid`, `POST /cancelbid`; puja sugerida desde `transactions`; enriquece Sofascore/favoritos | ~1.6 s |
| Balances router | `backend/app/api/v1/endpoints/balances.py` | `GET /balances` (saldo/valor/rendimiento por equipo), `/balances/{team_id}`, `/prizes/{team_id}` | ~0.4 s |
| Roster router | `backend/app/api/v1/endpoints/roster.py` | `POST /sell` (putonmarket + toggleplayer); usa standings+roster en vivo | — |
| Sync router | `backend/app/api/v1/endpoints/sync.py` | Triggers de sync, estado por pasos, `_check_phantoms` | — |
| Data sync service | `backend/app/services/data_sync_service.py` (~15 KB) | **God-file heredado (NO ampliar)**: `sync_all` delega en orquestadores `services/sync/*` | — |
| Data manager | `backend/app/services/data_manager_v2.py` (~33 KB) + `data_manager/` | **God-file heredado (NO ampliar)**; acceso a datos, parte extraída a adapters DDD | — |
| Sofascore client | `backend/app/services/sofascore_client.py` (~16 KB) | Cliente Sofascore (ratings); alimenta `sofascore_cache` | — |
| Endpoint helpers | `backend/app/api/v1/endpoints/_helpers.py` | `get_user_futmondo_client` (sesión durable), `get_championship_config`, `clean_float` | — |
| Sofascore helpers | `backend/app/api/v1/endpoints/_sofascore_helpers.py` | `build_sofascore_map`, `lookup_sofascore`, `calculate_starter_pct`, `get_current_matchday` | — |
| DB connection | `backend/app/services/db_connection.py` | Pool PostgreSQL/Neon (`ThreadedConnectionPool` 5-20), `get_connection`, `adapt_params` | — |
| Task store / repo | `backend/app/stores/task_repository.py` | Tareas de sync durables (ojeado) | — |
| Session store / repo | `backend/app/stores/session_repository.py` | Sesión durable + rehidratación con handle cifrado (ojeado) | — |

### Datos pre-sincronizados en Neon (tablas, por orquestador)

`sync_players_full`→`players`/`player_championship_stats`/`player_favorites`;
`sync_transactions`→`transactions`; `sync_round_rankings`→`team_standings`
(incl. `team_value`); `sync_prizes`→`team_prizes`; `sync_rosters`→rosters;
`sync_dream_teams_mvps`, `sync_player_performance`→`player_performance`,
`sync_clauses`, `sync_punishments_bonuses`, `sync_match_odds`; catálogo de
mercado del día→`market_today` (vía `assistant_service._save_market_to_db`);
ratings→`sofascore_cache`.

## Backend — store previo (preservado)

| Componente | Fichero | Responsabilidad |
|---|---|---|
| FastAPI app + AuthMiddleware | `app/main.py` | CORS, auth sobre `/api/v1/*`, routers, fotos estáticas, `/health` |
| Auth routes | `app/auth/routes.py` | `/auth/login`, `/refresh`, `/logout`; cookie `HttpOnly`; auto-detección de campeonatos |
| JWT utils | `app/auth/jwt_utils.py` | access 60 min / refresh 30 días HS256; `hash_token` |
| Token store | `app/auth/token_store.py` | `app_users`, `refresh_tokens`, `user_championships`; migraciones idempotentes |
| Session service / repo | `app/services/session_service.py`, `app/stores/session_repository.py` | Sesión durable + rehidratación cifrada |
| Credential protection | `app/security/credential_protection.py` | Cifra/descifra handle de re-auth (sin password en claro) |
| Integration errors | `app/services/integration_errors.py` | Jerarquía tipada recoverable/fatal; sin material de credencial |
| Photo service | `app/services/photo_service.py` (~23 KB) | Descarga/servido de fotos de jugador |
| Config | `app/core/config.py` | Env vars; `resolve_jwt_secret` (fail-fast); `FUTMONDO_CRED_KEY` |
| Sofascore detail router | `app/api/v1/endpoints/sofascore_detail.py` | `GET /player/{name}` (router `/api/v1/sofascore`); lee `sofascore_cache` |

## Frontend — Feature Market / Mercado (preservado del store; re-confirmado por contrato)

| Componente | Fichero | Responsabilidad |
|---|---|---|
| MarketComponent | `src/app/features/market/market.component.ts` | Pantalla de Mercado (standalone, `OnPush`); `loadData()`→`GET /api/v1/market/today`; `confirmBid()`/`cancelBid()` proxy; interface `MarketPlayer` (~28 campos) |
| BidDialogComponent | `src/app/features/market/bid-dialog.component.ts` | Diálogo de puja; validación mín=`marketPrice`/máx=`maxBid`/`>0` |
| ConfirmDialogComponent | `src/app/features/market/confirm-dialog.component.ts` | Confirmación genérica (cancelar puja); devuelve `boolean` |
| SofascoreDetailDialogComponent | `src/app/features/market/sofascore-detail-dialog.component.{ts,html}` | Stats Sofascore; `GET /api/v1/sofascore/player/{name}` (NO `/market/*`) |

## Frontend — store previo (preservado, resumen)

`AuthService`, `authInterceptor`, `authGuard`, `LoginComponent`,
`ChampionshipService`, `BudgetService`, feature `budget/*`, capa nativa iOS
`FutmondoKit`/`FutmondoApp` y su DesignSystem — sin cambios en este run (ver
store previo para detalle completo).

## Modelo de datos de auth (tablas)

- `app_users(id PK, futmondo_email UNIQUE, futmondo_user_id, display_name, created_at, last_login)`
- `refresh_tokens(token_hash PK, user_id FK, expires_at, revoked, created_at)`
- `user_championships(user_id, championship_id, ..., futmondo_team_id, PK(user_id, championship_id))`

## Sources

- `backend/app/services/sync/players_full/{orchestrator.py,infrastructure/players_full_adapter.py,domain/ports.py}`
- `backend/app/services/data_manager/{players,performance,schema_lifecycle}/**`
- `backend/app/services/sync_read/{favorites_read,market_read,__init__}.py`
- `backend/app/services/futmondo_client.py`
- `backend/app/api/v1/endpoints/favorites.py`
- `backend/app/api/v1/endpoints/{market,balances,roster,sync,_helpers,_sofascore_helpers}.py` (preservado)
- `backend/app/services/{data_sync_service,data_manager_v2,sofascore_client,db_connection}.py` (preservado)
- `angular-app/src/app/features/market/*` (preservado del store previo)
- Stores previos `261023-latencia-market-favorito` / `261020-mercado-pujas`
  (prosa de latencia, iOS/Budget/auth/Sofascore detail preservada)

## Assumptions & Open Questions

- Tamaños de servicio en KB desde el listado de directorio (bytes), no por
  líneas.
- Los adapters `data_manager/*` delegan verbatim en `DataManagerV2`; su SQL se
  leyó directamente del adapter, no del god-file.
- La DDL de `market_today` no está en `schema_lifecycle` (la crea/pobla
  `assistant_service`); se infiere de los SELECT de `favorites_read`/`market_read`.
- **INCÓGNITA (Functional Design)**: ¿trae `/5/league/championshipplayers` los
  campos que faltan (points/change/medias-detalle/logo) por jugador? El adapter
  actual solo lee un subconjunto; verificar con llamada cruda (token
  server-side).
