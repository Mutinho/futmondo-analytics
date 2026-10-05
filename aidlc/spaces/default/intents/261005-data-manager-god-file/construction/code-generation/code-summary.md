# Code Generation Summary — Part 2 (continuation): `data_manager_v2.py` decomposition

Intent `261005-data-manager-god-file` · scope `refactor` · Minimal · zero-Unit
(stage-level) · metodología **test-after / characterization-first**.

Esta continuación completó los **Steps 7–22** del plan aprobado: extracción de
los 11 módulos restantes (ranks 4–14) del god-file `DataManagerV2` al patrón DDD
del repo (`domain/ports.py` Protocol sin SQL → `application/<resp>.py`
orquestador sin SQL → `infrastructure/<resp>_adapter.py` con el SQL **verbatim**
incl. la rama de motor `if db_type in ["postgresql","postgres"]: … else:`), más
la verificación de fachada, auditoría de errores, lint quirúrgico y el gate
final. Los módulos 1–3 (match-odds, news-articles, performance) ya estaban
extraídos y **no se tocaron**.

## Archivos creados / modificados

### Creados — árbol DDD nuevo (`backend/app/services/data_manager/<resp>/`)
Por cada responsabilidad (clauses, punishments_bonuses, dream_teams_mvp, prizes,
market_roster, transactions, teams_standings, players, users_stats_evolution,
sync_metadata_cache, schema_lifecycle): `__init__.py`, `domain/__init__.py`,
`domain/ports.py`, `application/__init__.py`, `application/<resp>.py`,
`infrastructure/__init__.py`, `infrastructure/<resp>_adapter.py` (77 ficheros
Python nuevos en total). El SQL de cada método se movió verbatim al adapter; los
helpers compartidos de otros módulos (`ensure_championship_exists`,
`get_user_id_by_name`, `save_player`, `save_team_standing`, `get_latest_matchday`,
`get_team_by_id`) se alcanzan en vivo vía `self.dm.<helper>` (sin delegación
anidada). Los helpers `_ensure_user` / `_get_or_create_user_id` **se movieron** a
`users_stats_evolution` (expuestos como `ensure_user` / `get_or_create_user_id`);
la fachada mantiene delegadores finos con el nombre privado original para que los
adapters que llaman `self.dm._ensure_user` sigan funcionando.

### Creados — tests de caracterización (`backend/tests/`, 11 nuevos)
`test_data_manager_clauses_dm_characterization.py`,
`…_punishments_bonuses_…`, `…_dream_teams_mvp_…`, `…_prizes_read_…`,
`…_market_roster_…`, `…_transactions_…`, `…_teams_standings_…`,
`…_players_…`, `…_users_stats_evolution_…`, `…_sync_metadata_cache_…`,
`…_schema_lifecycle_…`.

### Modificados
- `backend/app/services/data_manager_v2.py` — **in-place** (sin duplicado
  `*_modified`): los 44 métodos restantes adelgazados a delegadores finos que
  mantienen nombre y firma exactos. De **3692 líneas originales (3276 al inicio
  de esta parte) a 685 líneas** — la fachada sólo delega, no crece (BR1.4).
  `__init__` permanece en la fachada (construcción de objeto) y delega sus
  llamadas de esquema (`_init_database` / `_ensure_schema_updates`).
- `backend/ruff.toml` — se añadió un `per-file-ignores` acotado
  (`app/services/data_manager/**/infrastructure/*_adapter.py = ["E722","F841"]`)
  para la deuda `bare-except` / variables sin uso movida **verbatim** desde el
  god-file (BR3.2, NFR4), espejo del ignore ya existente para `data_manager_v2.py`.

## Decisiones clave de implementación

- **Delegación vía `self.dm`**: cada adapter inyecta la fachada por constructor
  con default (`DataManagerV2(skip_init=True)`), patrón `analytics`, y expone
  `db` como *property* que lee `self.dm.db` en vivo (honra la reasignación del
  fake en test y la conexión real en producción). Los cruces entre módulos usan
  `self.dm.<helper>` → **sin delegación anidada**, preservando el comportamiento
  byte-for-byte (BR3.1) e independizando el orden de extracción.
