# Developer Code Scan — reverse-engineering (eslabón 1)

Intent: `260918-matchday-prizes-calc` — Mejora del cálculo de premios de las jornadas
(matchday prizes). Brownfield, FOCUSED SCAN sobre el área de premios/finanzas.

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply**:
  - backend/app/api/v1/endpoints/player_finances.py
  - backend/app/api/v1/endpoints/matchdays.py
  - backend/app/api/v1/endpoints/analytics.py
  - backend/app/api/v1/endpoints/balances.py
  - backend/app/services/analytics_service.py
  - backend/app/models/models.py
  - backend/tests/test_analytics_service.py
  - backend/tests/test_finance_characterization.py
  - angular-app/src/app/features/finances/finances.component.ts
  - angular-app/src/app/features/budget/budget-overview/budget-overview.component.ts
  - angular-app/src/app/features/budget/budget-overview/prizes-dialog.component.ts
  - angular-app/src/app/features/calculator/calculator.component.ts
- **Skimmed only** (contratos/dependencias del área, NO cobertura profunda):
  - backend/app/services/data_sync_service.py — SOLO el método `sync_prizes()` (~líneas 1577-1885),
    donde vive realmente TODA la fórmula de premios. **Es el fichero clave del intent y NO está en el
    snapshot de deep-scan.** God-file (~1925 líneas / ~84 KB).
  - backend/app/api/v1/endpoints/_helpers.py — `get_user_futmondo_client`, `get_championship_config`.
  - angular-app/src/app/features (resto del árbol, para ubicar sub-features de finanzas/analytics).
  - backend/pytest.ini — config de test/cobertura del área.
  - backend/tests/ (listado) — para inventariar qué existe y qué falta en el área de premios.

### Packages Found

- backend/app/api/v1/endpoints — capa HTTP (FastAPI) — Python — routers de finanzas/premios/analytics/saldos.
- backend/app/services — lógica de negocio y acceso a datos — Python — `analytics_service` (analítica derivada)
  y `data_sync_service` (**productor de la tabla `team_prizes`**, única fuente de verdad de premios).
- backend/app/models — modelos Pydantic de request/response — Python — DTOs; **no** hay modelo de premios aquí.
- angular-app/src/app/features/{finances,budget,calculator,analytics} — UI — TypeScript/Angular 22 — consumo y
  presentación de premios/finanzas/saldos.

### APIs Discovered

- REST (FastAPI) — backend/app/api/v1/endpoints/player_finances.py — `GET /` (finanzas agregadas por usuario;
  bajo prefijo `/api/v1/player-finances`).
- REST — backend/app/api/v1/endpoints/balances.py — `GET /balances`, `GET /balances/{team_id}`,
  **`GET /prizes/{team_id}`** (desglose de premios por jornada, montado bajo el prefijo `analytics` según el
  frontend: `GET /api/v1/analytics/prizes/{team_id}`).
- REST — backend/app/api/v1/endpoints/analytics.py — ~12 endpoints de analítica avanzada
  (trends, classification-full, custom-classification, heatmap, players/form, players/value-trend,
  users/consistency, users/market-activity, market/watchlist, clauses/network, opportunities/streaks,
  projections/matchday). Delegan en `AnalyticsService`; `classification-full` y `watchlist` llevan SQL inline.
- REST — backend/app/api/v1/endpoints/matchdays.py — `GET /teams`, `GET /teams/{team_id}/rounds`,
  `GET /evolution` (evolución por jornada; DB-first con fallback a la API de Futmondo).

### FÓRMULA de premios de jornada (hallazgo central del intent)

Todo el dinero de premios se PRECALCULA en `data_sync_service.sync_prizes()` y se persiste en la tabla
**`team_prizes(championship_id, team_id, matchday, ranking_prize, mvp_prize, position, points_prize,
dream_team_prize, synced_at)`** (UPSERT por `ON CONFLICT (championship_id, team_id, matchday)`). Los endpoints
**solo leen y suman**; no recalculan. Config de premios leída de `user_championships`:
`money_per_ranking`, `mvp_bonus`, `ranking_mode` (`flop`|otro), `users_to_rank`, `money_per_point`,
`dream_team_bonus`.

