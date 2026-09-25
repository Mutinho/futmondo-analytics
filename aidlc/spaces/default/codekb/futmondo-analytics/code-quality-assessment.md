# Evaluación de Calidad del Código — futmondo-analytics

## Cobertura de Tests, Linting y CI/CD

### Tests — Backend

- `pytest` + `pytest-cov`, ejecutado desde `backend/` (`pytest.ini`: `testpaths=tests`,
  `pythonpath=.`, `addopts = -ra`). **Sin piso de cobertura bloqueante** — no existe
  `cov-fail-under`/`fail_under` (ratcheting diferido, decisión de equipo). Suite `pytest`
  con ~27 ficheros; fixtures compartidas en `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`
  SQLite `:memory:` honrando el contrato de `db_connection` con ISO-encode de datetime como
  el wrapper Turso, `clean_jwt_env`, `fake_db`). Sin red, sin DB real, sin credenciales.
- **Cobertura existente relevante al área de fiabilidad (intent activo)**:
  - `test_sync_degraded_steps.py` — congela que un paso no crítico que lanza queda
    `status="degraded"` (nunca `done`) y que NO falla la tarea (FR3.1/BR1/BR2).
  - `test_sync_step_status.py` — unidad del helper `StepStatus`/`record_degraded_step`.
  - `test_sofascore_sync_characterization.py` — regresión del reemplazo transaccional de
    caché (DELETE+INSERT atómico) + señalización de baneo (`should_apply_replacement`,
    `SofascoreIPBanError`).
  - `test_durable_task_*` (service/repository/api/characterization) — contrato de
    durabilidad de tareas (autoridad DB, caché best-effort, barrido interrupted-by-restart).
  - **GAP (área de fiabilidad)**: NO existe caracterización de `futmondo_client._make_request`
    ni de las 29 ramas `except Exception` de `data_sync_service.py`; el punto de
    corromper-datos (`DELETE ... NOT IN` en `team_prizes`) tampoco tiene test directo de su
    modo de fallo.
- **Cobertura existente relevante al área de premios/finanzas**:
  - `test_finance_characterization.py` — caracteriza el CONSUMO
    (`player_finances.get_player_finances`) con doble de `DataManagerV2` + `get_db` falso.
  - `test_analytics_service.py` — caracteriza `AnalyticsService` con `StubDM`.
  - `test_prizes_characterization.py` / `test_prizes_calculator.py` — congelan `sync_prizes`
    (intent previo).
- **Cobertura existente relevante a intents de seguridad**:
  - **FR18**: `test_db_admin_guard.py` (404 por defecto / no-afirmativo, 200 con
    `ENABLE_DB_ADMIN=1`).
  - **FR9**: `test_auth_characterization.py` (caracteriza el bug de `is_refresh_token_valid`).
  - **NFR1.1**: `test_jwt_startup.py` cubre `resolve_jwt_secret`.

### Tests — Frontend

Estado (línea base evolucionada por el intent `260918-frontend-coverage-gate`): runner
**Vitest** (`^4.0.8`) + `jsdom` (`^25.0.1`) vía el builder `@angular/build:unit-test`
(`angular.json` → `architect.test.runner: vitest`). Migración a Vitest COMPLETA (sin restos
Karma/Jasmine). Los specs de referencia (`core/interceptors/auth.interceptor.spec.ts`,
`core/preloading/idle-preloading-strategy.spec.ts`) fijan el patrón Vitest +
`@angular/*/testing`. El área de cobertura del frontend NO es el foco de ESTE intent;
el detalle histórico se preserva sin re-verificar.

### Linting

