# Resumen de cambios — U1 sync-reliability

> Conversation language: Spanish. Backend-only, aditivo, coste 0 €. No amplía
> god-files. Estado: TODO aplicado (código de aplicación + tests) y la suite en
> verde en `python:3.12` (contenedor, coste 0 €). Sin commits.

## Cambios aplicados (FS1-FS4)

### 1. `backend/app/services/sync_step_status.py` (NUEVO) — FS1/CT1/FR3.1.1
- `StepStatus`: `RUNNING="running"`, `DONE="done"`, `DEGRADED="degraded"`.
- `ProgressSink` (Protocol): `update_progress(task_id, step, data)`, común a
  `TaskService` (durable) y `TaskManager` (cache) — resuelve R-01.
- `record_degraded_step(tm, task_id, step, reason, extra=None)`: escribe
  `progress[step]={status:"degraded", reason, **extra}` vía `tm.update_progress`
  y emite `logger.warning` estructurado (`sync_step`, `reason`). No propaga.

### 2. `backend/app/api/v1/endpoints/sync.py` — FS2/FR3.1.2
- Import de `record_degraded_step` y ramas `except` de `prizes` y `phantoms`
  cableadas a `record_degraded_step(...)` (`{"records_synced": 0}` /
  `{"total_phantoms": 0}`). El camino OK conserva `status="done"` (BR2). (Ya en
  workspace; verificado en esta unidad.)

### 3. `backend/app/api/v1/endpoints/market.py` — FS3/FR6
- Constante de módulo `PRICE_SANITY_CAP = 5_000_000_000` (ya presente).
- En `place_bid`, AÑADIDO el rechazo por techo: `if price > PRICE_SANITY_CAP ->
  HTTPException(422, "El precio de la puja excede el límite permitido")`, junto al
  `if price <= 0` existente (que se MANTIENE intacto), antes de proxyar a Futmondo.

### 4. `except` acotados — FS4/FR3.2
- `backend/app/auth/token_store.py::init_auth_tables`: el `except Exception: pass
  # Column already exists` del bucle de migraciones se ESTRECHÓ a la excepción
  esperada de "ya existe". **Corrección R-01 (revisión adversarial):** la tupla
  quedó EXACTAMENTE en (`psycopg2.errors.DuplicateColumn`,
  `psycopg2.errors.DuplicateObject`, `sqlite3.OperationalError`); se QUITÓ la
  superclase amplia `psycopg2.ProgrammingError`, que también captura
  `UndefinedTable`/`SyntaxError`/`InsufficientPrivilege` — fallos REALES de
  migración en el camino PostgreSQL productivo que ahora se RE-PROPAGAN (FR3.2/BR5:
  recuperable = `logger.debug`; fatal = re-propagar; prohibido tragar). psycopg2 se
  importa de forma perezosa y protegida (si no está, la tupla contiene solo
  `sqlite3.OperationalError` y la rama SQLite sigue funcionando). Añadido
  `import sqlite3`.
- `backend/app/services/db_connection.py::get_connection`: los dos `except
  Exception: pass` mudos del reintento de pool ahora emiten log de contexto
  (`logger.debug` en `putconn(conn, close=True)` de conn muerta; `logger.warning`
  en `closeall()` al recrear el pool). La lógica de reintento/recreación NO cambia.

### 5. Tests nuevos adyacentes — NFR3
- `backend/tests/test_sync_step_status.py` (FR3.1.1/BR1): payload `degraded` +
  `reason` + `extra` vía `ProgressSink` doble; `logger.warning` estructurado
  capturado con `caplog` (`sync_step`, `reason`); constantes de `StepStatus`.
- `backend/tests/test_sync_degraded_steps.py` (FR3.1.2/BR1/BR2): `prizes`/`phantoms`
  que lanzan quedan `degraded` (no `done`); un paso que no lanza conserva `done`;
  el degradado no marca la tarea como fallida. Fake `TaskManager` en memoria.
- `backend/tests/test_market_bid_sanity_cap.py` (FR6/BR4): `price>cap` -> 422 y el
  cliente Futmondo NO se invoca; `price==cap` -> 200 (inclusivo); `price<=0` -> 422
  (no regresión); `price` intermedio -> 200 e invoca al cliente (mock, sin red).