Términos por (equipo, jornada):
- **points_prize** = `round(round_points * money_per_point)`. Se paga SIEMPRE (incluso en pseudo-jornadas
  adelantadas), inmediatamente por los puntos de la ronda.
- **ranking_prize**: solo si `award_round_prizes` y el equipo tiene puntos > 0. Posiciones se asignan solo entre
  miembros activos (puntos > 0). `total_pct = active_members*(active_members+1)/2`. Modo `flop`:
  `ratio = pos/total_pct`; otro modo (top): `ratio = (active_members - pos + 1)/total_pct`.
  `ranking_prize = round(money_per_ranking * ratio)`.
- **mvp_prize** = `mvp_bonus` para el único equipo cuya alineación contenía al jugador MVP del dream team
  (`mvp_team_id`), solo si `award_round_prizes`; si no, 0.
- **dream_team_prize** = `round(dt_count * dream_team_bonus)`, donde `dt_count` = nº de jugadores del once ideal
  presentes en la alineación del equipo esa ronda; solo si `award_round_prizes`.
- **award_round_prizes** = `is_closed AND round_fully_played AND NOT is_advanced_pseudo_round`. `round_fully_played`
  exige que TODOS los partidos de la ronda estén en estado `"F"` (una ronda "closed" con partidos aplazados NO
  otorga ranking/MVP/dream-team, solo points).
- **Pseudo-jornadas adelantadas** (número no entero de Futmondo, p. ej. `0.5`): se almacenan bajo un `matchday`
  sintético NEGATIVO (`0.5 -> -5`) para no colisionar con jornadas reales 1..38 (la columna es entera y Postgres
  redondearía). Solo aportan points_prize. El endpoint `prizes/{team_id}` las etiqueta como "Adelantada" y las
  ordena al final.
- **Limpieza defensiva**: al final borra filas de `team_prizes` de matchdays ya no válidos (`DELETE ... WHERE
  matchday NOT IN (valid_matchdays)`), para purgar premios de ranking calculados antes de completarse la ronda.

Entradas: API de Futmondo (standings, rounds, round_ranking, dream_team, round_lineup, round_matches) +
config en `user_championships`. Salida: tabla `team_prizes`. Consumo aguas abajo:
- `player_finances.get_player_finances`: `total_money = initial_budget + points_money + transaction_profit +
  (dream_team + mvp) + ranking_money + net_adjustment`. Lee premios vía `dm.get_prizes_by_team` (dict con
  `ranking|mvp|points|dream_team|total`). **Nota**: no suma explícitamente `points_money` de team_prizes como
  término separado del budget salvo por `points_money` que ya viene de premios — verificar en diseño el doble
  origen de "puntos" (puntos como métrica vs points_prize monetario).
- `balances.get_balances`: suma `ranking_prize + mvp_prize + points_prize + dream_team_prize` de `team_prizes`
  al balance; expone `prizes` por equipo. `balances/prizes/{team_id}` da el desglose por jornada.

### Frameworks & Libraries

- FastAPI — backend (routers `APIRouter`, `HTTPException`, `Query`, `Depends`) — capa HTTP.
- Pydantic — modelos de request/response en models.py.
- Python `statistics` — analítica (media, pstdev) en analytics_service.
- Angular 22 + Angular Material 22 — UI (signals, standalone components, `MatTable`, `MatDialog`).
- PostgreSQL (Neon) accedido con SQL crudo vía `db_connection.get_db()` + `adapt_params` (placeholders `?`).

### Test Coverage

- **Test Directories**: backend/tests/
- **Test Frameworks**: pytest (+ FastAPI `TestClient`); frontend Vitest/`ng test` (no ejercitado en este scan).
- **Coverage Config**: presente pero NO bloqueante. `backend/pytest.ini`: `testpaths=tests`, `pythonpath=.`,
  cobertura informativa opt-in (`--cov=app`), sin `fail_under`.
- **Cobertura del área de premios**:
  - `test_finance_characterization.py` — CARACTERIZA `player_finances` (fórmula agregada, orden desc, lectura
    de `team_prizes`, budget por defecto 200M, 500 en error). Doble de `DataManagerV2` + `get_db` falso.
  - `test_analytics_service.py` — CARACTERIZA `AnalyticsService` (trends, form, value-trend, clause-network,
    streaks, projections) con `StubDM`.
  - **GAP crítico**: NO existe ningún test que caracterice `data_sync_service.sync_prizes()` — es decir, la
    FÓRMULA real de premios (ratios de ranking flop/top, gating por ronda completa, MVP/dream-team,
    pseudo-jornada negativa, limpieza defensiva) está SIN red de caracterización. `balances`/`matchdays`
    tampoco tienen tests directos.

