# Developer Scan — `261023-sync-jugador-completo` (reverse-engineering enfocado)

> Scan enfocado (brownfield, scope `refactor`) sobre el flujo de datos de
> `sync_players_full` y la ruta de lectura de favoritos/mercado. Objetivo del
> intent: enriquecer `sync_players_full` para que persista la info COMPLETA por
> jugador (puntos totales, `change`/tendencia, logo de equipo, medias
> casa/fuera, partidos) en las tablas sincronizadas, de modo que `favorites/my`
> y `market/today` sirvan cada campo del contrato desde el sync, sin depender de
> `market_today` ni de llamadas en vivo.

## Developer Code Scan Results

### Scan Coverage

#### Analizado en profundidad (área enfocada)

- `backend/app/services/sync/players_full/orchestrator.py` —
  `PlayersFullSyncOrchestrator.sync()`: lee `client.get_championship_players`
  (`/5/league/championshipplayers`, `{players:[...]}`), arma `player_records` y
  `stats_payload`, persiste batch, limpia huérfanos, persiste stats por
  campeonato, sincroniza favoritos, escribe metadata. **Punto exacto donde se
  decide qué campos se extraen del objeto vivo.**
- `backend/app/services/sync/players_full/infrastructure/players_full_adapter.py`
  — `DataManagerPlayersFullAdapter`: delega verbatim a `DataManagerV2`
  (`save_players_batch`, `delete_orphan_players`,
  `save_player_championship_stats`, `update_sync_metadata`) y aloja el SQL crudo
  de `save_favorites` (DDL + delete-then-insert + `execute_values` Postgres).
- `backend/app/services/sync/players_full/domain/ports.py` —
  `PlayersFullSyncDataPort` (Protocol estructural, sin SQL): la superficie de
  persistencia que consume el orquestador.
- `backend/app/services/data_manager/players/` — `PlayersAdapter` (único con
  SQL), `PlayersService` (orquestador fino), `PlayersDataPort`: `save_players_batch`
  (INSERT/UPSERT a `players`: `player_id,name,role,role2,real_team_id,
  real_team_name,slug,photo_url,value`), `save_player_championship_stats`
  (UPSERT a `player_championship_stats`: owner\*, clause\*, `average_last_five`,
  `average_overall`), `delete_orphan_players` (`DELETE ... NOT IN` /
  `<> ALL(%s)`), `get_all_players_with_points` (LEFT JOIN `player_performance`
  con `SUM(points)`), `get_player_by_id`.
- `backend/app/services/data_manager/performance/` — `PerformanceAdapter`,
  `PerformanceDataPort`: `save_player_performance(_batch)` (UPSERT a
  `player_performance` por `championship_id,player_id,team_id,matchday` con
  `points,value,was_best_player`), `get_player_performance_history`. **Única
  fuente de `points` hoy** (por jornada×equipo).
- `backend/app/services/data_manager/schema_lifecycle/` —
  `SchemaLifecycleAdapter`, `SchemaLifecycleDataPort`: DDL verbatim. Confirma los
  esquemas de `players`, `player_performance`, y (en `ensure_schema_updates`)
  `player_championship_stats`. **Punto exacto donde habría que añadir columnas
  nuevas** (`points`, `change`, `home_average`, `away_average`, `matches`,
  `team_logo`) a `players`/`player_championship_stats` o a una tabla de stats más
  rica.
- `backend/app/services/sync_read/favorites_read.py` — `read_favorites`: lee
  favoritos agentes libres desde `player_championship_stats`+`players`, enriquece
  con `market_today` (por `player_id`+`market_date` de hoy) y con
  `player_performance` (SUM de `points`), más Sofascore. Devuelve
  `(players, has_synced)`; `has_synced=False` dispara el fallback en vivo.
- `backend/app/services/sync_read/market_read.py` — `read_market_catalog`
  (lee `market_today.raw_json` del día), `available_for_bids` (derivación pura).
- `backend/app/services/sync_read/__init__.py` — descripción de la capa narrow
  read-from-sync.
- `backend/app/services/futmondo_client.py` — `FutmondoClient`:
  `get_championship_players` (adapter que hoy solo propaga lo que trae
  `answer.players`; el orquestador lee `name/role/role2/teamId/team/slug/photo/
  value/clause/average/userteam*`), `_make_request` (timeout 15 s, errores
  tipados, nunca `None` silencioso salvo no-autenticado), y
  `get_player_summary`/`get_player_fullprofile`/`get_market_players` como
  fuentes alternativas candidatas por jugador.
- `backend/app/api/v1/endpoints/favorites.py` — `get_my_favorites` (fast-path
  `read_favorites` → fallback `_get_favorites_live`), `_get_favorites_live` (el
  pre-refactor: descarga catálogo vivo y lee `change/points/home/away/matches/
  logo` directamente del objeto por jugador), `mark`/`unfollow`.

#### Solo ojeado