- **Backend**: `ruff` (`backend/ruff.toml`: `target-version = py312`, `line-length = 100`,
  `select = ["E","F","I"]`, `ignore = ["E501","E402","E722"]`) — **advisory** en CI
  (`continue-on-error`). **Punto clave del intent activo**: **`E722` (bare-except) está en
  `ignore`**, así que el linter NO señala los `except:` desnudos ("try/except amplios
  heredados en la capa de datos"). Cualquier objetivo de FR3.2 que quiera enforcement de
  bare-except deberá RE-HABILITAR `E722` por trinquete, aislando el reflow (regla afirmada de
  NO reformatear brownfield en masa).
- **Frontend**: ESLint flat config (`eslint.config.js`, Angular) — **advisory**
  (`continue-on-error: true`). Dependencias de ESLint declaradas pero no instaladas. Prettier
  `^3.8.1` disponible.

### CI/CD

Dos caminos de verificación, AMBOS con `pytest` y `ng test --watch=false` BLOQUEANTES:

- **`.github/workflows/ci.yml`** (PR→`main`, job `quality`): gitleaks (BLOQUEANTE) → Python
  3.12 + install → `ruff check` (advisory) → `pytest tests -q --cov=app --cov-report=term-missing`
  (BLOQUEANTE, **CON cobertura**) → `pip-audit` (advisory) → Node `'22'` + `npm ci` →
  `ng lint` (advisory) → **`ng test --watch=false` (BLOQUEANTE)** → `npm audit` (advisory).
- **`.github/workflows/fly-deploy.yml`** (push→`main`, `workflow_dispatch`): job `verify` =
  gitleaks@v2 (BLOQUEANTE) → `pytest tests -q` (BLOQUEANTE, **SIN `--cov`**) → Node `'22'` +
  `npm ci` → **`ng test --watch=false` (BLOQUEANTE)**. Luego `deploy-backend` →
  `deploy-frontend` (Fly.io) → `smoke-test` a `/health` (5 reintentos, HTTP 200).
- **Crons**: `daily-sync.yml` (04:30 UTC), `sofascore-sync.yml` (05:00 UTC) — máquinas Fly
  one-shot (coste ~0).

### Documentación

- README extenso (raíz y `angular-app/`); `docs/` incluye `docs/DEPLOY.md`, `docs/ROLLBACK.md`,
  `docs/PR-GATE.md`, backlogs de intents previos; `AGENTS.md`. Docstrings en inglés; texto de
  usuario / `HTTPException.detail` en castellano. Docstrings ricos con trazas a FR/BR en los
  ficheros nuevos/tocados por intents recientes (`sync_step_status.py`, `task_service.py`,
  `sofascore_client.py`); los god-files (`data_sync_service.py`, `data_manager_v2.py`) tienen
  docstrings dispersos. `main.py` lleva comentarios de seguridad (FR7/NFR1.6).

## Deuda Técnica y Hallazgos

Este artefacto es el propietario del detalle de deuda; el resto de artefactos referencian
aquí en lugar de repetir.

### Fiabilidad del backend — Manejo de errores y contratos (intent activo — hallazgo propietario)

El backend YA tiene un **vocabulario recuperable-vs-fatal parcial y de buena calidad**,
aplicado de forma DESIGUAL. Éste es el punto de partida real de FR3.2/FR4.

**Señales recuperable-vs-fatal YA presentes (base sólida sobre la que construir):**

- **`sofascore_client.py` (patrón de referencia)**: distingue el **fatal de repoblado**
  (`SofascoreIPBanError` en 403, con `except SofascoreIPBanError: raise` ANTES del
  `except Exception` genérico → NO se traga) del **recuperable/no-encontrado** (404 → `None`;
  otro status → warning + `None`). Es el patrón EXACTO que FR4 debe replicar en Futmondo:
  excepción tipada + `except <Typed>: raise` antes del genérico.
- **`db_connection.py`**: `get_connection()` hace `rollback()` + `raise` ante cualquier
  `Exception` (fatal, no traga); el `ThreadedConnectionPool` (5-20) reintenta hasta 3 veces
  conexiones muertas y recrea el pool como último recurso (recuperable a nivel de
  infraestructura); `_test_connection()` re-lanza en fallo de arranque. Contiene 9 ramas
  amplias.
- **`sync_step_status.record_degraded_step` (FR3.1)**: seam explícito que marca
  `StepStatus.DEGRADED` para fallos NO críticos ya capturados (registra, NO re-lanza),
  consumido por `sync.py` en `prizes`/`phantoms` (~L120-200). Ya caracterizado.
- **`task_service._cache_call`**: separa la **autoridad** (DB, debe tener éxito →
  `TaskPersistenceError`) del **best-effort** (`task_manager`, caché que traga y loguea
  warning, nunca falla la operación).
- **Arranque resiliente en `main.py`**: la init de tablas usa
  `try/except Exception → logger.warning` (degrada, NO aborta el boot; loguea, NO es swallow
  silencioso).

**Huecos de FR3.2/FR4 (foco del intent):**

- **FR4 — `futmondo_client._make_request` colapsa el fallo a `None`**: traga `Timeout`,
  `RequestException` y `JSONDecodeError` y devuelve `None`; `login()` devuelve `bool` y los
  getters devuelven `Optional`. NO distingue recuperable de fatal ni expone modo de fallo
  tipado; el llamador sólo ve "sin datos". **Es el hueco central de FR4.** Introducir una
  excepción tipada (replicando `SofascoreIPBanError`) es un **cambio de contrato con blast
  radius alto**: muchos `sync_*`/`get_*` del god-file de sync asumen `None == sin datos`;
  hay que mapear los llamadores antes de tocarlo.
- **FR3.2 — 29 ramas `except Exception` en `data_sync_service.py`** (L42, 116, 198, 223, 233,
  273, 355, 379, 407, 502, 531, 623, 685, 757, 784, 965, 1007, 1068, 1128, 1157, 1281, 1314,
  1461, 1467, 1478, 1506, 1564, 1859, 1875): 0 bare-except; todas capturan `Exception`,
  muchas hacen `logger.error(..., exc_info=True)` + `return {"status":"error", ...}`. Sin
  clasificación recuperable/fatal uniforme.
- **`data_manager_v2.py` — 3 `except: pass` (swallow silencioso real)** (L57-58, L68-69,
  L672-673) + 23 ramas amplias. **SKIMMED** (fuera del snapshot profundo, sólo conteo/
  localización): confirmar en diseño antes de tocarlos. `photo_service.py` tiene otro
  `except: pass` (L475-476). Total `except: pass` catalogados en `app/services/`: 4.
- **`E722` en `ignore` (`ruff.toml`)**: el linter NO vigila los `except:` desnudos hoy; el
  enforcement de bare-except no existe sin re-habilitar la regla.

**Punto de corromper-datos ("no corromper datos"):**

- En `data_sync_service.py`, el bloque de premios hace `INSERT ... ON CONFLICT DO UPDATE`
  (L1816) seguido de `conn.commit()` (L1825) y DESPUÉS **`DELETE FROM team_prizes ... matchday
  NOT IN (...)`** (L1846), cuyo `try/except Exception → logger.warning` (L1859) **traga el
  fallo de limpieza tras el commit previo**. Si el `DELETE` falla, la caché queda en estado
  mixto (matchdays obsoletos + nuevos) SIN señal al consumidor de lectura
  (`balances`/`player_finances`). El patrón correcto de referencia es el reemplazo
  transaccional atómico (DELETE+INSERT en la misma transacción) del caché de Sofascore, ya
  caracterizado. Otros puntos de escritura del worker: `UPDATE transactions` (L269, L350),
  `DELETE/INSERT player_favorites` (L1367/L1378/L1385).

**Riesgos de mapeo (FR4):** cambiar el contrato de señalización de fallo del cliente Futmondo
(de `None`/`bool` a excepción tipada) toca MUCHOS llamadores en un god-file de 1915 líneas;
sin caracterización previa el riesgo de regresión es alto. Caracterizar primero con dobles/
fakes en memoria (patrón `conftest.py`), coste 0 €.

### Cobertura del frontend y pipeline (intent previo — hallazgo preservado)

- **Asimetría de cobertura backend (preexistente, DIFERIDA)**: `verify` (fly-deploy.yml)
  corre `pytest -q` **sin `--cov`** mientras `ci.yml` mide `--cov=app`. Es diferencia de
  SEÑAL DE COBERTURA, **no de seguridad**: gitleaks es BLOQUEANTE en AMBOS caminos (`@v3` en
  PR, `@v2` en `verify`, sin `continue-on-error`). Cualquier piso de cobertura backend futuro
  debe cablearse en AMBOS caminos. Deuda registrada, fuera de alcance de este intent.
- **Dependencias de ESLint declaradas pero no instaladas** (`angular-eslint`/
  `typescript-eslint`/`@eslint/js`): lint frontend sólo advisory best-effort.
- **Directorio residual** `angular-app/node_modules.old-*`: ruido de repo (no afecta build).

### Área de premios/finanzas (hallazgo preservado)

- **Fórmula de premios en un god-file** (`services/data_sync_service.py::sync_prizes`,
  ~1577-1885): toda la lógica monetaria vive embebida con SQL crudo y llamadas a la API de
  Futmondo con `time.sleep()`. Debe extraerse tras una capa/función estrecha testeable, **sin
  ampliar** el god-file ni el patrón SQL-en-router (`project.md`).
- **Doble semántica de "puntos"**, **resolución de identidad frágil** en `player_finances`,
  **SQL inline en routers de analítica/saldos** (`classification-full`, `watchlist`):
  anti-patrones a no ampliar.

### Área de seguridad (intents anteriores, por FR — preservado)

- **FR6 — validación de puja ausente en backend** (`market.py::place_bid`): acepta
  `price: int = Query(...)` sin validar rango/positividad; la única validación vive en el
  frontend (`bid-dialog.component.ts`), evadible.
- **FR7 — exposición del endpoint de fotos**: `GET /api/v1/photos/{player_id}` SÍ exige
  Bearer; el punto real es `/static/photos/*` (StaticFiles) fuera del prefijo protegido.
- **FR8 — `SSL_VERIFY=0` huérfano**: declarado en `docker-compose.yml` (local) sin lector en
  Python (0 usos); ausente de `backend/fly.toml [env]`.
- **FR9 — bug de precedencia naive/aware** en `token_store.is_refresh_token_valid`: con
  `expires_at` aware (PostgreSQL/Turso) el ternario devuelve un `datetime` truthy →
  `return False`, rechazando tokens ACTIVOS futuros.
- **FR18 — guarda de administración**: `_require_db_admin()`/`ENABLE_DB_ADMIN` correcta y
  testeada.

### Deuda estructural (no ampliar — preservado)

- **SQL crudo disperso** en `auth/token_store.py`, `routes._auto_detect_championships`,
  `_helpers.get_championship_config`, `balances.py`, `analytics.py` sin capa repositorio.
- **God-files** en `services/`: `data_manager_v2.py` (~166 KB), `data_sync_service.py`
  (~84 KB / 1915 líneas), `assistant_service.py` (~51 KB). No deben crecer.
- **Imports dinámicos** dentro de funciones; preferir import estático.
- **Cobertura de errores amplia**: bloques `except Exception` que mapean a 500 / `None` sin
  distinguir causas (núcleo del área FR3.2).

### Riesgos de contexto

- Los scripts one-shot `scripts/migrate_to_turso.py` / `migrate_data_to_turso.py` usan
  `except Exception as e` con log (5 ramas), NO `except: pass`: el patrón "except: pass en
  migración/startup" del brief NO se materializa aquí (loguean). Sólo son utilidades, no
  parte del servicio web.
- `libsql-experimental==0.0.55` sólo compila en Python 3.12 (los tests usan fakes SQLite).
- Restricción dura de coste 0 € en toda propuesta.
