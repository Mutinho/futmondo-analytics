# Integration Test Instructions — Durabilidad del estado

> Etapa Build and Test (Construction). Estrategia **Standard**: tests de frontera clave e
> interacción cross-unit. Backend `pytest` desde `backend/`. Coste 0 €: fakes de persistencia en
> memoria (nunca Neon real). Los tests de integración de este intent ya viven, por diseño, en los
> archivos `test_durable_*_api.py` de cada unidad (integración endpoint ↔ service ↔ repository ↔
> fake DB); esta guía documenta cómo se ejecutan y qué fronteras cubren.

## Framework y configuración

- **Framework**: `pytest` + `starlette.testclient.TestClient` (via `httpx`), ya en el backend.
- **Ejecutar siempre desde `backend/`** (`pythonpath = .`, `testpaths = tests`).
- **Aislamiento**: fixtures de `backend/conftest.py` — `fake_db` (almacén en memoria que respeta el
  contrato de `db_connection`), fakes de `DataManager`/conexión, factories de API Futmondo, y
  `clean_jwt_env` para el arranque. Cada test crea y limpia su propio almacén.

## Fronteras de integración cubiertas

### u1 — Sesión durable (`test_durable_session_api.py`)
- `/auth/refresh` rehidrata la sesión desde el estado persistido (caché vacío → repositorio → BD).
- Primer uso autenticado tras "reinicio" (caché vacío): reconstruye la sesión o devuelve **401
  accionable** (no 403 opaco) — frontera endpoint ↔ `SessionService` ↔ `SessionRepository` (FR1.2/FR1.3).
- Idempotencia venga del disparador que venga (frontera de concurrencia por usuario).

### u2 — Tareas durables (`test_durable_task_api.py`)
- `/api/v1/sync/task/{id}` devuelve el último estado conocido tras "reinicio" (FR1.4) — frontera
  endpoint ↔ `TaskService` ↔ `TaskRepository` ↔ fake DB.
- `/api/v1/sync/trigger` responde **409** contra estado persistido activo y permite **relanzar** si
  la tarea previa quedó marcada interrumpida-por-reinicio (FR1.6).

### Interacción cross-unit
- u1 y u2 comparten la capa `stores/` y el fake `fake_db` (introducido en u1, reutilizado en u2). El
  arranque de `app.main` invoca ambos sweeps (`ensure_durable_session_schema` +
  `ensure_durable_task_schema` y `mark_interrupted_on_startup`), verificado por que la suite completa
  arranca y pasa (125 passed) sin colisión de esquema ni de estado.

## Cómo ejecutar los tests de integración

```bash
# desde backend/ — integración por endpoint de ambas unidades
JWT_SECRET="ci-ephemeral-test-secret-not-production" \
  pytest tests/test_durable_session_api.py tests/test_durable_task_api.py -q
```

Suite completa (recomendado como validación de no-regresión, NFR4):

```bash
# desde backend/
JWT_SECRET="ci-ephemeral-test-secret-not-production" pytest -q
```

## Objetivos de cobertura (Standard)

- Cobertura de las **fronteras de integración** listadas arriba: rehidratación de sesión, 401 vs
  403, consultabilidad de tarea tras reinicio, 409 de unicidad y relanzamiento. Sin piso porcentual
  bloqueante adicional (decisión Q3); la cobertura es referencia informativa.

## Gestión de datos y entorno de test

- **Fakes de persistencia** en memoria (`fake_db`), nunca Neon real; sin coste y determinista.
- API Futmondo simulada con las factories de `conftest.py` (éxito, credencial inválida, fallo
  transitorio).
- Cada test construye y descarta su propio almacén; sin estado mutable compartido entre tests.
