# Reverse Engineering — Developer Code Scan (link 1)

Intent: `260927-god-files-refactor` — FR13, descomposición de los god files del
backend. Escaneo FOCUSED, profundidad Minimal. Objetivo: identificar seams de
extracción por dominio/responsabilidad preservando comportamiento
(characterization-first).

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply** (dentro del path set del snapshot):
  - `backend/app/services/data_manager_v2.py`
  - `backend/app/services/data_sync_service.py`
  - `backend/app/services/assistant_service.py`
  - `backend/app/services/analytics_service.py`
- **Skimmed only** (solo para entender fronteras; NO son objetivo de extracción):
  - `backend/app/services/db_connection.py` (pool PostgreSQL/Neon, `get_db()`, `get_connection`/`get_cursor`/`adapt_params`; único engine tras FR14.1)
  - Routers llamadores: `backend/app/api/v1/endpoints/{sync,analytics,assistant,market,statistics,matchdays,player_finances,clausulable_players,user_stats,initialize,reset_db}.py`
  - Servicios llamadores/relacionados: `data_initializer.py`, `data_initializer_v2.py`, `prizes/` (paquete ya extraído, incl. `team_prizes_writer.replace_team_prizes`), `integration_errors.py`, `sync_step_status.py`, `futmondo_client.py`
  - Tests: `backend/tests/test_analytics_service.py` (leído), inventario del resto de `backend/tests/`

### Packages Found

- `backend/app/services` — service layer — Python 3.12 — lógica de negocio + acceso a datos mezclados (god files objetivo aquí).
- `backend/app/api/v1/endpoints` — routers FastAPI — Python 3.12 — llamadores externos (superficie a preservar).
- `backend/app/services/prizes` — paquete — Python 3.12 — **precedente de extracción ya hecho**: cálculo de premios sacado a módulo estrecho testeable con writer transaccional atómico.

### Build System

- **Type**: pip / `pytest`; sin cambio de build en este intent (config-agnóstico).
- **Config Files**: `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`.
- **Build Dependencies**: servicios → `db_connection` (DBConnection/get_db), `app.core.config`, `app.core.constants`.

### APIs Discovered

Superficie pública consumida externamente (contrato a NO romper por seam):

- `DataManagerV2` (`data_manager_v2.py`) — consumido por 8 routers + `data_initializer_v2`, `analytics_service`, `data_sync_service`. ~60 métodos públicos.
- `DataSyncService` (`data_sync_service.py`) — consumido por `endpoints/sync.py` y `data_initializer.py`. Entradas públicas: `sync_*()` (10 syncs) + `sync_all()`.
- `AssistantService` + `get_assistant_service()` (`assistant_service.py`) — consumido por `endpoints/assistant.py` y `endpoints/market.py`. Entrada pública: `async ask(...)`; el resto (`_factual_*`, `_ctx_*`, `_build_context`) es privado.
- `AnalyticsService` (`analytics_service.py`) — consumido solo por `endpoints/analytics.py`. Entradas públicas: `get_*` (10 métodos).

### Frameworks & Libraries

- FastAPI (routers), psycopg2 (`ThreadedConnectionPool`), `google.genai` (Gemini) + Groq (assistant), stdlib `statistics`/`collections` (analytics). Versiones: ver `requirements.txt` (rangos abiertos — deuda ya anotada en memoria del proyecto).

### Test Coverage

- **Test Directories**: `backend/tests/`
- **Test Frameworks**: pytest; fakes in-memory vía `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor` SQLite `:memory:`).
- **Coverage Config**: `--cov=app` observability-only hoy (sin piso; el piso backend lo introduce otro intent).
- **Cobertura por god file**:
  - `analytics_service.py` — **BIEN cubierto**. `test_analytics_service.py` monkeypatchea `AnalyticsService.__init__` con un `DataManagerV2` fake (lambdas por método) → seam de inyección YA existe de facto: analytics depende de `self.dm` con superficie estrecha y mockeable. 6 de 10 `get_*` con test directo.
  - `data_sync_service.py` — **cobertura parcial de efecto**: `test_sync_integration_failure_effect.py`, `test_sync_degraded_steps.py`, `test_sync_step_status.py` caracterizan clasificación de fallo (DEGRADED vs fatal) y `test_prizes_characterization.py`/`test_team_prizes_atomic_replacement.py` congelan `sync_prizes`/reemplazo transaccional. El resto de `sync_*` sin caracterización directa.
  - `data_manager_v2.py` — **cobertura directa ~cero** (solo indirecta vía finance/prizes/db_admin_guard/futmondo characterization). God file más expuesto y menos protegido.
  - `assistant_service.py` — **cobertura directa cero** detectada. Guardrails/factual-patterns/usage-tracker sin test.

