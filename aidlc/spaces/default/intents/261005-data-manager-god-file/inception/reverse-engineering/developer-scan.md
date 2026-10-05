## Developer Code Scan Results

> Scan FOCALIZADO (CodeKB previo STALE) para el intent `261005-data-manager-god-file`.
> Repo single-root sin cualificador. Lenguaje: identificadores/rutas/código en inglés;
> prosa de hallazgos en castellano. Esta etapa es **solo lectura/observación**: no se
> modificó ninguna fuente de aplicación.

### Scan Coverage

- **Analyzed deeply**:
  - `backend/app/services/data_manager_v2.py` (el god-file objetivo — 3692 líneas / ~162 KB)
  - `backend/app/services/` (facades, orquestadores y paquetes DDD ya descompuestos: `analytics/`, `assistant/`, `prizes/`, `sync/` y módulos sueltos `db_connection.py`, `data_sync_service.py`, `data_initializer_v2.py`, `futmondo_service.py`, `sync_step_status.py`, `integration_errors.py`)
  - `backend/app/api/v1/endpoints/` (endpoints consumidores de `DataManagerV2` y patrón SQL-en-router)
  - `backend/app/stores/` (`__init__.py`, `session_repository.py`, `task_repository.py` — capa de persistencia estrecha de referencia)
- **Skimmed only**:
  - `backend/conftest.py` y `backend/tests/` (clasificados: fakes in-memory + suite de characterization; no se leyó cada test en profundidad)
  - `backend/requirements.txt`, `backend/ruff.toml`, `backend/pytest.ini` (leídos para contexto de stack/calidad)
  - `.github/workflows/` (CI/CD — clasificado)
  - `angular-app/` (frontend Angular), resto de `backend/` (core, models, auth, main), `proxy/`, `docs/`, infra raíz (solo clasificados, no analizados)

### Packages Found

- `app.services.data_manager_v2` — god-file / data-access monolítico — Python — persistencia y lectura históricas sobre PostgreSQL/Neon; **objetivo del refactor**. Una sola clase `DataManagerV2` con 57 métodos (19 `save_*`, 26 `get_*`, 6 privados `_*`, resto varios).
- `app.services.analytics` — paquete DDD (Wave 1) — Python — patrón de referencia probado: `facade.py` (`AnalyticsService`, superficie pública preservada) → `application/calculations.py` → `domain/ports.py` (`AnalyticsDataPort`, Protocol consumer-owned, sin SQL) + `infrastructure/data_manager_adapter.py` (único módulo con SQL, envuelve `DataManagerV2` verbatim).
- `app.services.assistant` — paquete DDD (Wave 2) — Python — misma capa: `facade.py` + `application/{context,factual}.py` + `domain/{ports,guardrails}.py` + `infrastructure/{read_adapter,llm_adapter,usage_adapter}.py`.
- `app.services.prizes` — paquete DDD — Python — `calculator.py` + `team_prizes_writer.py` (**patrón de reemplazo atómico de referencia**: DELETE de filas stale + repopulado completo en UNA transacción, todo-o-nada).
- `app.services.sync` — paquetes DDD (Wave 3) — Python — 10 contextos (`match_odds` piloto, `clauses`, `transactions`, `rosters`, `players_full`, `player_performance`, `dream_teams_mvps`, `round_rankings`, `punishments_bonuses`, `prizes`). Cada uno: `orchestrator.py` + `domain/ports.py` + `infrastructure/*_adapter.py`. El facade sigue siendo `data_sync_service.py` (`DataSyncService`); los adapters envuelven `DataManagerV2` **verbatim** sin añadirle métodos.
- `app.services.db_connection` — infraestructura compartida — Python — `DBConnection` (pool PostgreSQL/Neon, `get_connection`/`get_cursor`/`adapt_params`, `?`→`%s`), singleton vía `get_db()`. Clasificación recuperable/fatal ya endurecida (FR3.2.2/BR1.6).
- `app.stores` — capa de persistencia estrecha (durable session/task) — Python — `SessionRepository`, `TaskRepository`, esquemas `ensure_*`. **Modelo de referencia** de "SQL fuera de routers y god-files, todo parametrizado".
- `app.api.v1.endpoints` — capa HTTP (FastAPI routers) — Python — 23 routers; 8 consumen `DataManagerV2` directamente y varios tienen SQL inline (deuda SQL-en-router).

### Build System

