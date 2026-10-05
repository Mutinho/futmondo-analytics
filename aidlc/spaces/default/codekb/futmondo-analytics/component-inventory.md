# Component Inventory

Inventario de componentes lógicos del codebase. Los encabezados de componente son
la fuente de verdad para el bloque `Scope of Analysis` de
`reverse-engineering-timestamp.md` (coincidencia literal por el rerun guard).

## data-manager-v2

- **Responsabilidad**: capa de acceso a datos monolítica (`DataManagerV2`,
  `backend/app/services/data_manager_v2.py`, ~162 KB / 3692 líneas, 57 métodos,
  148 sentencias SQL). **God-file objetivo del intent**; dependencia de datos común
  de casi todos los `sync_*`, los contextos DDD y 8 routers. Agrupa ~14
  responsabilidades (schema/lifecycle, players, teams/standings, performance,
  transactions, clauses, punishments/bonuses, dream-teams/MVP, prizes,
  market/roster, match-odds, news, users/stats/evolution, sync-metadata/cache; ver
  `api-documentation.md`). **NUNCA ampliar/reescribir**: los adapters la envuelven
  verbatim (`DataManagerV2(skip_init=True)`, kwargs originales preservados). Deuda:
  ver `code-quality-assessment.md`.
- **Dependencias**: `stores-layer`/`db_connection` (acceso físico a Neon),
  `core.config` (`CACHE_DURATION_HOURS`, `DATABASE_PATH`).

## services-layer

- **Responsabilidad**: lógica de negocio e integraciones en
  `backend/app/services/`. Incluye los facades y contextos DDD ya entregados que
  envuelven `data-manager-v2` sólo en su adapter de infraestructura: `analytics/`
  (Wave 1: `facade.py` + `application/calculations.py` + `domain/ports.py`
  `AnalyticsDataPort` + `infrastructure/data_manager_adapter.py`), `assistant/`
  (Wave 2), los 10 contextos `sync/*` (Wave 3, facade `data_sync_service.py`
  `DataSyncService`), y `prizes/` (`calculator.py` puro +
  `team_prizes_writer.replace_team_prizes`, patrón de reemplazo atómico de
  referencia). Más módulos de soporte: `db_connection.py` (`DBConnection` pool +
  `get_db()` singleton, `adapt_params` `?`→`%s`), `futmondo_client.py` /
  `sofascore_client.py` (`Integration*Error`), `data_initializer_v2.py`,
  `futmondo_service.py`, `sync_step_status.py`, `integration_errors.py`,
  `photo_service.py`, `task_*`, `session_*`.
- **Dependencias**: `data-manager-v2` (sólo en los adapters, salvo
  `DataSyncService`/`data_initializer_v2` que lo usan directo),
  `external-integration-clients`, Neon vía `db_connection`.

## api-v1-routers

- **Responsabilidad**: 23 routers REST bajo `backend/app/api/v1/endpoints/`
  (superficie HTTP interna; ver `api-documentation.md`). 8 consumen
  `data-manager-v2` directamente (`statistics`, `player_finances`,
  `clausulable_players`, `user_stats`, `sync`, `initialize`, `matchdays`,
  `reset_db`); 17 de 23 tienen SQL inline (deuda SQL-en-router a NO ampliar).
- **Dependencias**: `services-layer`, `data-manager-v2`, `data-sync-service`,
  `sync_step_status`.

## stores-layer

- **Responsabilidad**: capa de persistencia estrecha de referencia
  (`backend/app/stores/`): `SessionRepository`, `TaskRepository`, esquemas
  `ensure_*`. **Modelo de referencia** de "SQL fuera de routers y god-files, todo
  parametrizado" — la forma a la que debe tender el SQL extraído del god-file.
- **Dependencias**: Neon vía `db_connection` (`DBConnection` pool).

## data-sync-service

- **Responsabilidad**: coordinación de sincronización asíncrona
  (`data_sync_service.py`, clase `DataSyncService`). Prosa de detalle preservada
  del store previo (no re-verificada esta pasada). Consume `data-manager-v2` como
  dependencia de datos.
- **Dependencias**: `external-integration-clients`, `sync-context`,
  `prizes-context`, `data-manager-v2`.

## sync-context

- **Responsabilidad**: 10 contextos acotados DDD por dominio de sync
  (`services/sync/*`). Prosa preservada del store previo.
- **Dependencias**: `external-integration-clients`, `data-manager-v2` (sólo en el
  adapter).

## prizes-context

- **Responsabilidad**: contexto DDD de premios (`services/prizes/`): cálculo puro +
  persistencia atómica set-replacement de referencia.
- **Dependencias**: Neon (transacción atómica, DB inyectada); consumido por
  `data-sync-service`.

## analytics-context

- **Responsabilidad**: contexto DDD Wave 1 (`services/analytics/`). Shim
  `analytics_service.py`.
- **Dependencias**: `data-manager-v2` (sólo en el adapter).

## assistant-context

- **Responsabilidad**: contexto DDD Wave 2 (`services/assistant/`). Shim
  `assistant_service.py`.
- **Dependencias**: `data-manager-v2` (sólo en el adapter); LLM (`google-genai`,
  `groq`).

## external-integration-clients

- **Responsabilidad**: clientes salientes a APIs externas: `futmondo-client`
  (`Integration*Error`) y `sofascore-client` (`curl_cffi`). Incluye
  `integration_errors.py`.
- **Dependencias**: APIs Futmondo y Sofascore.

## auth-jwt

- **Responsabilidad**: autenticación JWT (`backend/app/auth/`); login/refresh/logout.
- **Dependencias**: `external-integration-clients` (validación de credenciales),
  `stores-layer`, Neon.

## backend-fastapi-app

- **Responsabilidad**: servicio web FastAPI (`backend/app/main.py`, `core/`,
  `models/`, `security/`); arranque, routing y wiring de capas.
- **Dependencias**: `api-v1-routers`, `auth-jwt`, `services-layer`, Neon vía
  `data-manager-v2`.

## angular-frontend

- **Responsabilidad**: PWA Angular 22 (`angular-app/`). Prosa preservada.
- **Dependencias**: backend REST vía nginx.

## infra-proxy-cron-ci

- **Responsabilidad**: infra de despliegue y operación: `proxy/` (nginx), `cron/`
  (Fly one-shot), `.github/workflows/` (`ci.yml`, `fly-deploy.yml`,
  `daily-sync.yml`, `sofascore-sync.yml`), Dockerfiles, `fly.toml`,
  `docker-compose.yml`.
- **Dependencias**: Fly.io, GitHub Actions, Neon.