- **`delete_orphan_players`** (BR3.3, OQ2 diferida): su `DELETE … NOT IN`
  set-replacement se movió **verbatim** y se **congela** en
  `test_delete_orphan_players_removes_unreferenced_only` (huérfano borrado;
  live + con historial conservados) y en el no-op de seguridad con lista vacía.
  **NO** se elevó al patrón atómico `replace_team_prizes`.
- **Error-handling legacy verbatim** (BR3.2): los `except Exception` / `except:`
  y los `return None` se movieron sin cambios; auditoría (Step 19): 18 broad +
  5 bare except y 18 `return None` en el árbol nuevo, **0** restantes de SQL/DELETE
  en la fachada.
- **Rama de motor** (BR1.2/FR1.4): cada adapter conserva la bifurcación
  PostgreSQL/SQLite verbatim; los tests corren sobre el fake SQLite (rama `else`),
  la rama Postgres queda cubierta por equivalencia del SQL envuelto.
- **`executemany` y `adapt_sql`**: los tests que ejercitan rutas batch (performance,
  transactions, players) decoran el cursor del fake con `executemany` (mismo patrón
  que el test de `performance` ya existente); los que llaman `self.db.adapt_sql`
  (users-stats-evolution, schema-lifecycle) adjuntan un `adapt_sql` passthrough al
  fake (en SQLite `adapt_sql` sólo reescribe DDL AUTOINCREMENT, passthrough para
  estos SELECT/CREATE IF NOT EXISTS).
- **`_init_database` / `reset_database`**: su DDL usa `SERIAL`/`BOOLEAN`/`CASCADE`
  (sólo PostgreSQL), no parseables por SQLite puro; se caracterizan las rutas
  ejecutables en SQLite (bootstrap de championship idempotente, `_ensure_schema_updates`
  creando las tablas nuevas) y el cableado de `__init__` (construye con `skip_init=True`
  sin correr el esquema completo), congelando la delegación sin fabricar un Postgres real.

## Resumen de cobertura de tests

| Módulo (rank) | test file | green-pre | green-post |
|---|---|---|---|
| clauses (4) | `…_clauses_dm_…` | 8 passed | 8 passed |
| punishments-bonuses (5) | `…_punishments_bonuses_…` | 5 passed | 5 passed |
| dream-teams-mvp (6) | `…_dream_teams_mvp_…` | 5 passed | 5 passed |
| prizes (7) | `…_prizes_read_…` | 2 passed | 2 passed |
| market-roster (8) | `…_market_roster_…` | 5 passed | 5 passed |
| transactions (9) | `…_transactions_…` | 7 passed | 7 passed |
| teams-standings (10) | `…_teams_standings_…` | 8 passed | 8 passed |
| players (11) | `…_players_…` | 10 passed | 10 passed |
| users-stats-evolution (12) | `…_users_stats_evolution_…` | 9 passed | 9 passed |
| sync-metadata-cache (13) | `…_sync_metadata_cache_…` | 4 passed | 4 passed |
| schema-lifecycle (14) | `…_schema_lifecycle_…` | 5 passed | 5 passed |

**Suite completa final**: `414 passed, 3 xfailed` (desde el baseline
`346 passed, 3 xfailed`; +68 tests de caracterización nuevos de esta parte).
**Cobertura**: `57.48%` (baseline 45.94%); piso bloqueante `--cov-fail-under=27`
**se mantiene** y el trinquete sólo subió — nunca se relajó (BR6.1/NFR2).

Fachada verificada (Step 18): `DataManagerV2` expone **exactamente los 57
métodos** con firmas idénticas, 0 faltantes, 0 añadidos; sólo delega. Los
consumidores (`data_sync_service`, `data_initializer_v2`, `futmondo_service`,
`analytics`, `assistant_service`, `sync.prizes.orchestrator`) y todos los routers
importan sin cambios (BR4.1).

## Desviaciones del plan

Ninguna desviación de alcance. Nota de ejecución: `_init_database` /
`reset_database` se caracterizan por sus rutas SQLite-ejecutables + el cableado
de `__init__` (su DDL PostgreSQL-only no es parseable por el fake SQLite); esto
congela la equivalencia observable disponible sin fabricar un motor Postgres,
coherente con el mandato de no tocar red/BD real (NFR6). El `per-file-ignores`
de ruff para los adapters es un cambio de configuración aislado que **registra**
la deuda legacy movida verbatim (BR3.2/NFR4), no la sanea reescribiendo código.