- `backend/tests/test_token_store_migrations.py` (FR3.2/BR5 — guarda de R-01): un
  error de migración que NO es de "ya existe" (`psycopg2.errors.UndefinedTable`
  cuando psycopg2 está disponible en CI, `RuntimeError` si no) se RE-PROPAGA desde
  `init_auth_tables` (`pytest.raises`); un `RuntimeError` genérico también se
  propaga; y un `sqlite3.OperationalError` de "columna duplicada" SÍ se traga
  (idempotencia). Fake `db` que honra el contrato `db_connection`, inyectado vía
  `monkeypatch` de `get_db`; sin red ni BD. Verificado como guarda efectiva: con la
  `ProgrammingError` amplia re-añadida, el test de propagación FALLA ("DID NOT RAISE
  UndefinedTable").
- Aserciones reales en todos; nunca `assert True`.

## Verificación (ejecución de pytest)

Runner en contenedor `python:3.12` (CI usa 3.12; el Python del sistema es 3.14 y
`libsql-experimental==0.0.55` no compila fuera de 3.12). Coste 0 €.

**Corrección R-01 (revisión adversarial NOT-READY → READY):** tras estrechar la
tupla de excepciones de `init_auth_tables` y añadir el test de propagación, la
suite COMPLETA queda VERDE **166 passed, 1 warning** (línea base previa 163 + 3
tests nuevos; +2 respecto de la ronda anterior, del nuevo
`test_token_store_migrations.py`). Sin regresión.

```bash
docker run --rm -v "$PWD":/repo -w /repo/backend -e JWT_SECRET=test-secret-not-default-000 python:3.12 bash -c "pip install --quiet -r requirements.txt; python -m pytest tests -ra"
# => 166 passed, 1 warning
```

Tests de la unidad (incluida la guarda de R-01), VERDE:

```bash
docker run --rm -v "$PWD":/repo -w /repo/backend -e JWT_SECRET=test-secret-not-default-000 python:3.12 bash -c "pip install --quiet -r requirements.txt; python -m pytest tests/test_sync_step_status.py tests/test_sync_degraded_steps.py tests/test_market_bid_sanity_cap.py tests/test_token_store_migrations.py -ra"
```

Prueba de que el test guarda R-01 de verdad: re-añadiendo temporalmente
`psycopg2.ProgrammingError` a la tupla, `test_non_duplicate_migration_error_propagates`
FALLA con "DID NOT RAISE UndefinedTable"; con la tupla estrecha, pasa.

Solo los tests nuevos de la ronda previa (13 tests, VERDE):

```bash
docker run --rm -v "$PWD":/app -w /app -e JWT_SECRET=test-secret-not-default-000 python:3.12 bash -c "
pip install --quiet 'fastapi>=0.104.0' 'pydantic>=2.5.0' 'requests>=2.31.0' 'psycopg2-binary>=2.9.9' 'PyJWT==2.9.0' 'python-dotenv>=1.0.0' 'python-multipart>=0.0.6' 'pytest>=8.0.0' 'httpx>=0.27.0'
python -m pytest tests/test_sync_step_status.py tests/test_sync_degraded_steps.py tests/test_market_bid_sanity_cap.py -ra
"
# => 13 passed
```

Suite completa de la ronda previa (163 tests, VERDE — antes de la corrección R-01;
la cifra vigente es 166, arriba). Se monta la RAÍZ del repo para
que `test_tls_verification.py` resuelva `docker-compose.yml`:

```bash
docker run --rm -v "$PWD":/repo -w /repo/backend -e JWT_SECRET=test-secret-not-default-000 python:3.12 bash -c "
pip install --quiet -r requirements.txt
python -m pytest tests -ra
"
# => 163 passed, 1 warning
```

`py_compile` de los ficheros modificados: OK. `ruff check` de los ficheros
tocados: solo 18 avisos PRE-EXISTENTES (`F841 except Exception as e/exc` en
cuerpos no autorados por esta unidad); las líneas añadidas no introducen avisos
nuevos. No se corrió `ruff format` (regla brownfield: no reformatear en masa).

## Sources
- `functional-design/functional-spec.md` (FS1-FS4), `functional-design/rules.md`
  (BR1-BR5), `functional-design/entities.md`.
- `inception/contract-design/contract-summary.md` (CT1-CT4).
- `inception/requirements-analysis/requirements.md` (FR3.1/FR3.2/FR6, NFR1-NFR5).
- Código verificado en workspace: `sync.py` (ramas prizes/phantoms),
  `market.py::place_bid`, `auth/token_store.py::init_auth_tables`,
  `services/db_connection.py::get_connection`.
- Patrón de test replicado de `tests/test_market_bid_validation.py` y del fake DB
  de `conftest.py`.

## Assumptions & Open Questions
- El estado `degraded` se añade de forma aditiva a `progress` (JSON libre) sin
  migración de BD; confirmado por `entities.md` y CT2.
- `PRICE_SANITY_CAP` es inclusivo: exactamente en el techo es una puja válida
  (el rechazo es estrictamente `> cap`), congelado por
  `test_bid_price_at_cap_is_allowed_and_invokes_client`.
- El `except` que probe psycopg2 en `token_store.py` es una detección de entorno,
  no un fallo de migración; en un entorno solo-SQLite se conserva la rama
  `sqlite3.OperationalError`. Tras R-01 la tupla de "ya existe" NO incluye la
  superclase `psycopg2.ProgrammingError`: un fallo real de migración (p. ej.
  `UndefinedTable`) se re-propaga en el camino PostgreSQL productivo.
