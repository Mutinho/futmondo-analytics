# Code Summary — Enriquecimiento del sync de jugadores

## Ficheros modificados (código de aplicación)

- `backend/app/services/data_manager/schema_lifecycle/infrastructure/schema_lifecycle_adapter.py`
  — `ensure_schema_updates`: migración idempotente no destructiva de `players`
  (+`points`, `change`, `home_average`, `away_average`, `matches`, `status`),
  junto al ALTER de `team_prizes`. **Engine-aware**: PostgreSQL usa `ADD COLUMN
  IF NOT EXISTS`; SQLite introspecta `PRAGMA table_info` y hace `ADD COLUMN`
  (SQLite no soporta `IF NOT EXISTS` en columnas). (BR2.1/BR2.2/NFR6)
- `backend/app/services/data_manager/players/infrastructure/players_adapter.py`
  — `save_players_batch`: las 6 columnas en column-list, VALUES y
  `ON CONFLICT DO UPDATE SET` (ramas PostgreSQL `execute_values` y SQLite
  `executemany`). Single-insert intacto. (BR2.1)
- `backend/app/services/sync/players_full/orchestrator.py` — extrae los 6 campos
  del objeto vivo a `player_records`: `points`/`change`/`matches`/`status` con
  defaults `0`/`''`; `home_average`/`away_average` normalizados con `clean_float`
  (`"NaN"`/vacío/None → None). `stats`, orphan, favorites, metadata y
  `SyncResult` byte-identical. (BR1.1/BR1.2)
- `backend/app/services/sync_read/favorites_read.py` — SELECT lee los 6 campos +
  `value`/`average_overall`/`real_team_id` desde `players`; sirve desde la fila
  autoritativa de `players` con defaults; `team`/`team_logo` por `real_team_id`
  con `LALIGA_TEAMS` (fallback `real_team_name`; peor caso `''`/`''`); eliminado
  el bloque muerto de points por `player_performance` (ahora `players.points`);
  20 claves y orden preservados. (BR3.1/BR4.1/BR4.2/BR5.2)

## Tests creados (`backend/tests/`)

- `test_sync_players_enrichment.py` (11) — characterization del orquestador
  (campos actuales + selección de favoritos + no-leak de credenciales) + la
  nueva extracción de los 6 campos, normalización de `"NaN"`, `SyncResult`
  byte-identical.
- `test_schema_players_columns.py` (3) — ALTER idempotente; columnas existen tras
  correr `ensure_schema_updates` dos veces.
- `test_players_adapter_enrichment.py` (3) — upsert persiste y actualiza las 6
  columnas.
- `test_favorites_read_enriched.py` (6) — favorito con columnas pobladas → valores
  reales; con columnas nulas → defaults; `team` por `LALIGA_TEAMS`; peor caso
  `''`/`''`; contrato de 20 claves; orden preservado; caracterización que congela
  que el origen ANTERIOR de `points` era `SUM(player_performance)` (0 para
  agentes libres), documentando el cambio intencional.

## Fixtures existentes actualizadas al nuevo esquema

`test_favorites_read.py`, `test_favorites_read_characterization.py`,
`test_sync_read_endpoints.py`, `test_data_manager_players_characterization.py`
(siembran las columnas nuevas).

## Decisiones clave

- Migración **engine-aware** (SQLite no soporta `ADD COLUMN IF NOT EXISTS`).
- `points` pasa de `SUM(player_performance)` (0 para agentes libres) a
  `players.points` (total real que da Futmondo) — cambio intencional congelado en
  caracterización.
- God-files intactos; SQL en las capas de sync/`sync_read`/schema_lifecycle;
  contrato de 20 claves inmutable.

## Cobertura de tests

- Unit-scoped (4 ficheros nuevos): **23 passed, 0 failed**.
- Suite completa: **463 passed, 3 xfailed (legacy), 0 failed**; cobertura
  **60,82%** (piso `--cov-fail-under=27` intacto); `favorites_read.py` 100%.

## Desviaciones del plan

- El método real es `ensure_schema_updates` (el facade `_ensure_schema_updates`
  delega en él); migración engine-aware por la limitación de SQLite; se añadió
  `value` también a la rama batch SQLite por consistencia con PostgreSQL. Ningún
  test existente se rompió. Step 5/12 (code-summary/traceability) los escribe el
  orquestador.
