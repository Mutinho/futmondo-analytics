# Code Structure — Futmondo Analytics

> Merge CURRENT. Organización previa **preservada**; se añade la estructura DDD
> del sync de jugadores y la capa `sync_read` (intent
> `261023-sync-jugador-completo`). Detalle de componentes en
> `component-inventory.md`.

## Organización de alto nivel

```
backend/app/
  api/v1/endpoints/   # routers FastAPI (SQL-en-router heredado)
  services/
    sync/             # orquestadores DDD por tipo de dato
      players_full/   #   domain/ports.py + infrastructure/players_full_adapter.py + orchestrator.py
    sync_read/        # capa narrow read-from-sync (favorites_read, market_read)
    data_manager/     # adapters DDD extraídos del god-file (uno por responsabilidad)
      players/        #   domain/ports.py + infrastructure/players_adapter.py + application/players.py
      performance/    #   idem (player_performance)
      schema_lifecycle/ # idem (DDL + bootstrap de campeonatos)
      {prizes,clauses,transactions,teams_standings,dream_teams_mvp,market_roster,...}
  stores/             # repositorios durables (task, session)
  auth/, security/, core/, models/
angular-app/src/app/
  features/market/    # vista de Mercado
  features/budget/    # Presupuesto
  core/               # servicios, interceptors, guards
```

## Patrón DDD por responsabilidad (sync de jugadores + data_manager)

Cada responsabilidad extraída del god-file sigue tres piezas:
- `domain/ports.py` — `typing.Protocol` estructural, **sin SQL ni framework**
  (la superficie que consume el orquestador).
- `infrastructure/<x>_adapter.py` — **único módulo con SQL**; delega verbatim a
  `DataManagerV2(skip_init=True)` (o aloja el SQL crudo movido verbatim, como
  `save_favorites`).
- `application/<x>.py` u `orchestrator.py` — orquestador fino que coordina sobre
  el puerto, sin SQL.

## Clasificación de ficheros (área player-sync — profundidad este run)

| Fichero | Categoría | Rol |
|---|---|---|
| `services/sync/players_full/orchestrator.py` | Service (orquestador DDD) | `PlayersFullSyncOrchestrator.sync()`: ingesta + persistencia; punto donde se decide qué campos se extraen |
| `services/sync/players_full/infrastructure/players_full_adapter.py` | Infrastructure (SQL) | delega a `DataManagerV2`; SQL crudo de `save_favorites` |
| `services/sync/players_full/domain/ports.py` | Domain (Protocol) | `PlayersFullSyncDataPort` |
| `services/data_manager/players/infrastructure/players_adapter.py` | Infrastructure (SQL) | `save_players_batch`→`players`, `save_player_championship_stats`→`player_championship_stats`, `delete_orphan_players`, `get_all_players_with_points` |
| `services/data_manager/players/{domain/ports.py,application/players.py}` | Domain/Application | puerto + `PlayersService` |
| `services/data_manager/performance/infrastructure/performance_adapter.py` | Infrastructure (SQL) | `save_player_performance(_batch)`→`player_performance` (única fuente de `points`) |
| `services/data_manager/schema_lifecycle/infrastructure/schema_lifecycle_adapter.py` | Infrastructure (DDL) | DDL de `players`/`player_performance`/`player_championship_stats`; punto donde añadir columnas nuevas |
| `services/sync_read/favorites_read.py` | Service (read-from-sync) | `read_favorites`: lee del sync, enriquece, decide `has_synced` |
| `services/sync_read/market_read.py` | Service (read-from-sync) | `read_market_catalog`, `available_for_bids` |
| `services/futmondo_client.py` | Adapter | `get_championship_players`, `_make_request` (timeout 15 s, errores tipados); candidatos por jugador: `get_player_summary`, `get_player_fullprofile`, `get_market_players` |
| `api/v1/endpoints/favorites.py` | Controller/Handler | `/my` (fast-path sync + fallback vivo), `/mark`, `/unfollow` |

## Clasificación de ficheros (ruta de latencia — preservado del store previo)

| Fichero | Categoría | Rol en la latencia |
|---|---|---|
| `api/v1/endpoints/market.py` | Controller/Handler | `/today` lee caché + 1 llamada en vivo (pujas) |
| `api/v1/endpoints/balances.py` | Controller/Handler | patrón rápido: 1 llamada en vivo + reads sincronizados |
| `api/v1/endpoints/roster.py` | Controller/Handler | usa standings+roster en vivo |
| `api/v1/endpoints/sync.py` | Controller/Handler | triggers de sync; `_check_phantoms` |
| `api/v1/endpoints/_helpers.py` | Utility | `get_user_futmondo_client`, `get_championship_config`, `clean_float` |
| `api/v1/endpoints/_sofascore_helpers.py` | Utility | `build_sofascore_map`, `calculate_starter_pct` (lee `sofascore_cache`) |
| `services/data_sync_service.py` | Service (god-file, NO ampliar) | `sync_all` delega en orquestadores `services/sync/*` |
| `services/data_manager_v2.py` | Service (god-file, NO ampliar) | acceso a datos; parte extraída en `data_manager/` |
| `services/sofascore_client.py` | Adapter | ratings Sofascore |
| `services/db_connection.py` | Config/DAO | pool PostgreSQL/Neon, `adapt_params` |
| `stores/{task,session}_repository.py` | Repository | persistencia durable (ojeado) |

## Patrones de código observados

- **DDD por responsabilidad**: puerto (Protocol) + adapter (único SQL, delega
  verbatim) + servicio/orquestador fino. Permite extraer de los god-files sin
  reescribir el comportamiento.
- **SQL-en-router** (deuda heredada): SQL crudo con `db.adapt_params("? → %s")`
  dentro de los endpoints. NO ampliar.
- **Caché por fecha**: `market_today` keyed por `championship_id` + `market_date`.
- **UPSERT batch**: `execute_values` (Postgres) / `executemany` (SQLite), con
  rama por `db_type` repetida verbatim en cada adapter.
- **Un `get_connection()` por request/transacción**.
- **Errores de integración tipados**: `_make_request` lanza
  `IntegrationTimeout/Request/UnparseableError`, nunca `None` silencioso (salvo
  no-autenticado explícito).
- **Punto de corrupción conocido**: `delete_orphan_players` usa `DELETE ... NOT
  IN` / `<> ALL(%s)` sin reemplazo transaccional atómico (deferido, OQ2).
