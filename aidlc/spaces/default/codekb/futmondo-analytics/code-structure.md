# Estructura del Código — Futmondo Analytics

## Organización de paquetes/módulos

```
futmondo-analytics/
├── backend/                # FastAPI (Python 3.12)
│   ├── app/
│   │   ├── core/           # config.py, constants.py
│   │   ├── services/       # lógica de negocio + integraciones (god files aquí)
│   │   ├── api/v1/endpoints/  # 24 routers HTTP
│   │   ├── auth/           # JWT + token/session store
│   │   ├── stores/         # repositorios durables task/session
│   │   ├── security/       # protección de credenciales
│   │   ├── models/         # modelos de datos
│   │   └── main.py         # app, middleware, montaje de routers/estáticos
│   ├── scripts/            # utilidades one-shot (sync, export, migraciones, init_db)
│   ├── tests/              # ≈28 ficheros pytest (characterization-first)
│   └── conftest.py         # fixtures fake in-memory
├── angular-app/            # SPA Angular 22 (PWA)
├── proxy/                  # nginx reverse proxy (local)
├── cron/                   # app Fly.io de crons
└── docs/                   # documentación
```

> Inventario de responsabilidades por componente en `component-inventory.md`;
> versiones en `technology-stack.md`.

## Clasificación de ficheros

- **Configuración de negocio**: `backend/app/core/config.py` (resolución de
  BD y secretos; contiene los defaults hardcodeados `CHAMPIONSHIP_ID`/
  `LEAGUE_ID`), `backend/app/core/constants.py` (catálogo estático
  `LALIGA_TEAMS`, fallback legítimo; `LALIGA_TEAM_NAMES` usado por assistant).
- **Acceso a datos**: `backend/app/services/db_connection.py` (manager
  multi-backend PostgreSQL/SQLite/Turso; único engine vivo = Neon).
- **Integraciones**: `futmondo_client.py`, `sofascore_client.py`,
  `assistant_service.py`; errores en `integration_errors.py`.
- **God-files (deuda, foco FR13, NO ampliar)**: `data_manager_v2.py` (3692
  líneas), `data_sync_service.py` (1955 líneas), `assistant_service.py` (1158
  líneas), `analytics_service.py` (828 líneas).
- **Precedente de extracción ya hecho**: paquete `backend/app/services/prizes/`
  (cálculo de premios sacado a módulo estrecho testeable +
  `team_prizes_writer.replace_team_prizes`, writer transaccional atómico) —
  **patrón de referencia a replicar** en la descomposición.
- **Build/deploy**: `Dockerfile`, `fly.toml`, `requirements.txt`,
  `nixpacks.toml` (residuo Railway), `entrypoint.sh`, `docker-compose.yml`.
- **CI/CD**: `.github/workflows/ci.yml`, `fly-deploy.yml`, `daily-sync.yml`,
  `sofascore-sync.yml`.
- **Tests**: `backend/tests/` (pytest) y specs Angular en `angular-app/src/app/`.

## God files — anatomía, seams de extracción y superficie a preservar (FR13)

Los cuatro god files comparten el anti-patrón **SQL-en-servicio** (SQL crudo
embebido en la lógica de negocio). El eje de descomposición es separar el
acceso a datos (repositorios por agregado) de la lógica, preservando cada
fachada pública como capa delgada que delega. Riesgos de cobertura y reglas
afirmadas en `code-quality-assessment.md`.

### `data_manager_v2.py` (3692 líneas · 62 `def` · 94 `cursor.execute` · ~60 métodos públicos)

- **Rol**: acceso a datos central. **Núcleo del acoplamiento** — consumido por
  8 routers + `data_initializer_v2` + `analytics_service` (`self.dm`) +
  `data_sync_service`. Es el de **mayor riesgo** (cobertura directa ~cero).
