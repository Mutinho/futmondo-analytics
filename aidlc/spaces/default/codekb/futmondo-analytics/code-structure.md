# Code Structure — futmondo-analytics

## Organización de paquetes/módulos

Monorepo con dos raíces de aplicación (evidencia `README.md`, `docker-compose.yml`):

```
futmondo-analytics/
├── backend/            # FastAPI (Python 3.12) — futmondo-api
│   └── app/
│       ├── main.py                 # ASGI app: CORS, AuthMiddleware, montaje de routers
│       ├── api/v1/endpoints/       # ~20 routers HTTP + helpers
│       ├── services/               # capa de dominio + integraciones (incluye DDD y god-files)
│       ├── auth/                   # JWT (routes, jwt_utils, token_store)
│       ├── stores/                 # repositorios durables (session, task)
│       ├── security/               # protección de credenciales
│       ├── core/                   # config.py (JWT_SECRET NFR1.1)
│       └── models/                 # modelos
│   └── tests/                      # suite de caracterización pytest (32 test_*.py)
├── angular-app/        # Angular 22 + Material 22 PWA — futmondo-app
│   └── src/app/        # core/services, features, shared (+ *.spec.ts colocados)
├── proxy/              # nginx reverse proxy (local)
├── cron/               # jobs programados
└── docs/               # BACKLOG, DEPLOY, ROLLBACK, PROJECT_CONTEXT
```

## Clasificación de ficheros (capa de servicios)

Evidencia: listado de `backend/app/services/`.

- **Paquetes DDD ya extraídos (referencia)**: `analytics/` (bounded context
  completo), `prizes/` (cálculo puro + writer).
- **Shims de re-export**: `analytics_service.py` (511 bytes, re-exporta la
  fachada para no romper imports históricos).
- **God-files (deuda)**: `data_manager_v2.py` (166 173 bytes),
  `data_sync_service.py` (84 591 bytes),
  `assistant_service.py` (51 681 bytes, **objetivo del intent**),
  `photo_service.py` (22 764 bytes).
- **Clientes de integración**: `futmondo_client.py` (27 267 bytes),
  `sofascore_client.py` (16 408 bytes), `futmondo_service.py`.
- **Infra/soporte**: `db_connection.py` (adaptación de placeholders SQLite/PG
  vía `adapt_params`), `task_manager.py`, `task_service.py`, `session_service.py`,
  `data_initializer.py`, `data_initializer_v2.py`, `integration_errors.py`
  (excepciones tipadas, p. ej. `SofascoreIPBanError`), `sync_step_status.py`
  (`StepStatus.DEGRADED`).

## Patrón de código de referencia — DDD Oleada 1 (`analytics/`, `prizes/`)

Este es el patrón que el intent activo replicará en `assistant/`. Evidencia:
`backend/app/services/analytics/facade.py`,
`backend/app/services/analytics/domain/ports.py`.

- **`__init__.py`** — re-exporta la fachada del paquete.
- **`facade.py`** (`AnalyticsService`) — **fachada delgada** que preserva la
  superficie pública histórica (los 11 métodos `get_*` y el constructor sin
  argumentos) y solo delega. Inyección por constructor con default
  (`data: Optional[AnalyticsDataPort] = None`, patrón OCP): en producción
  construye el adaptador real; en test se inyecta un stub port sin
  monkeypatching. Expone atributos observables (`_team_cache`, `_player_cache`,
  `dm`) por compatibilidad hacia atrás.
- **`domain/ports.py`** (`AnalyticsDataPort`) — `typing.Protocol` estructural
  consumer-owned que describe SOLO las operaciones de datos consumidas; **sin
  SQL, sin framework**; el dominio no importa `infrastructure/`.
- **`application/calculations.py`** — lógica pura sobre el port.
- **`infrastructure/data_manager_adapter.py`** — **ÚNICO** sitio con SQL crudo
  (`db.adapt_params` + placeholders `?`); implementa el `Protocol`.
- **`prizes/`** — patrón secundario: cálculo puro (`calculator.py`) separado del
  writer de persistencia (`team_prizes_writer.py`).

## Anti-patrón a descomponer — `assistant_service.py`

Seams identificados (evidencia de fichero en el handoff del developer; detalle
de deuda en `code-quality-assessment.md`): superficie pública a preservar
`get_assistant_service()` (~líneas 1150-1158) + `async def ask(...)` (~línea
507), consumida por `backend/app/api/v1/endpoints/assistant.py`. Seams:
`AssistantUsageTracker` (tabla `assistant_usage`), capa factual
(`_try_factual_answer` + handlers `_factual_*`), `ContextBuilder`
(`_build_context` + métodos `_ctx_*`, concentra la mayoría de los 42
`cursor.execute`), y **guardrails** (`_check_guardrails`, módulo puro
regex/strings). `ask()` queda como orquestador delgado.

## Convenciones visibles

- Backend: snake_case Python; identifiers/docstrings/comments en **inglés**;
  prosa de usuario (`HTTPException.detail`) en **castellano**. Tests bajo
  `backend/tests/`, fakes in-memory en `conftest.py`.
- Frontend: camelCase TS; `*.spec.ts` colocados junto a servicios/componentes.
