# Dependencies

## Dependencias externas

Versiones pinneadas en `technology-stack.md`. Resumen por categoría:

- **Servicios externos**: API Futmondo (auth + datos de sync), API Sofascore
  (ratings), Neon PostgreSQL (almacén), Fly.io (hosting), GitHub Actions (CI/CD),
  LLM (`google-genai`, `groq`) para el asistente.
- **Runtime backend**: `fastapi`, `uvicorn`, `pydantic`, `PyJWT`,
  `psycopg2-binary`, `requests`, `curl_cffi`, `python-dotenv`, `python-multipart`.
- **Runtime frontend**: `@angular/*`, `@angular/material`, `chart.js`,
  `ng2-charts`, `marked`, `rxjs`.
- **Gobierno de deps**: `requirements.txt` con rangos abiertos (deuda de pin);
  `pip-audit` sobre el entorno resuelto + allowlist versionada
  `backend/.pip-audit-allowlist`; `npm audit` en el frontend. Ver
  `code-quality-assessment.md`.

## Dependencias internas cross-módulo (backend, foco del scan)

Componentes en `component-inventory.md`; grafo de relaciones en `architecture.md`.
Aristas clave (build/import) del área analizada:

- `api/v1/endpoints/sync.py` → `DataSyncService` (surface público), `task_service`,
  `sync_step_status` (`record_degraded_step`), `data_manager_v2` (SQL inline del
  router), `db_connection`, `integration_errors`.
- `DataSyncService` (`data_sync_service.py`) →
  - `DataManagerV2` (`data_manager_v2.py`) — persistencia (SQL), incluyendo
    `self.dm.db` crudo en varios dominios inline.
  - `futmondo_client` — ingesta API Futmondo (excepciones tipadas).
  - `sofascore_client` — ingesta API Sofascore.
  - `prizes/` — `PrizeConfig`, `RoundTeamEntry`, `calculate_round_prizes`
    (`calculator.py`), `replace_team_prizes` (`team_prizes_writer.py`).
  - `sync.match_odds` + `sync.clauses` (lazy) — delegación fina de
    `sync_match_odds` / `sync_clauses` a sus orchestrators.
  - `integration_errors` — excepciones tipadas.
  - `core.config`.
- `sync/<pilot>/orchestrator.py` (match_odds, clauses) → `domain/ports.py`
  (abstracción `Protocol`) + `infrastructure/<domain>_adapter.py` (implementación
  por defecto `DataManagerV2(skip_init=True)`) + `FutmondoClient` (ingesta
  inyectada); el adapter → `data_manager_v2`.
- `prizes/calculator.py` → sin dependencias de I/O (puro);
  `prizes/team_prizes_writer.py` → sólo un `_DbLike` Protocol (DB inyectada).
- `data_initializer.py` → `DataSyncService.sync_all()`.
- **Routers → servicios/datos**: la mayoría de routers `api/v1/endpoints/*`
  (incluido `sync.py`) acceden a `DataManagerV2` con SQL crudo inline
  (SQL-en-router, deuda a NO ampliar).
- **Contextos DDD → datos**: `sync/`, `analytics/` y `assistant/` dependen de
  `DataManagerV2` **solo** en su `infrastructure/*_adapter.py` (dependency
  inversion vía `Protocol` en `domain/ports.py`); los shims `analytics_service.py`
  y `assistant_service.py` re-exportan para no romper imports históricos.
- **Acoplamientos internos del god-file a resolver**: `_find_championship()`
  compartido por `sync_dream_teams_mvps` + `sync_rosters` (decidir si queda en la
  fachada o se promueve a un módulo compartido en `sync/`); `_save_favorites`
  consumido sólo por `sync_players_full` (toca `self.dm.db` crudo).

## Dependencia crítica compartida

`data_manager_v2.py` (`DataManagerV2`, ~166 KB) es la dependencia de datos común
de casi todos los `sync_*` y routers. El refactor debe apoyarse en él vía
`Protocol`/adapter (como `sync/match_odds/infrastructure/match_odds_adapter.py`,
`sync/clauses/infrastructure/clauses_adapter.py` y
`analytics/infrastructure/data_manager_adapter.py`) sin tocarlo ni engordarlo
(regla afirmada).
