# Developer Code Scan — 260923-backend-fiabilidad-error

> Enlace 1 del pipeline de Reverse Engineering. Escaneo FOCALIZADO sobre el área
> de fiabilidad del backend (FastAPI / Python 3.12 en `backend/`). Proyecto
> brownfield: NO se propone reescritura de los god-files; este escaneo cataloga
> el estado real del manejo de excepciones, la señalización recuperable-vs-fatal
> y los puntos donde el camino de sync escribe datos ("no corromper datos").

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply**:
  - backend/app/main.py
  - backend/app/services/db_connection.py
  - backend/app/services/sofascore_client.py
  - backend/app/services/futmondo_client.py
  - backend/app/services/data_sync_service.py (leído la región de escritura de premios ~L1795–1915 en detalle; el resto del fichero de 1915 líneas catalogado por conteo/localización de `except`, sin lectura línea a línea de las 29 ramas)
  - backend/app/services/sync_step_status.py
  - backend/app/services/task_manager.py
  - backend/app/services/task_service.py
  - backend/scripts/migrate_to_turso.py (cabecera + patrón de `except`)
  - backend/scripts/migrate_data_to_turso.py (cabecera + patrón de `except`)
  - backend/tests/conftest.py
  - backend/tests/test_sync_degraded_steps.py
  - backend/tests/test_sofascore_sync_characterization.py (preámbulo + lógica pura)
  - backend/app/api/v1/endpoints/sync.py (rama de pasos degradados prizes/phantoms, ~L120–200)
  - backend/pytest.ini, backend/ruff.toml, backend/requirements.txt
  - .github/workflows/ci.yml + fly-deploy.yml (comandos de test/cobertura backend — grep dirigido)

- **Skimmed only** (granularidad de directorio; NO leídos en profundidad):
  - backend/app/services/data_manager_v2.py (~166 KB god-file; solo conteo de `except`: 23 ramas amplias, 3 `except: pass`)
  - backend/app/api/v1/endpoints/ (resto de routers; solo conteo de `except` por fichero)
  - backend/app/stores/ (task_repository, session_repository — referenciados desde task_service/main pero fuera del snapshot de coverage profunda)
  - backend/app/auth/, backend/app/core/config.py (referenciados; no leídos)
  - backend/scripts/ restantes (sync_sofascore_local.py, sync_data.py, fetch_user_finances_data.py, etc.)
  - backend/tests/ restantes (~24 ficheros; nombres catalogados, contenido no leído salvo los 2 citados)

> Nota de límite: me mantuve dentro del snapshot de coverage acordado. `data_manager_v2.py` NO estaba en el
> conjunto profundo; solo lo cuento a nivel de señal de deuda porque comparte el patrón de `except: pass`.

### Packages Found

- `app` — paquete FastAPI principal — Python — API multi-usuario de análisis Futmondo.
  - `app.services` — lógica de negocio y clientes externos (sync, clientes Sofascore/Futmondo, task manager, helper de degradación).
  - `app.api.v1.endpoints` — routers HTTP (sync, market, analytics, etc.).
  - `app.stores` — repositorios durables (`task_repository`, `session_repository`) — autoridad de estado en DB.
  - `app.auth` — JWT, token store, rutas `/auth/*`.
  - `app.core` — `config.py` (variables de entorno, tipo de DB, URLs base).
- `scripts` — utilidades one-shot (migraciones a Turso, sync local, exports). No forman parte del servicio web.
- `tests` — suite pytest de caracterización + regresión (fakes, sin red ni DB real).

### Build System

- **Type**: pip / setuptools (sin poetry). Contenedor Docker (`backend/Dockerfile`), despliegue Fly.io (`backend/fly.toml`), `nixpacks.toml` presente.
- **Config Files**: `requirements.txt`, `pytest.ini`, `ruff.toml`, `conftest.py`, `Dockerfile`, `fly.toml`, `nixpacks.toml`, `entrypoint.sh`, `run.py`.
- **Build Dependencies** (relaciones de módulos relevantes al intent):
  - `app.main` → `task_service.get_task_service()` (barrido de interrumpidos en startup), `session_repository`, `task_repository`, routers.
  - `app.api.v1.endpoints.sync` → `data_sync_service` (worker), `sync_step_status.record_degraded_step`, `task_manager`.
  - `task_service.TaskService` → `task_repository.TaskRepository` (autoridad) + `task_manager.TaskManager` (caché best-effort).
  - `data_sync_service` → `db_connection.DBConnection`, `futmondo_client`, `sofascore_client`, `data_manager_v2` (dm).