- **Type**: backend Python (pip + `requirements.txt`, pinned exacto); frontend npm (Angular, fuera de foco). Deploy Fly.io + GitHub Actions.
- **Config Files**: `backend/requirements.txt`, `backend/ruff.toml`, `backend/pytest.ini`, `backend/conftest.py`, `.github/workflows/{ci,fly-deploy,daily-sync,sofascore-sync}.yml`.
- **Build Dependencies** (relaciones internas relevantes al foco):
  - `endpoints/*` → `services.data_manager_v2.DataManagerV2` (8 routers: `clausulable_players`, `initialize`, `matchdays`, `player_finances`, `reset_db`, `statistics`, `sync`, `user_stats`)
  - `services.analytics.infrastructure.data_manager_adapter` → `DataManagerV2` (verbatim)
  - `services.assistant.infrastructure.read_adapter` → `DataManagerV2` / `db_connection`
  - `services.sync.<ctx>.infrastructure.*_adapter` → `DataManagerV2` (verbatim, los 10 contextos)
  - `services.data_sync_service` / `data_initializer_v2` → `DataManagerV2`
  - `DataManagerV2` → `app.core.config` (`CACHE_DURATION_HOURS`, `DATABASE_PATH`) + `services.db_connection.DBConnection`

### APIs Discovered

- **REST (FastAPI) — routers que consumen `DataManagerV2`** — `backend/app/api/v1/endpoints/` — 8 routers:
  - `statistics.py` (consumo limpio vía facade: `dm.get_users_unique_players_stats`)
  - `player_finances.py`, `clausulable_players.py`, `user_stats.py` (consumo mixto: facade + `cursor.execute` inline)
  - `sync.py` (consumo vía `DataSyncService.dm` y `DataManagerV2().get_last_sync_metadata`/`update_sync_metadata`)
  - `initialize.py`, `matchdays.py`, `reset_db.py`
- **Superficie pública interna de `DataManagerV2`** (contrato a PRESERVAR exacto) — `backend/app/services/data_manager_v2.py` — 57 métodos. Constructor `DataManagerV2(db_path=None, skip_init=True)`. Agrupación observada por responsabilidad candidata (a confirmar en Plan Approval):
  1. **schema/lifecycle**: `_init_database` (L38), `reset_database` (L368), `_ensure_schema_updates` (L3009), `_ensure_user`/`_get_or_create_user_id`/`_ensure_championship_in_transaction`/`ensure_championship_exists` (L835/1803/2014/1990).
  2. **players**: `save_player` (L418), `save_players_batch` (L467), `save_players` (L733), `delete_orphan_players` (L549), `get_player_by_id` (L3611), `get_all_players_with_points` (L2369), `get_free_agent_candidates` (L3638), `get_player_streak_data` (L3665).
  3. **teams/standings**: `save_team` (L799), `save_team_standing` (L595), `save_round_ranking` (L864), `get_team_by_id` (L3572), `get_team_standings_history` (L3386), `get_latest_matchday` (L3374).
  4. **performance**: `save_player_performance` (L675), `save_player_performance_batch` (L688), `save_player_championship_stats` (L3089), `get_player_performance_history` (L3461), `get_clausulable_player_stats` (L3174).
  5. **transactions**: `save_player_transactions` (L940), `save_pressroom_transactions` (L945), `get_all_player_transactions` (L2416), `get_user_transactions` (L2523), `get_transactions_raw` (L3504).
  6. **clauses**: `parse_clause_text` (L1508), `save_clauses` (L1551), `get_user_clauses_stats` (L1705), `get_clauses_raw` (L3539).
  7. **punishments/bonuses**: `save_punishments_bonuses` (L1330), `get_user_punishments_bonuses` (L1432).
  8. **dream teams / MVP**: `save_dream_team_mvp` (L2132), `get_dream_team_bonus_stats` (L2959).
  9. **prizes**: `get_prizes_by_team` (L3420).
  10. **market/roster**: `save_market_players` (L1831), `save_team_roster` (L1892).
  11. **match odds**: `save_match_odds` (L3215), `get_match_odds` (L3320).
  12. **news/articles**: `save_matchday_article` (L1118), `get_matchday_article` (L1170), `save_pressroom_news` (L2256), `get_matchday_data_for_news` (L2794).
  13. **users/stats/evolution**: `get_user_id_by_name` (L1204), `get_users_unique_players_stats` (L2266), `get_all_users_with_points` (L2464), `get_evolution_data_from_db` (L2695).
  14. **sync-metadata/cache**: `get_last_sync_metadata` (L2040), `update_sync_metadata` (L2069), `should_update_cache` (L2262).

### Frameworks & Libraries

- Python 3.12 (ruff `target-version = "py312"`; nota: hay `.pyc` cpython-314, pero target de lint y despliegue es 3.12).
- `fastapi==0.141.1`, `uvicorn[standard]==0.54.0`, `pydantic==2.13.5`, `python-multipart==0.0.32` — capa web/API.
- `psycopg2-binary==2.9.13` — driver PostgreSQL/Neon (único engine productivo).
- `requests==2.34.2`, `curl_cffi==0.16.3` — clientes HTTP integraciones (Futmondo/Sofascore).
- `PyJWT==2.15.0` — auth JWT. `python-dotenv==1.2.3` — config.
- `google-genai==1.14.0`, `groq==0.25.0` — LLM del assistant.
- Test: `pytest==9.1.1`, `pytest-cov==7.1.0`, `httpx==0.28.1` (TestClient). Todo pinned exacto.