- **Dominios mezclados** (candidatos a repositorios por agregado tras una
  fachada `DataManagerV2` delgada):
  1. **Schema/DDL & migraciones**: `_init_database` (~330 líneas, DDL de todas
     las tablas), `_ensure_schema_updates`, `reset_database`.
  2. **Jugadores**: `save_player(s)`, `save_players_batch`,
     `delete_orphan_players`, `get_player_*`, `save_player_championship_stats`,
     `get_clausulable_player_stats`, `get_player_streak_data`,
     `get_free_agent_candidates`.
  3. **Equipos/usuarios**: `save_team`, `_ensure_user`, `get_team_by_id`,
     `get_user_by_id`, `get_user_id_by_name`, `_get_or_create_user_id`.
  4. **Transacciones/pressroom/mercado**: `save_pressroom_transactions`,
     `save_player_transactions`, `save_market_players`, `get_*transactions*`,
     `get_transactions_raw`.
  5. **Cláusulas**: `parse_clause_text`, `save_clauses`,
     `get_user_clauses_stats`, `get_clauses_raw`.
  6. **Castigos/bonos & dream-team/MVP**: `save_punishments_bonuses`,
     `get_user_punishments_bonuses`, `save_dream_team_mvp`,
     `get_dream_team_bonus_stats`.
  7. **Standings/rankings/odds/evolution/prizes-read**: `save_team_standing`,
     `save_round_ranking`, `get_team_standings_history`, `save/get_match_odds`,
     `get_evolution_data_from_db`, `get_prizes_by_team`, `get_latest_matchday`.
  8. **Rosters & performance**: `save_team_roster`,
     `save_player_performance(_batch)`, `get_player_performance_history`.
  9. **News/articles & sync-metadata**: `save_matchday_article`,
     `get_matchday_article`, `save_pressroom_news`,
     `get_matchday_data_for_news`, `get_last_sync_metadata`,
     `update_sync_metadata`, `should_update_cache`.
- **Seam más limpio para empezar**: envolver los 94 `cursor.execute` en un
  `SqlGateway`/query-helpers, o extraer primero los grupos read-only (7/8) que
  `analytics_service` ya consume con superficie estrecha.
- **Superficie pública a preservar**: `DataManagerV2.*` (los ~60 métodos que
  consumen los 8 routers, sync, analytics y el initializer). La fachada debe
  mantenerse o los routers rompen.
- **Cobertura actual**: directa ~cero (solo indirecta vía
  finance/prizes/db_admin_guard/futmondo characterization). **Characterization-
  first obligatorio** antes de mover código.

### `data_sync_service.py` (1955 líneas · 28 `except Exception`)

- **Rol**: orquestación del sync asíncrono (11 pasos). Consumido por
  `endpoints/sync.py` y `data_initializer.py`.
- **Dominios mezclados**: un `sync_*` por dominio ya es la unidad natural —
  candidatos a una clase/módulo por dominio (transactions, clauses,
  punishments, dream_teams, performance, rosters, rankings, players, odds,
  prizes) coordinados por un orquestador delgado `sync_all`. Funciones enormes:
  `sync_prizes` (303 líneas), `sync_player_performance` (223),
  `sync_dream_teams_mvps` (161). Helpers privados (`_store_bids`,
  `_enrich_market_values`, `_find_price_at_date`, `_save_favorites`,
  `_find_championship`, `_log_integration_failure`) siguen a su dominio.
- **Seam de referencia ya materializado**: `sync_prizes` ya delega en el
  paquete `prizes/` — replicar ese patrón (capa estrecha + writer
  transaccional atómico) para el resto de dominios.
- **Superficie pública a preservar**: `sync_*()` (10 syncs) + `sync_all()`.
- **Cobertura actual**: **parcial de efecto** — `test_sync_integration_failure_effect.py`,
  `test_sync_degraded_steps.py`, `test_sync_step_status.py` congelan la
  clasificación de fallo (DEGRADED vs fatal); `test_prizes_characterization.py`
  / `test_team_prizes_atomic_replacement.py` congelan `sync_prizes` y el
  reemplazo transaccional. El resto de `sync_*` sin caracterización directa.