### APIs Discovered

- **API interna (FastAPI)** — `app/main.py` monta ~24 routers bajo `/api/v1/*` y `/auth/*`; `AuthMiddleware` exige Bearer JWT salvo `AUTH_EXCLUDED_PATHS` (`/auth/login|refresh|logout`, `/health`, `/`, `/docs`, `/openapi.json`, `/redoc`) y el montaje público intencional `/static/photos/*`. `/health` devuelve `{"status":"healthy"}` (usado por el smoke-test de Fly.io).
- **Cliente externo Futmondo** (`futmondo_client.py`) — POST JSON al patrón `{header:{token,userid}, query:{...}, answer:{}}` contra `BASE_URL`. Endpoints: `/5/login/with_mail`, `/5/league/championshipplayers`, `/1/player/summary`, `/2/championship/teams`, `/1/userteam/{nightmareteam,dreamteam,rounds,roster,roundlineup}`, `/1/match/list`, `/1/ranking/round`, `/1/market/players`, `/1/locker/pressroom`, `/1/player/fullprofile`, `/2/locker/news`, `/2/league/list`. Contrato de éxito: `answer.code == "api.general.ok"` + `mobile.code == "login.mobile.ok"` en login.
- **Cliente externo Sofascore** (`sofascore_client.py`) — GET no oficial contra `https://api.sofascore.com/api/v1` vía `curl_cffi` (impersonate chrome, throttle 750 ms). Endpoints: `/search/players`, `/player/{id}`, `/player/{id}/statistics/seasons`, `/player/{id}/unique-tournament/{tid}/season/{sid}/statistics/overall`, `/player/{id}/events/last/0`.

### Frameworks & Libraries

- `fastapi` — >=0.104.0 — framework web/ASGI.
- `uvicorn[standard]` — >=0.24.0 — servidor ASGI.
- `pydantic` — >=2.5.0 — validación/serialización.
- `requests` — >=2.31.0 — cliente HTTP (Futmondo).
- `curl_cffi` — >=0.16.0 — cliente HTTP con impersonación TLS (Sofascore, bypass fingerprinting).
- `psycopg2-binary` — >=2.9.9 — driver PostgreSQL (Neon; pool `ThreadedConnectionPool` 5–20).
- `libsql-experimental` — ==0.0.55 (pin exacto) — replica embebida Turso (branch legacy; NO compila fuera de 3.12).
- `PyJWT` — ==2.9.0 — JWT.
- `google-genai` — ==1.14.0, `groq` — ==0.25.0 — asistente (fuera del área del intent).
- **Testing**: `pytest` >=8.0.0, `pytest-cov` >=5.0.0, `httpx` >=0.27.0 (para `starlette.testclient.TestClient`).

### Test Coverage

- **Test Directories**: `backend/tests/` (~27 ficheros), specs adyacentes ausentes (árbol de tests unificado bajo `tests/`).
- **Test Frameworks**: pytest. Fixtures compartidas en `conftest.py`: `_FakeInMemoryDB`/`_FakeCursor` (SQLite `:memory:` honrando el contrato de `db_connection`, ISO-encode de datetime como el wrapper Turso), `clean_jwt_env`, `fake_db`.
- **Coverage Config**: `pytest.ini` declara cobertura como métrica informativa SIN piso bloqueante (`addopts = -ra`; activación manual `--cov=app`). Artefactos `.coverage` presentes.
- **Patrón de dobles/mocks**: characterization-first con fakes inyectados (NO red, NO DB real, NO credenciales). Cobertura relevante al intent ya existente:
  - `test_sync_degraded_steps.py` — congela que un paso no crítico que lanza queda `status="degraded"` (nunca `done`) y que NO falla la tarea (FR3.1/BR1/BR2).
  - `test_sync_step_status.py` — unidad del helper `StepStatus`/`record_degraded_step`.
  - `test_sofascore_sync_characterization.py` — regresión del reemplazo transaccional de caché (DELETE+INSERT atómico) + señalización de baneo (`should_apply_replacement`, `SofascoreIPBanError`).
  - `test_durable_task_*` (service/repository/api/characterization) — contrato de durabilidad de tareas (autoridad DB, caché best-effort, barrido interrupted-by-restart).
  - `test_prizes_characterization.py` / `test_prizes_calculator.py` — congelan `sync_prizes` (intent previo).