- Resto de responsabilidades `data_manager/` (`prizes`, `clauses`,
  `transactions`, `teams_standings`, `dream_teams_mvp`, `market_roster`,
  `punishments_bonuses`, `users_stats_evolution`, `sync_metadata_cache`,
  `news_articles`, `match_odds`) — por firma/estructura DDD (puerto + adapter +
  servicio), fuera del área enfocada.
- `data_sync_service.py` / `data_manager_v2.py` (god-files) — por rol de facade;
  no abiertos línea a línea (restricción durable: NO ampliar).
- `assistant_service.py` (escribe `market_today` vía `_save_market_to_db`) y
  `_sofascore_helpers.py` — referenciados por su rol de fuente de
  `market_today`/Sofascore, no abiertos este run.

#### Dejado fuera

- Resto de `backend/` fuera del flujo player-sync; todo `angular-app/`;
  `.github/workflows/`, `docs/`, `cron/`, `proxy/`, `spikes/`, `scripts/`.
- Instalación de AI-DLC (`.kiro/`, `.claude/`, `.codex/`, `.cursor/`, `.aidlc/`,
  `aidlc/` workspace).
- Build outputs / deps / caches (`node_modules/`, `.angular/`, `dist/`,
  `coverage/`, `__pycache__/`, `.pytest_cache/`).

### Packages Found

- `backend/app/services/sync/players_full` — orquestador DDD del sync completo de
  jugadores (domain/infrastructure) — Python — ingesta + persistencia de
  jugadores.
- `backend/app/services/data_manager/{players,performance,schema_lifecycle}` —
  adapters DDD extraídos de `data_manager_v2` (único SQL por responsabilidad) —
  Python — acceso a datos de jugadores/rendimiento/esquema.
- `backend/app/services/sync_read` — capa narrow read-from-sync para
  `favorites/my` y `market/today` — Python — lectura desde Neon sincronizado.
- `backend/app/services/futmondo_client.py` — cliente de integración Futmondo —
  Python — llamadas en vivo con errores tipados.
- `backend/app/api/v1/endpoints/favorites.py` — router FastAPI de favoritos —
  Python — endpoint de lectura/mutación.

### Build System

- **Type**: pip (backend Python 3.12).
- **Config Files**: `backend/requirements.txt`, `ruff.toml`, `pytest.ini`
  (referenciados; no abiertos este run).
- **Build Dependencies**: `fastapi`, `requests`, `psycopg2` — ver
  `dependencies.md` (no modificadas por el scan).

### APIs Discovered

- **HTTP interno (FastAPI)**: `GET /api/v1/favorites/my`,
  `POST /api/v1/favorites/{mark,unfollow}` — contratos a preservar byte-for-byte.
- **Integración Futmondo (vía `FutmondoClient`)**:
  `/5/league/championshipplayers` (catálogo completo, fuente actual del sync),
  `/1/player/summary`, `/1/player/fullprofile`, `/1/market/players` — candidatas
  por jugador si el catálogo no trae los campos que faltan.

### Frameworks & Libraries

- FastAPI, `requests`, `psycopg2` (Neon PostgreSQL), `curl_cffi` (Sofascore) —
  sin cambios; ver `technology-stack.md`.

### Test Coverage

- **Test Directories**: `backend/tests/` (suite `pytest` characterization-first,
  fakes in-memory `conftest.py`); no abierta este run.
- **Test Frameworks**: `pytest` + `pytest-cov`.
- **Coverage Config**: presente (`--cov-fail-under`, ratchet solo sube).

### Code Quality Indicators

- **Linting**: `ruff` (`select E,F,I`, line 100), bloqueante en ambos gates.
- **CI/CD**: `ci.yml` (PR) + `fly-deploy.yml` job `verify` (push).
- **Documentation**: docstrings densos en los adapters/orquestadores del área
  (DDD con business-rule IDs `BRx.y`).

### Technical Debt Signals

- **God-files**: `data_manager_v2.py` (~33 KB) y `data_sync_service.py` (~15 KB)
  — los adapters delegan verbatim en ellos; NO ampliar (regla durable).
- **`delete_orphan_players`**: `DELETE ... NOT IN` / `<> ALL(%s)` sin reemplazo
  transaccional atómico — punto de corrupción conocido (deferido, OQ2).
- **`except Exception` no-fatales** en el orquestador (huérfanos, stats,
  favoritos) — degradan y continúan; registrados como deuda.
- **Fuente de campos dispersa**: `points` solo en `player_performance`;
  `change`/medias-detalle/`team_logo` solo en `market_today` — origen del gap.

## Data Flow — player-sync y el gap de campos (núcleo del intent)

### Flujo de escritura actual (`sync_players_full`)

```
FutmondoClient.get_championship_players  (/5/league/championshipplayers, {players:[...]})
   │  orquestador lee por jugador: name, role, role2, teamId, team, slug, photo, value,
   │                               clause{price,suggestedClause,date}, average{averageLastFive,average},
   │                               userteamId/userteam/userteamUserId/userId, fav
   ▼
PlayersFullSyncOrchestrator.sync()
   ├─ save_players_batch        → tabla `players`  (name,role,role2,real_team_id,
   │                                                 real_team_name,slug,photo_url,value)
   ├─ delete_orphan_players     → limpia `players` (NOT IN + sin historial)
   ├─ save_player_championship_stats → `player_championship_stats`
   │                                   (owner*, clause_price, suggested_clause,
   │                                    average_last_five, average_overall, clause_date)
   ├─ save_favorites            → `player_favorites` (championship_id,user_id,player_id)
   └─ update_sync_metadata      → `sync_metadata` (data_type='players')
```

