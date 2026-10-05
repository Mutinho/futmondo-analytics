# Dependencies

## Dependencias externas

Versiones pinneadas en `technology-stack.md`. Resumen por categoría:

- **Servicios externos**: API Futmondo (auth + datos de sync), API Sofascore
  (ratings), Neon PostgreSQL (almacén, único engine productivo), Fly.io (hosting),
  GitHub Actions (CI/CD), LLM (`google-genai`, `groq`) para el asistente.
- **Runtime backend**: `fastapi`, `uvicorn`, `pydantic`, `PyJWT`,
  `psycopg2-binary`, `requests`, `curl_cffi`, `python-dotenv`, `python-multipart`.
  `DataManagerV2` depende sólo de `psycopg2-binary` + stdlib para su SQL.
- **Runtime frontend**: `@angular/*`, `@angular/material`, `chart.js`,
  `ng2-charts`, `marked`, `rxjs`.
- **Gobierno de deps**: `requirements.txt` con rangos abiertos (deuda de pin);
  `pip-audit` sobre el entorno resuelto + allowlist versionada; `npm audit` en el
  frontend. Ver `code-quality-assessment.md`.

## Dependencias internas cross-módulo (backend, foco del scan)

Componentes en `component-inventory.md`; grafo de relaciones en `architecture.md`.
Aristas clave (build/import) del área analizada, centradas en **quién consume
`DataManagerV2`**:

- **Routers → `DataManagerV2`** (8 consumidores directos): `endpoints/`
  `clausulable_players`, `initialize`, `matchdays`, `player_finances`, `reset_db`,
  `statistics`, `sync`, `user_stats`. Varios además con SQL inline (SQL-en-router,
  deuda a NO ampliar).
- **Adapters DDD → `DataManagerV2`** (verbatim, dependency inversion vía `Protocol`
  en `domain/ports.py`):
  - `analytics/infrastructure/data_manager_adapter.py`.
  - `assistant/infrastructure/read_adapter.py` (+ `db_connection`).
  - los 10 `sync/<ctx>/infrastructure/*_adapter.py`.
- **Servicios → `DataManagerV2`** (directo): `data_sync_service.DataSyncService`,
  `data_initializer_v2`, `futmondo_service`.
- **`DataManagerV2` → sus dependencias**: `app.core.config`
  (`CACHE_DURATION_HOURS`, `DATABASE_PATH`) + `services.db_connection.DBConnection`
  (pool PostgreSQL/Neon, `get_cursor`/`adapt_params` `?`→`%s`, singleton `get_db()`).
- **`stores/` → Neon**: `SessionRepository`/`TaskRepository` acceden a Neon vía
  `db_connection`, sin pasar por `DataManagerV2` (modelo de SQL parametrizado fuera
  de god-files).
- **Shims de compatibilidad**: `analytics_service.py` / `assistant_service.py`
  re-exportan desde `facade.py` para no romper imports históricos.

## Dependencia crítica compartida

`data_manager_v2.py` (`DataManagerV2`, ~162 KB) es la dependencia de datos común
del backend. El refactor debe apoyarse en él vía `Protocol`/adapter (como
`analytics/infrastructure/data_manager_adapter.py` y los
`sync/*/infrastructure/*_adapter.py`) **sin tocarlo ni engordarlo** (regla
afirmada): romper su superficie pública rompe las 4 oleadas DDD ya entregadas,
porque todos sus consumidores la envuelven verbatim.