### Code Quality Indicators

- **Linting**: `ruff` (`backend/ruff.toml`), `target-version = py312`, `line-length = 100`, `select = [E,F,I]`. Modo ESCALONADO/advisory: **`E722` (bare-except) está en `ignore`** junto a `E501`/`E402` — es decir, el linter hoy NO señala los `except:` desnudos ("try/except amplios heredados en la capa de datos"). El gate de CI corre `ruff check .` en modo advisory (no bloquea).
- **CI/CD**: `.github/workflows/ci.yml` (PR→`main`): backend `python -m pytest tests -q --cov=app --cov-report=term-missing` BLOQUEANTE; `fly-deploy.yml` job `verify` (push→`main`): `python -m pytest tests -q` BLOQUEANTE **pero SIN `--cov`** (asimetría preexistente de cobertura backend, deuda ya registrada por el equipo). gitleaks bloqueante en ambos caminos.
- **Documentation**: docstrings ricos en los ficheros nuevos/tocados por intents recientes (`sync_step_status.py`, `task_service.py`, `sofascore_client.py`) con trazas explícitas a FR/BR; comentarios de seguridad en `main.py` (FR7/NFR1.6, montaje público de fotos). Los god-files (`data_sync_service.py`, `data_manager_v2.py`) tienen docstrings dispersos.

### Technical Debt Signals

- **Excepciones amplias (`except Exception` / bare `except:`) — conteo por fichero (app/)**: total dominado por los dos god-files. Los más relevantes al intent:
  - `data_sync_service.py` — **29** ramas `except Exception` (0 bare-except; todas capturan `Exception`, muchas hacen `logger.error(..., exc_info=True)` + `return {"status":"error", ...}`; localizadas en L42,116,198,223,233,273,355,379,407,502,531,623,685,757,784,965,1007,1068,1128,1157,1281,1314,1461,1467,1478,1506,1564,1859,1875).
  - `data_manager_v2.py` — **23** amplias, incl. **3 `except: pass`** (L57–58, L68–69, L672–673) → swallow silencioso real (skimmed; fuera del área profunda pero señal fuerte).
  - `analytics.py` (14), `db_connection.py` (9), `data_initializer_v2.py` (9), `market.py` (9), `photo_service.py` (6, incl. `except: pass` L475–476), `main.py` (6), `auth/routes.py` (6), `sync.py` (6).
  - `except: pass` (swallow desnudo) total en `app/services/`: catalogadas 4 ocurrencias reales (`photo_service.py`, `data_manager_v2.py`×3) — el resto son `except Exception` con log.
- **Señales recuperable-vs-fatal YA presentes** (buena base sobre la que construir FR3.2):
  - `sofascore_client.py`: distingue **fatal-de-repoblado** (`SofascoreIPBanError` en 403, se re-lanza y NO se traga en el `except` genérico) de **recuperable/no-encontrado** (404 → `None`, otros status → warning + `None`). Patrón `except SofascoreIPBanError: raise` antes del `except Exception` genérico.
  - `db_connection.py`: `get_connection()` hace `rollback()` + `raise` en cualquier `Exception` (fatal, no traga); el pool PostgreSQL reintenta hasta 3 veces conexiones muertas (recuperable) y recrea el pool como último recurso; `_test_connection()` re-lanza en fallo de arranque.
  - `sync_step_status.record_degraded_step`: seam explícito FR3.1 — marca `StepStatus.DEGRADED` para fallos NO críticos ya capturados (registra, NO re-lanza), consumido por `sync.py` en `prizes`/`phantoms`.
  - `task_service._cache_call`: distingue autoridad (DB, debe tener éxito → `TaskPersistenceError`) de best-effort (caché, traga y loguea warning, nunca falla la operación).
