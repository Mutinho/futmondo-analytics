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

## Dependencias internas cross-módulo (backend)

Componentes en `component-inventory.md`; grafo de relaciones en `architecture.md`.
Aristas clave (build/import):

- `api/v1/endpoints/sync.py` → `DataSyncService`.
- `DataSyncService` (`data_sync_service.py`) →
  - `DataManagerV2` (`data_manager_v2.py`) — persistencia (SQL).
  - `futmondo_client` — ingesta API Futmondo.
  - `sofascore_client` — ingesta API Sofascore.
  - `prizes/` — `PrizeConfig`, `RoundTeamEntry`, `calculate_round_prizes`
    (`calculator.py`), `replace_team_prizes` (`team_prizes_writer.py`).
  - `integration_errors` — excepciones tipadas.
  - `core.config`.
- `data_initializer.py` → `DataSyncService.sync_all()`.
- **Routers → servicios/datos**: la mayoría de routers `api/v1/endpoints/*`
  acceden a `DataManagerV2` con SQL crudo inline (SQL-en-router, deuda a NO ampliar).
- **Contextos DDD → datos**: `analytics/` y `assistant/` dependen de
  `DataManagerV2` **solo** en su `infrastructure/*_adapter.py` (dependency
  inversion vía Protocol en `domain/ports.py`); los shims `analytics_service.py`
  y `assistant_service.py` re-exportan para no romper imports históricos.
- `prizes/team_prizes_writer.py` → `db.get_connection()` (transacción atómica).

## Dependencia crítica compartida

`data_manager_v2.py` (`DataManagerV2`, ~166 KB) es la dependencia de datos común
de casi todos los `sync_*` y routers. El refactor debe apoyarse en él vía
Protocol/adapter (como `analytics/infrastructure/data_manager_adapter.py`) sin
tocarlo ni engordarlo (regla afirmada).
