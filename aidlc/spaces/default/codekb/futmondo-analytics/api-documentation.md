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

Endpoints principales representativos (ver `README.md` para la lista de usuario):

| Endpoint | Método | Router | Descripción |
|----------|--------|--------|-------------|
| `/api/v1/sync/trigger` | POST | `sync` | Lanza sync async, devuelve `task_id` |
| `/api/v1/sync/task/{id}` | GET | `sync` | Polling del progreso del sync |
| `/api/v1/user/championships` | GET/POST/DELETE | `championships` | CRUD campeonatos del usuario |
| `/api/v1/analytics/balances` | GET | `balances` | Presupuestos por equipo |
| `/api/v1/market/today` | GET | `market` | Mercado + puja sugerida + Sofascore |
| `/api/v1/market/bid` | POST | `market` | Pujar por jugador |
| `/api/v1/player-finances/` | GET | `player_finances` | Finanzas por usuario |

> Nota de deuda: la mayoría de estos routers ejecutan SQL crudo inline
> (SQL-en-router). Ver `code-quality-assessment.md`.

## Integraciones externas (clientes salientes)

- **API Futmondo** — `backend/app/services/futmondo_client.py`. Validación de
  credenciales y fuente de la mayor parte de los datos de sync. Expone excepciones
  tipadas por modo de fallo (`Integration*Error`: `IntegrationBanError` fatal;
  `IntegrationTimeoutError` / `IntegrationUnparseableError` / `IntegrationRequestError`
  recuperables). Contrato de fallo caracterizado en `test_futmondo_client_characterization.py`.
- **API Sofascore** — `backend/app/services/sofascore_client.py` vía `curl_cffi`.
  Ratings deportivos.

## Superficie interna — `DataSyncService` (`data_sync_service.py`)

Contrato público **a preservar** en el refactor. Clase `DataSyncService` (L67).

### Las 10 operaciones `sync_*`

| Operación | Línea | Dominio |
|-----------|-------|---------|
| `sync_transactions` | L135 | transacciones |
| `sync_clauses` | L452 | cláusulas |
| `sync_punishments_bonuses` | L589 | castigos/bonificaciones |
| `sync_dream_teams_mvps` | L681 | dream teams / MVP |
| `sync_player_performance` | L842 | rendimiento de jugadores |
| `sync_rosters` | L1065 | plantillas |
| `sync_round_rankings` | L1215 | clasificación por jornada |
| `sync_players_full` | L1429 | jugadores (primero por FK) |
| `sync_match_odds` | L1564 | odds de partidos |
| `sync_prizes` | L1622 | premios (ya delega en `prizes/`) |

### Coordinador `sync_all()` (L1925–1955)

Coordinador **fino**: invoca los 10 `sync_*` en orden (players primero por FK) y
agrega los resultados en un dict `{dominio: resultado}`. Es el molde del `sync_all`
"thin" objetivo.

### `sync_prizes` — patrón de referencia (L1622)

Orquesta: (a) ingesta desde `FutmondoClient`; (b) materialización de
`RoundTeamEntry` / `PrizeConfig` (L~1817–1835); (c) delegación del cálculo puro a
`calculate_round_prizes(...)` de `prizes/calculator.py` (L1836); (d) persistencia
atómica vía `replace_team_prizes(db, championship_id, all_prizes_to_save, valid_matchdays)`
de `prizes/team_prizes_writer.py` (L1868). Manejo de errores tipados en
L~1888–1924, espejado en el router `sync.py`. Comportamiento a preservar:
pseudo-rondas adelantadas (matchday sintético negativo), gating
`round_fully_played` / `all(m.get("status")=="F")`, y throttling `time.sleep()`.