- **Cliente Futmondo — propagación de fallo**: `_make_request` traga `Timeout`/`RequestException`/`JSONDecodeError` y devuelve `None` (NO distingue recuperable de fatal; el llamador solo ve `None`). `login()` devuelve `bool`; los getters devuelven `Optional` → el fallo se propaga como ausencia de datos, no como excepción tipada. Este es el hueco central de FR4 (contratos/modos de fallo del cliente Futmondo).
- **Migraciones (`scripts/migrate_*`)**: `except Exception as e` con log (5 ramas entre ambos); NO se observó `except: pass` en estas dos concretas (el patrón "except: pass en migración/startup" del brief NO se materializa aquí — las migraciones loguean). En `main.py` el arranque usa `try/except Exception → logger.warning` (no `pass`) para init de tablas auth/durable-session/durable-task — degrada a warning en vez de abortar el boot (decisión de resiliencia, no swallow silencioso).
- **God-files**: `data_sync_service.py` = 1915 líneas; `data_manager_v2.py` ~166 KB. NO ampliar (mandato afirmado en `project.md`).
- **Puntos de escritura del camino de sync ("no corromper datos")** en `data_sync_service.py`: `UPDATE transactions` (L269, L350), `DELETE/INSERT player_favorites` (L1367/L1378/L1385), y el bloque de premios (L1816 `INSERT ... ON CONFLICT DO UPDATE` + `conn.commit()` L1825; **L1846 `DELETE FROM team_prizes ... matchday NOT IN (...)`** = borrado defensivo con su propio `try/except Exception → logger.warning` en L1859, que traga el fallo de limpieza tras un `commit()` previo → un fallo parcial puede dejar caché en estado mixto sin señal al consumidor).

## Handoff Summary

- **Intent-relevant finding**: El backend YA tiene un vocabulario recuperable-vs-fatal parcial y de buena calidad —`SofascoreIPBanError` (fatal-de-repoblado, se re-lanza), `db_connection` rollback+raise/retry de pool, `record_degraded_step` (FR3.1) y la separación autoridad-DB / caché-best-effort en `task_service`— pero está aplicado de forma desigual. El hueco más nítido para FR3.2/FR4 es `futmondo_client._make_request` (`futmondo_client.py`), que traga `Timeout`/`RequestException`/`JSONDecodeError` y devuelve `None` sin distinguir recuperable de fatal ni exponer un modo de fallo tipado; y las **29** ramas `except Exception` de `data_sync_service.py` + los **3 `except: pass`** de `data_manager_v2.py` (evidencia: conteos por fichero arriba). El punto de corromper-datos concreto es el borrado defensivo `DELETE FROM team_prizes ... NOT IN (...)` (L1846) cuyo `except` traga el fallo tras un `commit()` previo. Base fuerte para construir sin reescribir: `SofascoreClient` es el patrón de referencia a replicar para Futmondo (excepción tipada + `except <Typed>: raise` antes del genérico).
- **Risks / follow-up**:
  - `ruff.toml` tiene **`E722` en `ignore`**: el linter NO vigila los `except:` desnudos, así que cualquier objetivo de FR3.2 que quiera enforcement de bare-except necesitará re-habilitar E722 (por trinquete, aislando el reflow — regla afirmada de NO reformatear brownfield en masa).
  - Asimetría de cobertura backend: `verify` (fly-deploy.yml) corre pytest SIN `--cov` mientras `ci.yml` sí — deuda preexistente ya registrada por el equipo; cualquier piso de cobertura backend futuro debe cablearse en AMBOS caminos.
  - `data_manager_v2.py` NO se leyó en profundidad (fuera del snapshot); sus 3 `except: pass` y 23 ramas amplias deberían confirmarse en el diseño antes de tocarlas.
  - El cliente Futmondo actual señala fallo vía `None`/`bool`: introducir excepciones tipadas es un cambio de contrato con MUCHOS llamadores en el god-file de sync — hay que mapear el blast radius (los getters `get_*` devuelven `Optional` y los `sync_*` asumen `None==sin datos`).
