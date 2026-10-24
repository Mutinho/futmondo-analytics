# Dependencies — Futmondo Analytics

> Merge CURRENT. Grafo previo (latencia) **preservado**; se añade el grafo
> interno del flujo player-sync (sync + adapters DDD + `sync_read`).

## Dependencias externas (backend, relevantes)

- `fastapi`, `uvicorn` — framework web / ASGI.
- `requests` — `FutmondoClient` (llamadas en vivo a Futmondo, timeout 15 s).
- `curl_cffi` — `SofascoreClient` (ratings).
- `psycopg2` — pool de conexiones a Neon PostgreSQL (`execute_values` en los
  batch UPSERT).
- `PyJWT`, `python-dotenv` — auth / config.

(Fijadas a versión exacta en `backend/requirements.txt`; no se introducen
dependencias de pago. El intent no añade ninguna.)

## Grafo interno — player-sync (este run)

```
DataSyncService (god-file) → PlayersFullSyncOrchestrator
PlayersFullSyncOrchestrator → FutmondoClient.get_championship_players
                            → PlayersFullSyncDataPort (Protocol)
DataManagerPlayersFullAdapter (impl del puerto) → DataManagerV2 (god-file, verbatim)
                                                → db (SQL crudo de save_favorites)
PlayersAdapter / PerformanceAdapter / SchemaLifecycleAdapter → DataManagerV2.db (SQL verbatim)
favorites.py → sync_read.read_favorites → db_connection
             → FutmondoClient.get_championship_players (solo en fallback vivo)
sync_read.read_favorites → players + player_championship_stats + market_today
                         + player_performance + sofascore_cache (_sofascore_helpers)
sync_read.market_read    → market_today.raw_json
FutmondoClient           → requests, integration_errors
db_connection            → psycopg2 (pool), core.config.DATABASE_URL
```

## Grafo interno — ruta de latencia (preservado)

```
market.py        → _helpers.get_user_futmondo_client → session_service → FutmondoClient
                 → _sofascore_helpers (sofascore_cache) → db_connection
                 → assistant_service._save_market_to_db (fallback caché)
balances.py      → _helpers.{get_user_futmondo_client,get_championship_config}
                 → FutmondoClient.get_matchday_standings → db_connection
```

## Dependencias cruzadas / acoplamientos a vigilar

- `sync_players_full` acopla su persistencia a `DataManagerV2` vía el adapter
  (delegación verbatim); los campos nuevos no deben ensanchar el god-file sino ir
  tras `PlayersAdapter`/`SchemaLifecycleAdapter`.
- `read_favorites` depende de `market_today` para `change/medias-detalle/logo`
  (acoplamiento que el intent busca romper enriqueciendo el sync) y de
  `player_performance` para `points`.
- `market_today` lo puebla `assistant_service`, no `sync_players_full`: hoy son
  dos rutas de escritura distintas para el mismo jugador.
- Los endpoints acoplan SQL crudo a `db_connection` (SQL-en-router, deuda); el
  SQL nuevo va en `sync_read`/adapters, nunca en el router.

## Referencias circulares

Ninguna crítica observada. Los imports de `assistant_service`, de los
orquestadores `services/sync/*` y de `DataManagerV2` dentro de los adapters son
lazy (dentro de función / `__init__` con default), para no alterar el grafo de
import de los facades.
