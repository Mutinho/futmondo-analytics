# Code Structure

## Organización de paquetes/módulos

Mono-repo con dos apps desplegables más soporte de infra:

- `backend/app/` — servicio web FastAPI (Python 3.12). Capas:
  - `api/v1/endpoints/` — 23 routers REST (ver `api-documentation.md`); 8 consumen
    `DataManagerV2` directamente y 17 de 23 tienen SQL inline (deuda SQL-en-router).
  - `services/` — lógica de negocio + integraciones + acceso a datos (foco de esta
    pasada).
  - `auth/` — JWT.
  - `stores/` — capa de persistencia estrecha de referencia (durabilidad).
  - `core/` — config/constants (`CACHE_DURATION_HOURS`, `DATABASE_PATH`).
  - `models/`, `security/`.
  - `main.py` — arranque FastAPI.
- `angular-app/` — frontend Angular 22 (PWA, standalone components, signals,
  Material 22): `src/app/{core,features,shared}` (skimmed).
- `proxy/` — nginx reverse proxy local.
- `cron/` — máquinas Fly one-shot para sincronizaciones programadas.
- `docs/`, `scripts/`, `docker-compose.yml`, `.github/workflows/`.

## Clasificación de ficheros (backend `services/` + `stores/`, foco del scan)

### God-file objetivo — `services/data_manager_v2.py` (deuda principal)

- `DataManagerV2` — clase única, 3692 líneas / ~162 KB, 57 métodos
  (19 `save_*`, 26 `get_*`, 6 privados `_*`, resto varios). Constructor
  `DataManagerV2(db_path=None, skip_init=True)`. SQL embebido masivo: 148
  sentencias (34 `INSERT` / 75 `SELECT` / 14 `UPDATE` / 15 `CREATE TABLE` / 24
  `ON CONFLICT`). Mezcla ~14 responsabilidades (ver `api-documentation.md` para la
  superficie exacta con números de línea y `component-inventory.md` para los
  clusters). Es el **último god-file original sin descomponer**; su deuda de lint
  está registrada en `ruff.toml` `per-file-ignores`.

### Capa de persistencia estrecha de referencia — `services/db_connection.py` + `stores/`

- `services/db_connection.py` — `DBConnection` (pool PostgreSQL/Neon,
  `get_connection`/`get_cursor`/`adapt_params` que convierte `?`→`%s`), singleton
  vía `get_db()`. Clasificación recuperable/fatal ya endurecida. Es el punto único
  de acceso físico a Neon que `DataManagerV2` y los stores comparten.
- `stores/__init__.py`, `stores/session_repository.py`, `stores/task_repository.py`
  — `SessionRepository`, `TaskRepository`, esquemas `ensure_*`. **Modelo de
  referencia** de "SQL fuera de routers y god-files, todo parametrizado": la forma
  a la que debe tender el SQL extraído del god-file.

### Contextos DDD ya entregados (patrón objetivo probado)

- `services/analytics/` (Wave 1): `facade.py` (`AnalyticsService`) →
  `application/calculations.py` → `domain/ports.py` (`AnalyticsDataPort`, Protocol
  consumer-owned, sin SQL) + `infrastructure/data_manager_adapter.py` (único SQL,
  envuelve `DataManagerV2` verbatim). Shim `analytics_service.py`.
- `services/assistant/` (Wave 2): `facade.py` + `application/{context,factual}.py`
  + `domain/{ports,guardrails}.py` + `infrastructure/{read_adapter,llm_adapter,usage_adapter}.py`.
- `services/sync/` (Wave 3): 10 contextos (`match_odds`, `clauses`, `transactions`,
  `rosters`, `players_full`, `player_performance`, `dream_teams_mvps`,
  `round_rankings`, `punishments_bonuses`, `prizes`), cada uno con
  `orchestrator.py` + `domain/ports.py` + `infrastructure/*_adapter.py`. Facade
  `data_sync_service.py` (`DataSyncService`). Prosa de detalle del dominio sync
  preservada del store previo (no re-verificada esta pasada).
- `services/prizes/`: `calculator.py` (cálculo puro, DTOs `dataclasses`) +
  `team_prizes_writer.py` (`replace_team_prizes`, **patrón de reemplazo atómico de
  referencia**: DELETE stale + repopulado en UNA transacción, todo-o-nada;
  documenta el bug histórico que corrigió).

### Otros módulos de servicios (clasificados)

`futmondo_client.py`, `sofascore_client.py` (clientes de integración),
`data_sync_service.py`, `data_initializer_v2.py`, `futmondo_service.py`,
`sync_step_status.py` (`record_degraded_step` + `StepStatus`),
`integration_errors.py` (`IntegrationBanError`/`IntegrationTimeoutError`/
`IntegrationUnparseableError`/`IntegrationRequestError`), `photo_service.py`,
`task_*`, `session_*`.

## Patrones de código

- **Patrón objetivo DDD (probado y a replicar)**: facade delgado que preserva la
  superficie → `orchestrator.py` (application, sin SQL) → domain port (`Protocol`
  consumer-owned, sin SQL) → `infrastructure/*_adapter.py` (único SQL, envuelve
  `DataManagerV2` verbatim, `skip_init=True`, kwargs originales). Demostrado
  end-to-end en `analytics/`, `assistant/`, los 10 `sync/*` y (cálculo/escritura)
  en `prizes/`.
- **Set-replacement + escritura atómica**: upsert del conjunto completo +
  `DELETE ... NOT IN (...)` de filas stale en una sola transacción
  (`team_prizes_writer.replace_team_prizes`), all-or-nothing. Patrón al que debe
  migrar `delete_orphan_players`.
- **Divergencia de ramas SQL por engine**: `if self.db.db_type in
  ["postgresql","postgres"]: ... else: (SQLite)` en múltiples métodos del god-file;
  productiva es la rama PostgreSQL, la SQLite sostiene el `_FakeInMemoryDB` de
  tests. A preservar en characterization.
- **Anti-patrones heredados (NO ampliar, regla afirmada)**:
  - **SQL-en-router**: 17 de 23 routers con `cursor.execute` inline; entre los
    consumidores del objetivo `clausulable_players.py` (L75–79, L170–179),
    `player_finances.py` (L38), `user_stats.py`, `sync.py` mezclan SQL inline con
    el facade.
  - **Broad/bare excepts**: 18 `except Exception` + 5 `except:` desnudos en el
    god-file (L57, L68, L672, L1388, L1628, …). Deuda afirmada (E722 en
    per-file-ignores).
  - **`return None` como posible señal de fallo silenciosa**: 16 `return None` en
    el god-file — distinguir `Optional` "no encontrado" de fallo tragado.
- **Convenciones**: identificadores/docstrings/comentarios en inglés; texto de
  usuario y mensajes de commit en castellano; snake_case Python, camelCase TS.
  Docstrings ricos en los contextos DDD; razonables (módulo/clase/método) en el
  god-file.