### `assistant_service.py` (1158 líneas · 42 `cursor.execute`)

- **Rol**: asistente conversacional (Gemini/Groq) con SQL inline en la
  construcción de contexto. Consumido por `endpoints/assistant.py` y
  `endpoints/market.py`.
- **Seams claros**:
  - (a) `AssistantUsageTracker` (rate-limit/usage, tabla propia) — ya es una
    clase separable.
  - (b) Capa "factual" (`_try_factual_answer` + `_factual_*` + `FACTUAL_PATTERNS`)
    — resoluble desde BD sin LLM; módulo aislable.
  - (c) Construcción de contexto (`_build_context` + `_ctx_*` con SQL inline) →
    `ContextBuilder` que consuma un repositorio en vez de `cursor.execute`
    directo.
  - (d) Guardrails (`_check_guardrails` + patrones) → módulo puro fácilmente
    testeable. `ask()` queda como orquestador delgado.
- **Superficie pública a preservar**: `get_assistant_service()` y
  `async ask(...)`; el resto (`_factual_*`, `_ctx_*`, `_build_context`,
  `_check_guardrails`) es privado.
- **Cobertura actual**: **directa cero** — guardrails/factual/context/tracker
  sin test. **Characterization-first obligatorio** antes de cualquier seam.

### `analytics_service.py` (828 líneas · 2 `cursor.execute`)

- **Rol**: cálculos analíticos. El **más sano** de los cuatro: ya delega en
  `self.dm` (inyección de `DataManagerV2`) y solo tiene 2 `cursor.execute`.
  Consumido solo por `endpoints/analytics.py`.
- **Seams sugeridos**: separar helpers de resolución (`_safe_*`, `_resolve_*`,
  `_build_team_lookup`) de los cálculos `get_*`; o agrupar por familia
  (trends/form/value vs market/watchlist/clause-network vs projections).
- **Superficie pública a preservar**: `AnalyticsService.get_*` (10 métodos).
- **Cobertura actual**: **BIEN cubierto**. `test_analytics_service.py`
  monkeypatchea `AnalyticsService.__init__` con un `DataManagerV2` fake
  (lambdas por método) → el **seam de inyección ya existe de facto** (superficie
  estrecha y mockeable). 6 de 10 `get_*` con test directo. **Candidato de menor
  riesgo para la primera oleada.**

## Patrones de código observados

- **Router-por-recurso**: 24 routers montados en `main.py` bajo `/api/v1/*`.
- **SQL-en-servicio** (anti-patrón núcleo del intent): SQL crudo inline en los
  god files (94 + 42 + … `cursor.execute`).
- **Acoplamiento estrella a `DataManagerV2`**: sync y analytics dependen del
  god file vía `self.dm`; extraer DM sin romper esos consumidores es la
  restricción dura.
- **Estado/config module-level**: `data_sync_service` toma
  `CHAMPIONSHIP_ID`/`LEAGUE_ID`/`FUTMONDO_EMAIL/PASSWORD` de `app.core.config`;
  assistant toma `GEMINI_API_KEY`/`GROQ_API_KEY` y límites module-level;
  `_resolve_real_team_name` importa `LALIGA_TEAM_NAMES` dentro del método.
- **Caché mutable per-instance**: `analytics_service._team_cache`/`_player_cache`;
  `data_manager_v2.cache_duration`.
- **Excepciones tipadas propagadas** para fallos de integración.
- **Characterization-first** en tests (fixtures fake in-memory en `conftest.py`,
  sin red/BD real/credenciales).

## Idioma del código

Identificadores, docstrings y comentarios en inglés; texto de cara al usuario
(`HTTPException.detail`, UI) y mensajes de commit en castellano.
