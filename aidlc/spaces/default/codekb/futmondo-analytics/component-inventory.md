# Component Inventory

Inventario de componentes lógicos del codebase. Los encabezados de componente son
la fuente de verdad para el bloque `Scope of Analysis` de
`reverse-engineering-timestamp.md` (coincidencia literal por el rerun guard).

## backend-fastapi-app

- **Responsabilidad**: servicio web FastAPI (Python 3.12); arranque, routing y
  wiring de capas (`backend/app/main.py`, `core/`, `models/`, `security/`).
- **Dependencias**: `api-v1-routers`, `auth-jwt`, `services-layer`, Neon vía
  `data-manager-v2`.

## api-v1-routers

- **Responsabilidad**: 21 routers REST bajo `backend/app/api/v1/endpoints/`
  (superficie HTTP interna; ver `api-documentation.md`). Incluye `sync.py` (sync
  router + worker en background `_run_sync_in_background`, 4 endpoints:
  `/status`, `/last-sync`, `/trigger`, `/task/{id}`).
- **Dependencias**: `services-layer`, `data-sync-service`, `task_service`,
  `sync_step_status`; deuda de SQL-en-router contra `data-manager-v2`
  (`_check_phantoms`, `get_last_sync_date`).

## auth-jwt

- **Responsabilidad**: autenticación JWT y session/token stores
  (`backend/app/auth/`, `stores/`); login/refresh/logout.
- **Dependencias**: `futmondo-client` (validación de credenciales), Neon.

## data-sync-service

- **Responsabilidad**: coordinación de sincronización asíncrona; god-file
  objetivo del intent (`data_sync_service.py` ~77 KB / ~1806 líneas, clase
  `DataSyncService`: 10 `sync_*` + `sync_all()` con 10 claves literales y orden
  fijo). `sync_match_odds` y `sync_clauses` ya delegan en `sync-context`;
  `sync_prizes` delega cálculo/escritura en `prizes-context`. Aloja aún 8 dominios
  inline + 5 helpers privados (`_find_championship`, `_store_bids`,
  `_enrich_market_values`, `_find_price_at_date`, `_save_favorites`,
  `_log_integration_failure`). Ver `api-documentation.md`.
- **Dependencias**: `futmondo-client`, `sofascore-client`, `sync-context`,
  `prizes-context`, `data-manager-v2`, `integration-errors`, `core.config`.

## sync-context

- **Responsabilidad**: contexto acotado DDD por dominio de sync
  (`services/sync/`): raíz del árbol de descomposición del god-file con DOS
  pilotos completos (`match_odds` shape ligero + `clauses` shape paginado), cada
  uno con `orchestrator.py` + `domain/ports.py` (Protocol consumer-owned) +
  `infrastructure/<domain>_adapter.py` que envuelve `DataManagerV2` verbatim.
  Patrón de referencia a replicar para los 8 dominios pendientes. Ver
  `code-structure.md`.
- **Dependencias**: `futmondo-client` (ingesta inyectada), `data-manager-v2`
  (sólo en el adapter), `integration-errors`.

## prizes-context

- **Responsabilidad**: contexto acotado DDD de premios (`services/prizes/`):
  cálculo puro (`calculator.py`) + persistencia atómica set-replacement
  (`team_prizes_writer.py`, `replace_team_prizes`). Patrón de referencia del
  refactor; aún le falta el facade/orchestrator uniforme (la orquestación de
  `sync_prizes` sigue inline en el god-file).
- **Dependencias**: Neon (transacción atómica, DB inyectada vía `_DbLike`
  Protocol); consumido por `data-sync-service`.

## analytics-context

- **Responsabilidad**: contexto acotado DDD oleada 1 (`services/analytics/`):
  `domain/ports.py`, `application/calculations.py`,
  `infrastructure/data_manager_adapter.py`, `facade.py`. Shim `analytics_service.py`.
- **Dependencias**: `data-manager-v2` (solo en el adapter).

## assistant-context

- **Responsabilidad**: contexto acotado DDD oleada 2 / FR13 (`services/assistant/`):
  `domain/`, `application/`, `infrastructure/`, `facade.py`. Shim `assistant_service.py`.
- **Dependencias**: `data-manager-v2` (solo en el adapter); posibles LLM
  (`google-genai`, `groq`).

## data-manager-v2

- **Responsabilidad**: acceso a datos monolítico (`DataManagerV2`,
  `data_manager_v2.py` ~166 KB); dependencia de datos común de casi todos los
  `sync_*` y routers. God-file (deuda, ver `code-quality-assessment.md`);
  **NUNCA ampliar/reescribir**, los adapters la envuelven verbatim
  (`DataManagerV2(skip_init=True)`, kwargs originales preservados).
- **Dependencias**: Neon PostgreSQL (`db_connection.py`).

## external-integration-clients

- **Responsabilidad**: clientes salientes a APIs externas: `futmondo-client`
  (`futmondo_client.py`, excepciones tipadas `Integration*Error`) y
  `sofascore-client` (`sofascore_client.py`, `curl_cffi`). Incluye
  `integration_errors.py`.
- **Dependencias**: APIs Futmondo y Sofascore.

## services-layer (otros)

- **Responsabilidad**: servicios y utilidades de soporte restantes
  (`analytics_service.py`, `photo_service.py`, `data_initializer*.py`, `task_*`,
  `session_*`, `sync_step_status.py` — `record_degraded_step` + `StepStatus`).
- **Dependencias**: `data-manager-v2`, `data-sync-service`.

## angular-frontend

- **Responsabilidad**: PWA Angular 22 (`angular-app/`): `core/`, `features/`,
  `shared/`; consume la API v1 y muestra presupuesto, mercado, sync, finanzas,
  analítica.
- **Dependencias**: backend REST vía nginx.

## infra-proxy-cron-ci

- **Responsabilidad**: infra de despliegue y operación: `proxy/` (nginx),
  `cron/` (Fly one-shot sync programado), `.github/workflows/`
  (`ci.yml`, `fly-deploy.yml`, `daily-sync.yml`, `sofascore-sync.yml`),
  Dockerfiles, `fly.toml`, `docker-compose.yml`.
- **Dependencias**: Fly.io, GitHub Actions, Neon.