### Code Quality Indicators

- **Linting**: `backend/ruff.toml` (`E,F,I`; `E722`/bare-except re-habilitado advisory). Sin `# noqa` en los 4 ficheros (0).
- **CI/CD**: `.github/workflows/{ci.yml,fly-deploy.yml}` (gate gitleaks + pytest + ng test).
- **Documentation**: docstrings de módulo/clase presentes; lógica interna escasamente documentada.

### Technical Debt Signals

- **God files / SQL-en-servicio** (patrón núcleo del intent):
  - `data_manager_v2.py`: 3692 líneas, ~60 métodos, **94 `cursor.execute` inline**, `except: pass` ~29, 5 `except:` bare, 18 `except Exception`. `_init_database` (330 líneas) mezcla DDL de todas las tablas. SQL crudo embebido en cada save/get.
  - `data_sync_service.py`: 1955 líneas, 28 `except Exception`, ~34 `except:`-tipo. Funciones enormes: `sync_prizes` (303), `sync_player_performance` (223), `sync_dream_teams_mvps` (161).
  - `assistant_service.py`: 1158 líneas, 42 `cursor.execute` inline (SQL-en-servicio dentro de los `_ctx_*`).
  - `analytics_service.py`: 828 líneas, solo 2 `cursor.execute` (delega en `self.dm`) — el más limpio.
- **Estado global / config module-level**: `data_sync_service` toma `CHAMPIONSHIP_ID`/`LEAGUE_ID`/`FUTMONDO_EMAIL/PASSWORD` de `app.core.config`; assistant toma `GEMINI_API_KEY`/`GROQ_API_KEY` y límites module-level; `_resolve_real_team_name` importa `LALIGA_TEAM_NAMES` de constants dentro del método.
- **Caché mutable per-instance**: `analytics_service._team_cache`/`_player_cache`; `data_manager_v2` `cache_duration`.
- **Acoplamiento estrella a `DataManagerV2`**: sync y analytics dependen del god file vía `self.dm`; extraer DM sin romper esos consumidores es la restricción dura.
- **Reincidencia de `except: pass` en DM** (ya listada como deuda registrada fuera de alcance en memoria del proyecto).

---

## Candidatos de extracción por seam (POR FICHERO)

- **`data_manager_v2.py`** — dominios mezclados = candidatos a repositorios por agregado, preservando la fachada `DataManagerV2` como capa delgada que delega:
  1. Schema/DDL & migraciones: `_init_database`, `_ensure_schema_updates`, `reset_database`.
  2. Jugadores: `save_player(s)`, `save_players_batch`, `delete_orphan_players`, `get_player_*`, `save_player_championship_stats`, `get_clausulable_player_stats`, `get_player_streak_data`, `get_free_agent_candidates`.
  3. Equipos/usuarios: `save_team`, `_ensure_user`, `get_team_by_id`, `get_user_by_id`, `get_user_id_by_name`, `_get_or_create_user_id`.
  4. Transacciones/pressroom/mercado: `save_pressroom_transactions`, `save_player_transactions`, `save_market_players`, `get_*transactions*`, `get_transactions_raw`.
  5. Cláusulas: `parse_clause_text`, `save_clauses`, `get_user_clauses_stats`, `get_clauses_raw`.
  6. Castigos/bonos & dream-team/MVP: `save_punishments_bonuses`, `get_user_punishments_bonuses`, `save_dream_team_mvp`, `get_dream_team_bonus_stats`.
  7. Standings/rankings/odds/evolution/prizes-read: `save_team_standing`, `save_round_ranking`, `get_team_standings_history`, `save/get_match_odds`, `get_evolution_data_from_db`, `get_prizes_by_team`, `get_latest_matchday`.
  8. Rosters & performance: `save_team_roster`, `save_player_performance(_batch)`, `get_player_performance_history`.
  9. News/articles & sync-metadata: `save_matchday_article`, `get_matchday_article`, `save_pressroom_news`, `get_matchday_data_for_news`, `get_last_sync_metadata`, `update_sync_metadata`, `should_update_cache`.
  - **Seam más limpio para empezar**: extraer un `SqlGateway`/query-helpers (envolver los 94 `cursor.execute`) o los grupos read-only (7/8) que analytics ya consume con superficie estrecha.