### Test Coverage

- **Test Directories**: `backend/tests/` (≈40+ archivos `test_*.py`, muchos `*_characterization.py`). `conftest.py` en `backend/` (raíz del runner, no en `tests/`).
- **Test Frameworks**: `pytest` + `pytest-cov`; `httpx`/`starlette.testclient.TestClient` para endpoints.
- **Coverage Config**: PRESENTE y BLOQUEANTE. `pytest.ini` → `addopts = -ra --cov-fail-under=27` (line-coverage total, sin `--cov-branch`; cobertura real medida 27.52%, piso=27 por trinquete, solo sube). Requiere `--cov=app` en la invocación (CI y job `verify` en paridad).
- **Fakes in-memory (patrón a usar en characterization)**: `backend/conftest.py` define `_FakeInMemoryDB` + `_FakeCursor` (SQLite `:memory:`, convierte `?`→`%s` espejo del `adapt_params` real), fixture `fake_db`, y `clean_jwt_env`. Sin red, sin BD real, sin credenciales reales.
- Tests que ya referencian `DataManagerV2` directamente: `test_analytics_service.py`, `test_db_admin_guard.py`, `test_finance_characterization.py` (base de partida para characterization del objetivo).

### Code Quality Indicators

- **Linting**: `ruff` (`backend/ruff.toml`), `select = ["E","F","I"]`, `ignore = ["E501","E402"]`, `line-length=100`. Estado ADVISORY (escalonado). **La deuda de lint del god-file está REGISTRADA en `per-file-ignores`**: `"app/services/data_manager_v2.py" = ["E722","F841","F401","I001"]` (E722/bare-except como deuda afirmada; saneo diferido a este refactor dedicado, NUNCA tocando/ampliando el fichero antes).
- **CI/CD**: `.github/workflows/ci.yml` (gate PR): gitleaks (bloqueante), `ruff check` (`ruff==0.16.9`, advisory), pytest con `--cov=app` (bloqueante, piso 27), `pip-audit==2.10.1` + allowlist-expiry (bloqueante), `npm audit --audit-level=high` (bloqueante). `fly-deploy.yml` replica el gate en job `verify` antes de desplegar a Fly.io (`cdg`). Crons `daily-sync.yml`, `sofascore-sync.yml`.
- **Documentation**: `README.md` extenso (es), `docs/` presente. Docstrings de módulo/clase ricos y en inglés en los paquetes DDD (analytics/assistant/sync/prizes documentan BR/FR y el "único módulo con SQL"). El god-file tiene docstring de módulo + docstrings por método razonables.

### Technical Debt Signals

- **God-file (señal principal)**: `data_manager_v2.py`, 3692 líneas / ~162–166 KB, una sola clase `DataManagerV2` con 57 métodos y responsabilidades mezcladas (14 clusters observados arriba). SQL embebido masivo: 34 `INSERT INTO`, 75 `SELECT`, 14 `UPDATE`, 15 `CREATE TABLE`, 24 `ON CONFLICT`. Es el **último god-file original sin descomponer**; `ruff` lo tiene en `per-file-ignores`.
- **Punto de corrupción de caché — reemplazo de conjunto por DELETE**: `delete_orphan_players` (L549–595) ejecuta un `DELETE FROM players ... WHERE player_id NOT IN (...) AND NOT EXISTS (...)` (rama PostgreSQL con `<> ALL(%s)`, rama SQLite con `NOT IN (placeholders)`). Hace de guardia (`if not live_player_ids: return 0`) pero el borrado y los upserts previos NO comparten una única transacción explícita a nivel de este método: patrón de reemplazo de conjunto a vigilar frente al **patrón atómico de referencia** ya probado en `prizes/team_prizes_writer.py` (DELETE stale + repopulado completo en UNA transacción, rollback todo-o-nada). El `team_prizes_writer` documenta explícitamente el bug histórico que corrigió (DELETE separado cuyo fallo se tragaba un `except: logger.warning` dejando estado MIXTO) — ese es el anti-patrón a NO replicar al descomponer.
- **Broad excepts / `except:` desnudos**: en `data_manager_v2.py` hay 18 `except Exception` y 5 `except:` desnudos (L57, L68, L672, L1388, L1628, más los `except Exception` en L360/365/378/1006/3084/3274…). Deuda afirmada (E722 en per-file-ignores). A caracterizar y preservar comportamiento observable antes de extraer; no silenciar fallos nuevos.
- **`return None` como posible señal de fallo silenciosa**: 16 `return None` en el god-file. Varios son legítimos (lookups `get_*_by_id` con tipo `Optional[...]`), pero debe distinguirse en characterization el `None` "no encontrado" (contrato legítimo) del `None` "fallo tragado" (deuda a registrar), conforme a la regla afirmada NEVER usar `return None` silencioso como señal de fallo.
- **SQL-en-router (deuda existente, NO ampliar)**: 17 de 23 routers en `endpoints/` tienen `cursor.execute` inline; entre los consumidores del objetivo, `clausulable_players.py` (L75–79, L170–179), `player_finances.py` (L38), `user_stats.py`, `sync.py` mezclan SQL inline con el facade. Patrón a preservar/observar, no a tocar en esta etapa (regla afirmada NEVER ampliar el patrón SQL-en-router).
- **Acoplamiento amplio del objetivo**: `DataManagerV2` es consumido por 8 routers + los 10 adapters de `sync/*` + `analytics`/`assistant` adapters + `data_sync_service` + `data_initializer_v2` + `futmondo_service`. El refactor debe **preservar la superficie pública exacta** (constructor no-arg / `skip_init=True`, nombres y firmas de los 57 métodos) porque los adapters la envuelven verbatim; romperla rompe las 4 oleadas DDD ya entregadas.
- **Divergencia de ramas SQL por engine**: múltiples métodos ramifican `if self.db.db_type in ["postgresql","postgres"]: ... else: (SQLite)`. Producción es PostgreSQL/Neon exclusivamente (`db_connection.py` lo documenta); la rama SQLite sobrevive para el fake de tests. Characterization debe cubrir la rama efectiva productiva sin romper la ejecución contra el `_FakeInMemoryDB`.

