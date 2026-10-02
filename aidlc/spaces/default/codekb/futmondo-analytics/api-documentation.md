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
| `/api/v1/sync/status` | GET | Estado del sync |
| `/api/v1/sync/last-sync` | GET | Última fecha de sync (`get_last_sync_date`, SQL inline) |
| `/api/v1/sync/trigger` | POST | Lanza sync async (202 + `task_id`, lanza thread) |
| `/api/v1/sync/task/{task_id}` | GET | Polling del progreso del sync |

El worker `_run_sync_in_background` invoca el surface público de `DataSyncService`
(`sync_players_full`, `sync_transactions`, `sync_clauses`,
`sync_punishments_bonuses`, `sync_dream_teams_mvps`, `sync_player_performance`,
`sync_rosters`, `sync_round_rankings`, `sync_match_odds`, `sync_prizes`) con el
**mismo orden y claves** que `sync_all`, más `phantoms` (helper del router
`_check_phantoms`). El router tiene SQL inline (`_check_phantoms`,
`get_last_sync_date`): patrón SQL-en-router que NO debe ampliarse.

> Resto de endpoints principales (market, balances, finances, championships) y
> deuda de SQL-en-router: ver versión previa del store y `code-quality-assessment.md`.

## Integraciones externas (clientes salientes)

- **API Futmondo** — `backend/app/services/futmondo_client.py`. Validación de
  credenciales y fuente de la mayor parte de los datos de sync. Métodos consumidos
  por el sync: `get_pressroom_news`, `get_locker_news`, `get_match_list`,
  `get_matchday_standings`, `get_userteam_rounds`, `get_user_roundlineup`,
  `get_round_ranking`, `get_round_matches`, `get_dream_team`, `get_round_lineup`,
  `get_championship_players`, `get_player_fullprofile`, `get_userteam_roster`.
  Expone excepciones tipadas por modo de fallo (`IntegrationBanError` fatal;
  `IntegrationTimeoutError` / `IntegrationUnparseableError` / `IntegrationRequestError`
  recuperables). Contrato caracterizado en `test_futmondo_client_characterization.py`.
- **API Sofascore** — `backend/app/services/sofascore_client.py` vía `curl_cffi`.
  Ratings deportivos.

## Superficie interna — `DataSyncService` (`data_sync_service.py`)

Contrato público **a preservar byte-a-byte** en el refactor (FR5). Clase
`DataSyncService`.

### Las 10 operaciones `sync_*`

| Operación | Línea | Dominio | Clave en `sync_all` |
|-----------|-------|---------|---------------------|
| `sync_transactions` | L135 | transacciones | `transactions` |
| `sync_clauses` | L452 | cláusulas | `clauses` |
| `sync_punishments_bonuses` | L589 | castigos/bonificaciones | `punishments_bonuses` |
| `sync_dream_teams_mvps` | L681 | dream teams / MVP | `dream_teams` |
| `sync_player_performance` | L842 | rendimiento de jugadores | `player_performance` |
| `sync_rosters` | L1065 | plantillas | `rosters` |
| `sync_round_rankings` | L1215 | clasificación por jornada | `team_standings` |
| `sync_players_full` | L1429 | jugadores (primero por FK) | `players` |
| `sync_match_odds` | L1564 | odds de partidos (ya delega) | `match_odds` |
| `sync_prizes` | L1585 | premios (delega en `prizes/`) | `prizes` |

### Coordinador `sync_all()` (L1888)

Coordinador **fino**: invoca los 10 `sync_*` en **orden fijo** (players primero
por FK) y agrega los resultados en un dict con **10 claves literales**: `players`,
`transactions`, `clauses`, `punishments_bonuses`, `dream_teams`,
`player_performance`, `rosters`, `team_standings`, `match_odds`, `prizes`. Mapeo
no obvio: `players` ↔ `sync_players_full`, `dream_teams` ↔ `sync_dream_teams_mvps`,
`team_standings` ↔ `sync_round_rankings`.

### Forma del `SyncResult` (NO uniforme entre dominios — preservar por dominio)

La forma observable del resultado varía por dominio y debe preservarse exacta:
- `match_odds` (ya delegado): `status` + `records_synced` + `matchday` +
  `duration_seconds` (happy); `status:error` + `error` + `duration_seconds` (fallo).
- `transactions` / `clauses`: devuelven `last_sync_id`.
- dominios basados en matchday: devuelven `last_sync_matchday`.
- `round_rankings`: devuelve `rounds_synced` + `last_matchday`.
- `prizes`: devuelve `rounds_processed` + `stale_prizes_removed`.

### `sync_match_odds` — patrón de referencia ya aplicado (L1564)

Delegación fina a `MatchOddsSyncOrchestrator` (`sync/match_odds/orchestrator.py`),
que ingesta vía `FutmondoClient`, persiste a través de `MatchOddsSyncDataPort`
(`domain/ports.py`) implementado por `DataManagerMatchOddsAdapter`
(`infrastructure/match_odds_adapter.py`, envuelve `DataManagerV2` verbatim).

### `sync_prizes` — patrón de referencia de cálculo/escritura (L1585)

Orquesta: (a) ingesta desde `FutmondoClient`; (b) delegación del cálculo puro a
`calculate_round_prizes(...)` de `prizes/calculator.py`; (c) persistencia atómica
vía `replace_team_prizes(...)` de `prizes/team_prizes_writer.py`. Comportamiento a
preservar: pseudo-rondas adelantadas (matchday sintético negativo), gating
`round_fully_played` / `all(m.get("status")=="F")`, throttling `time.sleep()`, y
manejo de errores tipado (fatal propaga / recoverable degrada).