### Code Quality Indicators

- **Linting**: ruff (backend/ruff.toml; advisory en CI hoy) + ESLint flat (frontend, advisory).
- **CI/CD**: `.github/workflows/ci.yml` (gate MR: pytest + ng test + gitleaks bloqueantes) y `fly-deploy.yml`
  (push→main; `verify` corre `pytest -q` sin `--cov` ni gitleaks — no idéntico al gate MR).
- **Documentation**: docstrings en inglés en endpoints; comentarios extensos y de calidad en `sync_prizes`
  explicando el porqué de la pseudo-jornada negativa y el gating. README raíz completo.

### Technical Debt Signals

- **God-file** `data_sync_service.py` (~1925 líneas / ~84 KB) alberga toda la fórmula de premios; sin capa
  repositorio, con SQL crudo embebido y llamadas a la API de Futmondo intercaladas con `time.sleep()`.
- **SQL crudo disperso en routers**: `balances.py`, `analytics.py` (classification-full, watchlist) construyen
  SQL inline sin capa de persistencia — mismo patrón que `project.md` marca como deuda a no ampliar.
- **Resolución de identidad frágil** en `player_finances`: múltiples lookups por team_id/user_id/nombre
  (normalización a lower) con fallback por coincidencia de nombre — riesgo de doble conteo/omisión de ajustes.
- **Ausencia de caracterización** de `sync_prizes` (ver Test Coverage) — el núcleo del intent no está congelado.
- **Cobertura de errores amplia**: bloques `except Exception` que mapean a 500 sin distinguir causas.
- **Doble semántica de "puntos"** entre métrica de puntos y `points_prize` monetario a aclarar en diseño.

## Handoff Summary

- **Intent-relevant finding**: La fórmula de premios de jornada NO vive en los ficheros del snapshot de
  deep-scan (endpoints/finanzas), sino ENTERAMENTE en `backend/app/services/data_sync_service.py::sync_prizes()`
  (~1577-1885). Produce la tabla `team_prizes` (única fuente de verdad); los endpoints
  (`player_finances`, `balances`, `balances/prizes/{team_id}`) solo LEEN y SUMAN. Términos: points_prize
  (`round_points*money_per_point`, siempre), ranking_prize (ratio flop/top sobre miembros activos, solo ronda
  completa), mvp_prize (`mvp_bonus` al equipo con el MVP), dream_team_prize (`dt_count*dream_team_bonus`), con
  gating `award_round_prizes = is_closed AND round_fully_played AND NOT pseudo-ronda` y pseudo-jornadas
  adelantadas almacenadas como matchday negativo.
- **Risks / follow-up** (a preservar para el architect):
  1. **Fichero clave fuera del snapshot de cobertura profunda**: `sync_prizes` (en un god-file ~84 KB) es donde
     hay que intervenir. El architect debe decidir si amplía el snapshot para caracterizarlo/refactorizarlo tras
     una capa de persistencia estrecha, respetando `project.md` (no ampliar SQL-en-router/god-files).
  2. **GAP de tests**: no hay caracterización de `sync_prizes` ni de `balances`/`matchdays`. `team.md` exige
     characterization-first antes de refactor: falta congelar ratios de ranking, gating de ronda completa, MVP,
     dream-team, pseudo-jornada negativa y la limpieza defensiva `DELETE ... NOT IN`. Los tests existentes solo
     cubren el consumo (finanzas/analytics), no la producción del premio.
  3. **Dependencia dura de la API de Futmondo** en `sync_prizes` (standings, rounds, ranking, dream_team,
     lineups, matches) con `time.sleep()` — diseñar dobles/fakes (patrón `conftest.py`) para test sin coste 0€.
  4. **Doble origen de "puntos"** (métrica vs points_prize) y **resolución de identidad por nombre** son focos
     de posible incoherencia a validar en diseño.
  5. Coste 0€ y stack fijo (FastAPI/Angular/Neon/Fly.io) se mantienen; sin reescrituras grandes.