## Handoff Summary

- **Intent-relevant finding**: `backend/app/services/data_manager_v2.py` es una única clase `DataManagerV2` de 3692 líneas con 57 métodos públicos (19 `save_*`, 26 `get_*`, 6 privados) agrupables en ~14 responsabilidades (players, teams/standings, performance, transactions, clauses, punishments/bonuses, dream-teams/MVP, prizes, market/roster, match-odds, news, users/stats/evolution, sync-metadata/cache, schema/lifecycle), con 148 sentencias SQL embebidas (34 INSERT / 75 SELECT / 14 UPDATE / 15 CREATE TABLE / 24 ON CONFLICT). El patrón DDD destino **ya está probado y disponible como plantilla** en el mismo repo: facade delgado que preserva la superficie (`analytics/facade.py`), orquestador de aplicación, port Protocol consumer-owned sin SQL (`analytics/domain/ports.py`), `*_adapter` como único módulo con SQL que envuelve verbatim (`analytics/infrastructure/data_manager_adapter.py`, los 10 `sync/*/infrastructure/*_adapter.py`) y reemplazo de conjunto **atómico** de referencia (`prizes/team_prizes_writer.py`).
- **Risks / follow-up** (a preservar por el architect / siguiente etapa):
  1. **Preservar la superficie pública EXACTA** de `DataManagerV2` (constructor `skip_init=True`, nombres/firmas de los 57 métodos): 8 routers + 10 adapters de `sync/*` + adapters de `analytics`/`assistant` + `data_sync_service`/`data_initializer_v2` la consumen; los adapters la envuelven verbatim. Characterization-first ESTRICTO por responsabilidad antes de extraer.
  2. **Puntos de corrupción de datos a vigilar**: `delete_orphan_players` (reemplazo de conjunto por `DELETE ... NOT IN`/`<> ALL`) debe migrar al patrón atómico de `team_prizes_writer.py` (una sola transacción, rollback todo-o-nada), nunca replicar el anti-patrón histórico de DELETE separado con fallo tragado.
  3. **Error handling**: 18 `except Exception` + 5 `except:` desnudos y 16 `return None` — distinguir contrato legítimo (`Optional` "no encontrado") de deuda (fallo silencioso); registrar como deuda, no introducir fallos silenciosos nuevos.
  4. **Reglas afirmadas vigentes**: coste 0 €; characterization (congelar con tests fake in-memory del `conftest.py`, sin red/BD/credenciales) antes de endurecer; NO ampliar god-files ni SQL-en-router (esta etapa solo observa); nunca credenciales Futmondo en mensajes/`repr`/`exc_info`; no reformateo masivo (`ruff format` solo quirúrgico en ficheros nuevos); no bajar el piso `--cov-fail-under=27` (solo sube); identificadores/docstrings en inglés, prosa de usuario en castellano.
  5. **Deuda de lint registrada**: al descomponer, la entrada `per-file-ignores` de `data_manager_v2.py` en `ruff.toml` (`E722,F841,F401,I001`) podrá sanearse en los ficheros NUEVOS; el fichero original se vacía por extracción, no por reescritura in-place masiva.
