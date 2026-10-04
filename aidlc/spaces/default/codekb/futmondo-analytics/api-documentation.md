# API Documentation

## Superficies externas (HTTP)

### Auth (`backend/app/auth/routes.py`)

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/auth/login` | POST | Login con credenciales Futmondo → JWT access + refresh cookie |
| `/auth/refresh` | POST | Renovar access token desde la cookie HttpOnly |
| `/auth/logout` | POST | Revocar sesión |

### REST FastAPI v1 (`backend/app/api/v1/endpoints/`, 21 routers)

Todos los endpoints `/api/v1/*` requieren Bearer token. Routers:
`sync`, `market`, `balances`, `analytics`, `player_finances`, `transactions`,
`clausulable_players`, `roster`, `sofascore_sync`, `sofascore_detail`, `user`,
`user_stats`, `championships`, `favorites`, `phantoms`, `matchdays`,
`statistics`, `initialize`, `reset_db`, más helpers `_helpers.py` y
`_sofascore_helpers.py`.

### Sync router — `backend/app/api/v1/endpoints/sync.py` (foco del scan)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/sync/status` | GET | Estado del sync por data_type (lee `get_last_sync_metadata`) |
| `/api/v1/sync/last-sync` | GET | `MAX(last_sync_date)` por championship (SQL directo inline) |
| `/api/v1/sync/trigger` | POST | Lanza sync async (202 + `task_id`, thread daemon); 409 si hay sync en curso; `valid_types=("all","transactions","clauses","dream_teams","rosters","players")` |
| `/api/v1/sync/task/{task_id}` | GET | Polling del progreso (pending\|running\|completed\|failed) |

El worker `_run_sync_in_background(task_id, sync_type, …)` invoca el surface
público de `DataSyncService` con el **mismo orden y claves** que `sync_all` para
`sync_type=="all"`, actualizando `progress[step]` con las claves literales
(incluidas `team_standings`→`sync_round_rankings` y
`dream_teams`→`sync_dream_teams_mvps`), más `phantoms` (helper del router
`_check_phantoms`). El manejo DEGRADED de `prizes`/`phantoms` vive en el router
vía `record_degraded_step`. El router tiene SQL inline (`_check_phantoms`,
`get_last_sync_date`): patrón SQL-en-router que NO debe ampliarse.

> Resto de endpoints principales (market, balances, finances, championships) y
> deuda de SQL-en-router: ver `code-quality-assessment.md`.

## Integraciones externas (clientes salientes)

- **API Futmondo** — `backend/app/services/futmondo_client.py`. Validación de
  credenciales y fuente de la mayor parte de los datos de sync. Métodos consumidos
  por el sync: `get_pressroom_news`, `get_locker_news`, `get_match_list`,
  `get_matchday_standings`, `get_userteam_rounds`, `get_user_roundlineup`,
  `get_round_ranking`, `get_round_matches`, `get_dream_team`, `get_round_lineup`,
  `get_championship_players`, `get_player_fullprofile`, `get_userteam_roster`.
  Expone excepciones tipadas por modo de fallo (`IntegrationBanError` fatal;
  `IntegrationTimeoutError` / `IntegrationUnparseableError` / `IntegrationRequestError`
  recuperables); mantiene las credenciales fuera de sus propios errores.
- **API Sofascore** — `backend/app/services/sofascore_client.py` vía `curl_cffi`.
  Ratings deportivos.

## Superficie interna — `DataSyncService` (`data_sync_service.py`)

Contrato público **a preservar byte-a-byte** en el refactor (equivalencia
observable, FR5). Clase `DataSyncService`.

### Constructor y atributos públicos

- `DataSyncService(futmondo_client=None)` — `__init__` crea
  `DataManagerV2(skip_init=True)`, `ensure_championship_exists`, auth del cliente
  si no se inyecta. Atributos públicos: `self.dm`, `self.client`,
  `self.championship_id`, `self.league_id`, `self.user_id`.

### Las 10 operaciones `sync_*` (firma `() -> Dict`)

| Operación | Dominio | Clave en `sync_all` | Estado |
|-----------|---------|---------------------|--------|
| `sync_transactions` | transacciones | `transactions` | inline (helpers `_store_bids`/`_enrich_market_values`/`_find_price_at_date`) |
| `sync_clauses` | cláusulas | `clauses` | **extraído** (piloto) |
| `sync_punishments_bonuses` | castigos/bonificaciones | `punishments_bonuses` | inline |
| `sync_dream_teams_mvps` | dream teams / MVP | `dream_teams` | inline (usa `_find_championship`) |
| `sync_player_performance` | rendimiento de jugadores | `player_performance` | inline |
| `sync_rosters` | plantillas | `rosters` | inline (usa `_find_championship`) |
| `sync_round_rankings` | clasificación por jornada | `team_standings` | inline |
| `sync_players_full` | jugadores (primero por FK) | `players` | inline (usa `_save_favorites`) |
| `sync_match_odds` | odds de partidos | `match_odds` | **extraído** (piloto) |
| `sync_prizes` | premios | `prizes` | delega cálculo/escritura en `prizes/`; falta facade |

### Coordinador `sync_all()`

Coordinador **fino**: invoca los 10 `sync_*` en **orden FIJO** (players primero
por FKs) y agrega los resultados en un dict con **10 claves LITERALES**:
`players`, `transactions`, `clauses`, `punishments_bonuses`, `dream_teams`,
`player_performance`, `rosters`, `team_standings`, `match_odds`, `prizes`. Mapeo
no obvio (crítico): `players` ↔ `sync_players_full`,
`dream_teams` ↔ `sync_dream_teams_mvps`,
`team_standings` ↔ `sync_round_rankings`.

### Helpers privados consumidos por los dominios

`_find_championship()` (dream_teams + rosters),
`_store_bids`/`_enrich_market_values`/`_find_price_at_date` (transactions),
`_save_favorites` (players, toca `self.dm.db` crudo + `self.client.user_id`),
`_log_integration_failure` (prizes, log key=value sin credenciales).

### Forma del `SyncResult` (NO uniforme entre dominios — preservar por dominio)

La forma observable del resultado varía por dominio y debe reproducirse exacta
(cada orquestador la replica byte-a-byte):
- `transactions` / `clauses`: `{status, records_synced, last_sync_id, duration_seconds}`.
- `punishments_bonuses`: `{status, records_synced, last_sync_id, duration_seconds}`
  (`status = "success" if total_synced > 0 or from_id else "no_new_data"`).
- `dream_teams` / `rosters` / `player_performance`:
  `{status, records_synced, last_sync_matchday, duration_seconds}`
  (performance tiene dos retornos tempranos `no_new_data` que también escriben
  metadata).
- `round_rankings` (clave `team_standings`): forma DISTINTA —
  `{status, rounds_synced, records_synced, last_matchday, duration_seconds}`.
- `players_full`: `{status, records_synced, duration_seconds}` (sin `last_sync_*`).
- `match_odds` (ya delegado): `{status, records_synced, matchday, duration_seconds}`
  (happy); `{status:"error", error, duration_seconds}` (fallo).
- `prizes`: set de status más rico
  (`success|no_new_data|no_config|no_prizes_configured|no_standings|no_teams|no_rounds|error`),
  `{… rounds_processed, records_synced, stale_prizes_removed, duration_seconds}` —
  preservar TODOS los early-returns.

### `sync_match_odds` / `sync_clauses` — patrón de referencia ya aplicado

Delegación fina al `<Domain>SyncOrchestrator` (`sync/<domain>/orchestrator.py`),
que ingesta vía `FutmondoClient`, persiste a través del
`<Domain>SyncDataPort` (`domain/ports.py`) implementado por
`DataManager<Domain>Adapter` (`infrastructure/<domain>_adapter.py`, envuelve
`DataManagerV2` verbatim).

### `sync_prizes` — patrón de cálculo/escritura (falta facade uniforme)

Orquesta: (a) ingesta desde `FutmondoClient` + lectura de config vía SQL directo
sobre `get_db()`; (b) pseudo-rondas adelantadas (matchday sintético negativo),
gating `round_fully_played` / `all(m.get("status")=="F")`; (c) delegación del
cálculo puro a `calculate_round_prizes(...)` de `prizes/calculator.py`;
(d) persistencia atómica vía `replace_team_prizes(...)` de
`prizes/team_prizes_writer.py`. Manejo de errores tipado (fatal propaga /
recoverable degrada vía `_log_integration_failure`). Falta mover la orquestación
a `sync/<prizes>/` dejando la delegación delgada.