### Campos que el sync NO extrae ni persiste (el gap)

Del objeto vivo, el orquestador **no** toca: `points` (puntos totales),
`change` (tendencia de valor), `home_average`/`away_average`/`matches` (medias
detalladas), ni `team_logo`. El adapter de `get_championship_players` tampoco
los expone: solo propaga `answer.players` tal cual, y el orquestador lee el
subconjunto de arriba.

### Dónde viven hoy esos campos (fuentes actuales, por eso el fallback)

- `points`: solo en `player_performance` (por jornada×equipo; `read_favorites`
  los agrega con `SUM(points)`). **Vacío para agentes libres** → SUM=0.
- `change`, `home_average`, `away_average`, `matches`, `team_logo`: solo en
  `market_today` (~25-30 jugadores del día, vía `assistant_service`). Ausentes
  para la mayoría de agentes libres.
- Verificado en prod (token fresco, 2026-10-23): de 33 favoritos, 32 sin
  `points/team/team_logo/change`; `value`+`average` sí (desde `players`/
  `player_championship_stats`).

### Capa de lectura (`sync_read`) y por qué expone el gap

`read_favorites` ya hace lo correcto con lo que hay: free-agent set desde
`player_championship_stats`+`players`, enriquece con `market_today` (left
lookup) y `player_performance` (SUM points), y cae a los defaults de la ruta
viva cuando faltan. El límite NO es la lectura: es que el **sync nunca persiste
esos campos para TODOS los jugadores**, así que para un agente libre fuera del
mercado del día el left-lookup no encuentra nada y devuelve defaults
(`change=0`, medias `None`, `matches=0`, `team_logo=''`). Enriquecer el sync
elimina esa dependencia de `market_today`/vivo.

## Handoff Summary

- **Intent-relevant finding**: El cuello no es la lectura sino la **escritura**.
  `PlayersFullSyncOrchestrator.sync()`
  (`backend/app/services/sync/players_full/orchestrator.py`) solo extrae
  `name/role/role2/teamId/team/slug/photo/value` + `clause*`/`average*` del
  objeto vivo de `/5/league/championshipplayers`, y persiste a `players` y
  `player_championship_stats`. **No persiste** `points`, `change`,
  `home_average`, `away_average`, `matches` ni `team_logo` para todos los
  jugadores; hoy solo existen en `player_performance` (points, por jornada, vacío
  para agentes libres) y `market_today` (el resto, ~30 jugadores/día). Por eso
  32/33 favoritos agentes libres salen con esos campos vacíos. El enriquecimiento
  requiere (a) añadir columnas en `players`/`player_championship_stats` (o una
  tabla de stats más rica) vía `schema_lifecycle` + re-sync, (b) extraer los
  campos en el orquestador, (c) que `read_favorites`/`market_read` los lean desde
  el sync en vez de `market_today`.
- **Risks / follow-up**:
  1. **INCÓGNITA CRÍTICA (para Functional Design)**: no hay evidencia en código
     de que `/5/league/championshipplayers` traiga `points`/`change`/`average`
     detallado/`team_logo` **por jugador** — el adapter actual solo lee
     `name/role/team/value/clause/average`. Si el catálogo NO los trae, la fuente
     debe ser otra (`/1/player/summary` o `/1/player/fullprofile` por jugador, o
     Sofascore), lo que cambia el diseño y el coste del sync. **Verificar con una
     llamada cruda (token server-side de Futmondo, no el JWT) antes de diseñar.**
  2. **Characterization-first (mandato durable)**: congelar con tests el
     comportamiento de `sync_players_full` en todas sus ramas antes de cambiarlo;
     hoy la producción del sync de jugadores tiene cobertura directa escasa.
  3. **God-files / SQL-en-router — NO ampliar**: los campos nuevos van tras los
     adapters DDD (`players_adapter`/`schema_lifecycle_adapter`) y una capa
     narrow testeable, nunca ensanchando `data_manager_v2.py`/
     `data_sync_service.py`.
  4. **Punto de corrupción `delete_orphan_players`** (`DELETE ... NOT IN`): si el
     cambio de esquema toca `players`, vigilar que la limpieza de huérfanos siga
     siendo segura (deferido, OQ2).
  5. **Contrato de respuesta intacto**: `favorites/my` y `market/today` deben
     seguir devolviendo el mismo shape byte-for-byte; el enriquecimiento cambia
     la FUENTE de los campos, no las claves/tipos.
  6. **Cambio de esquema + re-sincronización**: poblar las columnas nuevas exige
     un re-sync completo tras la migración; planificar en Functional Design.