- **`data_sync_service.py`** — un `sync_*` por dominio ya es la unidad natural; candidatos a una clase/módulo por dominio de sync (transactions, clauses, punishments, dream_teams, performance, rosters, rankings, players, odds, prizes) coordinados por un orquestador delgado `sync_all`. Helpers privados (`_store_bids`, `_enrich_market_values`, `_find_price_at_date`, `_save_favorites`, `_find_championship`, `_log_integration_failure`) siguen a su dominio. `sync_prizes` (303) ya delega en el paquete `prizes/` — patrón de referencia a replicar.
- **`assistant_service.py`** — tres seams claros: (a) `AssistantUsageTracker` (rate-limit/usage, tabla propia) ya es una clase separable; (b) capa "factual" (`_try_factual_answer` + `_factual_*` + `FACTUAL_PATTERNS`) resoluble desde DB sin LLM; (c) construcción de contexto (`_build_context` + `_ctx_*` con SQL inline) → candidata a un `ContextBuilder` que consuma un repositorio en vez de `cursor.execute` directo; guardrails (`_check_guardrails` + patrones) a módulo puro (fácilmente testeable). `ask()` queda como orquestador delgado.
- **`analytics_service.py`** — el más sano; ya inyecta `self.dm`. Seam sugerido: separar helpers de resolución (`_safe_*`, `_resolve_*`, `_build_team_lookup`) de los cálculos `get_*`, o agrupar por familia (trends/form/value vs market/watchlist/clause-network vs projections). Riesgo bajo; buen candidato para primera oleada de bajo riesgo.

## Seams testeables (characterization-first)

- **Ya existe**: patrón de fake `DataManagerV2` por lambdas en `test_analytics_service.py` → reutilizable para caracterizar analytics y para caracterizar consumidores de DM antes de mover código.
- **Ya existe**: fakes in-memory de `conftest.py` (`_FakeInMemoryDB`) → base para caracterizar métodos DM con SQL antes de extraer un repositorio.
- **Ya existe**: caracterización de efecto de sync (DEGRADED/fatal, prizes atómico) → congela el contrato de fallo antes de trocear `data_sync_service`.
- **Falta cubrir antes de extraer**: `assistant` (guardrails/factual/context) y la mayoría de métodos de `DataManagerV2` (cobertura directa ~cero) — caracterización obligatoria previa a cualquier seam en ellos.

## Handoff Summary

- **Intent-relevant finding**: los cuatro god files comparten el anti-patrón SQL-en-servicio; `DataManagerV2` (3692 líneas, 94 `cursor.execute`, ~60 métodos públicos consumidos por 8 routers + sync + analytics) es el núcleo del acoplamiento y el de mayor riesgo por su cobertura directa ~cero. Los seams naturales ya están insinuados por dominio (grupos de métodos en DM, un `sync_*` por dominio en sync, tracker/factual/context/guardrails en assistant). El paquete `prizes/` + `replace_team_prizes` es el precedente de extracción a replicar (capa estrecha testeable + writer transaccional). `analytics_service` es el candidato de menor riesgo (ya inyecta `self.dm`, ya tiene test con fake).
- **Risks / follow-up**:
  - Preservar la superficie pública: `DataManagerV2.*` (8 routers), `DataSyncService.sync_*`/`sync_all`, `get_assistant_service()`/`ask()`, `AnalyticsService.get_*`. Cualquier extracción debe mantener fachada o los routers rompen.
  - Cobertura previa insuficiente en `data_manager_v2.py` y `assistant_service.py`: characterization-first es obligatorio antes de mover su código (mandato afirmado del proyecto).
  - Deuda de `except: pass` en DM (29) y en `photo_service` está EXPLÍCITAMENTE fuera de alcance por reglas afirmadas en memoria — NO sanearla oportunistamente al extraer; se preserva comportamiento.
  - Estado/config module-level (`CHAMPIONSHIP_ID`, keys de API, `LALIGA_TEAM_NAMES`) crea acoplamiento oculto; considerar inyección al extraer, sin cambiar el comportamiento observable.
  - No ampliar los god files ni el patrón SQL-en-router (regla afirmada); el código nuevo va tras capa/función estrecha testeable.
