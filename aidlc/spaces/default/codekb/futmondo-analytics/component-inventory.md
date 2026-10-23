# Component Inventory — Futmondo Analytics

> Merge CURRENT: se **preservan** los componentes del store previo
> (`261020-mercado-pujas`) y se **extiende** con los de la ruta de latencia de
> este run. Los nombres de componente son verbatim (comparación literal del
> guard de rerun).

## Backend — ruta de latencia (analizada en profundidad este run)

| Componente | Fichero | Responsabilidad | Latencia |
|---|---|---|---|
| Market router | `backend/app/api/v1/endpoints/market.py` | `GET /today` (caché `market_today` + 1 llamada en vivo de pujas), `POST /bid`, `POST /cancelbid`; puja sugerida desde `transactions`; enriquece Sofascore/favoritos | ~1.6 s (1 llamada en vivo obligatoria) |
| Favorites router | `backend/app/api/v1/endpoints/favorites.py` | `GET /my` (favoritos agentes libres + Sofascore), `POST /unfollow`, `POST /mark`; 2-3 llamadas Futmondo en vivo | ~3.4 s (el más lento) |
| Balances router | `backend/app/api/v1/endpoints/balances.py` | `GET /balances` (saldo/valor/rendimiento por equipo), `/balances/{team_id}`, `/prizes/{team_id}`; 1 llamada en vivo + reads sincronizados | ~0.4 s (patrón rápido de referencia) |
| Roster router | `backend/app/api/v1/endpoints/roster.py` | `POST /sell` (putonmarket + toggleplayer); usa standings+roster en vivo | mismo patrón de llamadas en vivo |
| Sync router | `backend/app/api/v1/endpoints/sync.py` | Triggers de sync, estado por pasos, `_check_phantoms` (standings+roster en vivo por equipo) | — (pre-sincroniza Neon) |
| Data sync service | `backend/app/services/data_sync_service.py` (~15 KB) | **God-file heredado (NO ampliar)**: `sync_all` delega en orquestadores `services/sync/*` que escriben Neon | fuente del camino read-from-sync |
| Data manager | `backend/app/services/data_manager_v2.py` (~33 KB) + `data_manager/` | **God-file heredado (NO ampliar)**; acceso a datos, parte extraída a adapters DDD | — |
| Futmondo client | `backend/app/services/futmondo_client.py` (~27 KB) | Cliente Futmondo: `_make_request` (timeout 15 s, errores tipados), `get_championship_players`, `get_matchday_standings`, `get_userteam_roster`, `get_market_players` | **origen de las llamadas en vivo** |
| Sofascore client | `backend/app/services/sofascore_client.py` (~16 KB) | Cliente Sofascore (ratings); alimenta `sofascore_cache` | — |
| Endpoint helpers | `backend/app/api/v1/endpoints/_helpers.py` | `get_user_futmondo_client` (sesión durable), `get_championship_config`, `clean_float` | resuelve sesión sin llamada extra |
| Sofascore helpers | `backend/app/api/v1/endpoints/_sofascore_helpers.py` | `build_sofascore_map`, `lookup_sofascore`, `calculate_starter_pct`, `get_current_matchday` (lee `sofascore_cache`/`team_standings`) | lecturas baratas |
| DB connection | `backend/app/services/db_connection.py` | Pool PostgreSQL/Neon (`ThreadedConnectionPool` 5-20), `get_connection`, `adapt_params` | reads baratos |
| Task store / repo | `backend/app/stores/task_repository.py` | Tareas de sync durables (ojeado) | — |
| Session store / repo | `backend/app/stores/session_repository.py` | Sesión durable + rehidratación con handle cifrado (ojeado) | — |

### Datos pre-sincronizados en Neon (tablas, por orquestador)

`sync_players_full`→`players`/`player_championship_stats`/`player_favorites`;
`sync_transactions`→`transactions`; `sync_round_rankings`→`team_standings`
(incl. `team_value`); `sync_prizes`→`team_prizes`; `sync_rosters`→rosters;
`sync_dream_teams_mvps`, `sync_player_performance`, `sync_clauses`,
`sync_punishments_bonuses`, `sync_match_odds`; catálogo de mercado del día→
`market_today` (vía `assistant_service._save_market_to_db`); ratings→
`sofascore_cache`.

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

- `backend/app/api/v1/endpoints/{market,favorites,balances,roster,sync,_helpers,_sofascore_helpers}.py`
- `backend/app/services/{data_sync_service,data_manager_v2,futmondo_client,sofascore_client,db_connection}.py`
- `backend/app/services/sync/*` (orquestadores DDD, referenciados)
- `backend/app/stores/{task,session}_repository.py`
- `angular-app/src/app/features/market/*` (preservado del store previo)
- Store previo `261020-mercado-pujas` (prosa iOS/Budget/auth/Sofascore detail preservada)

## Assumptions & Open Questions

- Tamaños de servicio en KB desde el listado de directorio (bytes), no por
  líneas. Orquestadores `services/sync/*` referenciados por import, no abiertos
  fichero a fichero (profundidad Minimal).
- Nombres de tablas de Neon inferidos del SQL de los endpoints y las firmas de
  los orquestadores de sync; el esquema DDL no se abrió este run.
- No existe una caché TTL por-campeonato genérica ni capa de invalidación
  observada; la frescura depende del sync en background y de `market_date`.
