# Code Structure

## Organización de paquetes/módulos

Mono-repo con dos apps desplegables más soporte de infra:

- `backend/app/` — servicio web FastAPI (Python 3.12). Capas:
  - `api/v1/endpoints/` — 21 routers REST (ver `api-documentation.md`).
  - `services/` — lógica de negocio + integraciones (núcleo del intent).
  - `auth/` — JWT + session/token stores.
  - `stores/` — repositorios de durabilidad.
  - `core/` — config/constants.
  - `models/`, `security/`.
  - `main.py` — arranque FastAPI.
- `angular-app/` — frontend Angular 22 (PWA, standalone components, signals,
  Material 22): `src/app/{core,features,shared}`.
- `proxy/` — nginx reverse proxy local.
- `cron/` — máquinas Fly one-shot para sincronizaciones programadas.
- `docs/`, `scripts/`, `docker-compose.yml`, `.github/workflows/`.

## Clasificación de ficheros (backend `services/`)

### Contextos DDD ya extraídos (patrón objetivo)

- `prizes/` — contexto acotado (oleada previa): `calculator.py` (cálculo puro),
  `team_prizes_writer.py` (persistencia atómica set-replacement), `__init__.py`.
- `analytics/` — oleada 1 (DDD completo): `domain/ports.py` (Protocol
  consumer-owned, sin SQL), `application/calculations.py` (cálculo puro sobre el
  port), `infrastructure/data_manager_adapter.py` (único sitio con SQL crudo sobre
  `DataManagerV2`), `facade.py` (servicio de aplicación fino que preserva la
  superficie pública).
- `assistant/` — oleada 2 (FR13, DDD): `domain/`, `application/`,
  `infrastructure/`, `facade.py`.
- **Shims de re-export**: `analytics_service.py`, `assistant_service.py`
  (ya reducido a shim) mantienen la ruta histórica de import sin romper llamadores.

### God-files (deuda; ver `code-quality-assessment.md`)

- `data_sync_service.py` (1955 líneas, ~84 KB) — **objetivo del intent**. Define
  `DataSyncService` (L67) con 10 `sync_*` + `sync_all()` (L1925, coordinador fino).
- `data_manager_v2.py` (3692 líneas, ~166 KB) — SQL/acceso a datos monolítico
  (`DataManagerV2`), dependencia de datos común de casi todos los `sync_*`.
- `photo_service.py` (492 líneas) — deuda `E722` registrada.

### Otros módulos de servicios (skimmed)

`futmondo_client.py`, `sofascore_client.py`, `data_initializer*.py`,
`task_*`, `session_*`, `db_connection.py`, `integration_errors.py`,
`sync_step_status.py`.

## Patrones de código

- **Patrón objetivo DDD (a replicar)**: domain port (Protocol) → application
  (cálculo puro) → infrastructure (`*_adapter.py`, único SQL) → `facade.py` fino →
  shim de re-export. Demostrado en `analytics/` y `assistant/`; `sync_prizes` es el
  ejemplo dentro del propio god-file (orquesta ingesta, delega cálculo a
  `calculate_round_prizes`, persiste con `replace_team_prizes`).
- **Set-replacement + escritura atómica**: upsert de todo el conjunto y
  `DELETE ... NOT IN (...)` de filas stale en una sola transacción
  (`team_prizes_writer.replace_team_prizes`), all-or-nothing.
- **Anti-patrones heredados (NO ampliar, regla afirmada)**:
  - **SQL-en-router**: casi todos los routers ejecutan `cursor.execute`/SQL crudo
    inline en vez de delegar en un servicio/adaptador.
  - **Métodos mixtos**: 8 de 10 `sync_*` mezclan ingesta + SQL/persistencia +
    cálculo en el mismo método; solo `sync_prizes` ya delega.
  - **`except Exception → return {"status":"error"}`** como red final por método;
    `time.sleep()` de throttling incrustado.
- **Convenciones**: identificadores/docstrings/comentarios en inglés; texto de
  usuario y mensajes de commit en castellano; snake_case Python, camelCase TS.
  Docstrings ricos en el código nuevo (waves DDD), escasos en los god-files.
