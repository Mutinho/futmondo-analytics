# Estructura del Código — futmondo-analytics

## Organización de Paquetes/Módulos

Monorepo con dos aplicaciones desplegables y utilidades de soporte. El catálogo con
responsabilidades y dependencias está en `component-inventory.md`; aquí se describe la
organización física y los patrones de código.

```
futmondo-analytics/
├── backend/                    # Servicio web FastAPI (Python 3.12)
│   ├── app/
│   │   ├── main.py             # App FastAPI, AuthMiddleware, montaje de routers, /photos, /health,
│   │   │                       #   arranque resiliente (init tablas → warning, no abort)
│   │   ├── api/v1/endpoints/   # Routers HTTP (market, reset_db, analytics, balances, matchdays,
│   │   │                       #   player_finances, sync, _helpers, ...)
│   │   ├── auth/               # JWT + sesión: routes.py, token_store.py, session_store.py
│   │   ├── core/               # config.py (entorno, JWT guard NFR1.1), constants.py
│   │   ├── services/           # Lógica de negocio + clientes externos (god-files, ver más abajo);
│   │   │                       #   data_sync_service.sync_prizes() = fórmula de premios;
│   │   │                       #   db_connection, sofascore_client, futmondo_client, sync_step_status,
│   │   │                       #   task_manager, task_service (área de fiabilidad, intent activo)
│   │   ├── stores/             # Repositorios de durabilidad (task_repository, session_repository)
│   │   ├── security/           # Protección de credenciales
│   │   └── models/             # Modelos de dominio/datos (DTOs Pydantic; sin modelo de premios)
│   ├── scripts/                # Scripts one-shot (sync, migraciones migrate_*_to_turso, exports) — no web
│   ├── tests/                  # pytest (~27 ficheros: test_db_admin_guard, test_jwt_startup,
│   │                           #   test_auth_characterization, test_finance_characterization,
│   │                           #   test_analytics_service, test_sync_degraded_steps,
│   │                           #   test_sync_step_status, test_sofascore_sync_characterization,
│   │                           #   test_durable_task_*, test_prizes_*; conftest fakes en memoria)
│   ├── requirements.txt, pytest.ini, ruff.toml, fly.toml, Dockerfile, nixpacks.toml, entrypoint.sh, run.py
├── angular-app/                # Frontend Angular 22 (PWA); ver detalle abajo
├── proxy/, angular-app/nginx*.conf   # Reverse proxy nginx (local y prod)
├── cron/                       # Config Fly.io del worker cron (sync; nunca emite JWT)
├── docker-compose.yml          # Orquestación local (SSL_VERIFY=0 aquí)
├── .nvmrc                      # Node 22.22.3 (SOLO en raíz; NO existe en angular-app/)
└── .github/workflows/          # ci.yml, fly-deploy.yml, daily-sync.yml, sofascore-sync.yml
```

### Área de fiabilidad del backend `backend/app/services/` (intent activo)

Ficheros del camino de sync y sus clientes, analizados en profundidad para FR3.2/FR4. El
estado de manejo de errores por fichero y su evidencia viven en `code-quality-assessment.md`.

```
backend/app/services/
├── data_sync_service.py    # ~1915 líneas (god-file); worker de sync; 29 ramas except Exception
│                           #   (L42,116,198,223,233,273,355,379,407,502,531,623,685,757,784,
│                           #    965,1007,1068,1128,1157,1281,1314,1461,1467,1478,1506,1564,1859,1875);
│                           #   puntos de escritura: UPDATE transactions (L269,L350),
│                           #   DELETE/INSERT player_favorites (L1367/L1378/L1385),
│                           #   premios: INSERT ON CONFLICT (L1816) + commit (L1825),
│                           #   DELETE ... NOT IN team_prizes (L1846) con except→warning (L1859)
├── data_manager_v2.py      # ~166 KB (god-file, SKIMMED); 23 except amplias, 3 except: pass (L57-58,L68-69,L672-673)
├── sofascore_client.py     # cliente Sofascore (curl_cffi); SofascoreIPBanError re-lanzado antes del genérico
├── futmondo_client.py      # cliente Futmondo (requests); _make_request traga a None (hueco FR4)
├── db_connection.py        # DBConnection; get_connection → rollback+raise; pool retry x3, recrea pool
├── sync_step_status.py     # StepStatus/record_degraded_step (FR3.1): marca DEGRADED, no re-lanza
├── task_manager.py         # caché best-effort de tareas (traga y loguea, nunca falla la operación)
└── task_service.py         # TaskService; _cache_call separa autoridad-DB (TaskPersistenceError) de best-effort
```

### Estructura del frontend `angular-app/`

```
angular-app/
├── src/app/
│   ├── main.ts / app.config.ts / app.routes.ts   # bootstrapApplication, providers, rutas
│   ├── core/
│   │   ├── services/*.service.ts   # 11 clientes HTTP: analytics, assistant, auth, budget,
│   │   │                           #   championship, evolution, favorites, roster, stats, sync
│   │   ├── interceptors/auth.interceptor.ts       # Bearer + refresh en cola ante 401 (+ .spec.ts)
│   │   ├── guards/auth.guard.ts                    # Protección de rutas
│   │   └── preloading/idle-preloading-strategy.ts  # Precarga por inactividad (+ .spec.ts)
│   ├── features/{market,finances,budget,calculator,analytics,evolution,statistics,...}/
│   │                                # Componentes standalone por pantalla
│   └── shared/                      # UI/utilidades reutilizables
├── angular.json                     # Builder @angular/build; architect.test.runner: vitest
├── package.json                     # name angular-app, packageManager npm@11.12.1
├── tsconfig.json / tsconfig.app.json / tsconfig.spec.json  # spec: types ["vitest/globals"]
├── eslint.config.js (flat) / .prettierrc
└── ngsw-config.json / proxy.conf.json / Dockerfile / fly.toml
```

El estado de tests/cobertura del frontend (línea base y su evolución en intents previos) se
detalla en `code-quality-assessment.md`.

### Estructura de `.github/workflows/`

```
.github/workflows/
├── ci.yml            # PR → main, job "quality": gitleaks(bloq) + pytest --cov=app(bloq)
│                     #   + ruff/pip-audit(adv) + npm ci + ng test --watch=false(bloq)
│                     #   + ng lint/npm audit(adv). Node fijado a '22'.
├── fly-deploy.yml    # push → main + workflow_dispatch. job verify (gitleaks@v2 + pytest -q
│                     #   SIN --cov + npm ci + ng test --watch=false, bloqueantes) →
│                     #   deploy-backend → deploy-frontend → smoke-test /health (5 reintentos)
├── daily-sync.yml    # cron 04:30 UTC + manual: máquina Fly one-shot; sync completo; poll
│                     #   hasta "stopped" y verifica exit code
└── sofascore-sync.yml# cron 05:00 UTC + manual: reutiliza imagen cron; corre
                      #   scripts/sync_sofascore_local.py; destrucción garantizada (trap EXIT)
```

## Clasificación de Archivos

- **Punto de entrada / composición**: `backend/app/main.py`, `run.py`/`entrypoint.sh`;
  frontend `angular-app/src/app/main.ts` + `app.config.ts`.
- **Configuración**: `backend/app/core/config.py`, `constants.py`, `.env.example`,
  `fly.toml`, `docker-compose.yml`, `.nvmrc`; frontend `angular.json`, `tsconfig*.json`,
  `eslint.config.js`, `.prettierrc`, `ngsw-config.json`, `proxy.conf.json`.
- **Superficie HTTP (backend)**: `backend/app/api/v1/endpoints/*` (incl.
  `player_finances.py`, `balances.py`, `matchdays.py`, `analytics.py`, `sync.py`),
  `backend/app/auth/routes.py`.
- **Cliente HTTP (frontend)**: `angular-app/src/app/core/services/*.service.ts` +
  `core/interceptors/auth.interceptor.ts`.
- **Camino de sync y clientes externos (área de fiabilidad, intent activo)**:
  `services/data_sync_service.py` (worker + fórmula de premios), `services/db_connection.py`
  (conexión/pool), `services/sofascore_client.py`, `services/futmondo_client.py`
  (clientes externos), `services/sync_step_status.py` (helper de degradación),
  `services/task_manager.py` / `services/task_service.py` (durabilidad de tareas).
- **Lógica de premios (fórmula)**: `backend/app/services/data_sync_service.py::sync_prizes`
  (~líneas 1577-1885) — productor de la tabla `team_prizes`.
- **Persistencia**: `backend/app/stores/*` (capa nueva estrecha) y SQL crudo en
  `auth/token_store.py`, `_helpers.py`, `balances.py`, `analytics.py`,
  `routes._auto_detect_championships`.
- **Integración externa**: `services/futmondo_client.py`, `sofascore_client.py`,
  `photo_service.py`.
- **Scripts one-shot**: `backend/scripts/migrate_to_turso.py`,
  `backend/scripts/migrate_data_to_turso.py`, `sync_sofascore_local.py`, `sync_data.py`,
  `fetch_user_finances_data.py` — utilidades, NO parte del servicio web.
- **Tests**: `backend/tests/*.py` (~27), `angular-app/**/*.spec.ts`.
- **Entrega/CI**: `.github/workflows/*.yml`.
- **Datos estáticos (no código)**: `backend/static/photos/players/**` (~800 PNG).

## Patrones de Código Observados

### Backend

- **Middleware de autenticación global** con lista de exclusión (`AUTH_EXCLUDED_PATHS`) en
  vez de dependencias por endpoint; ver `api-documentation.md`.
- **Proxy a APIs externas** desde `services/`, con cliente por usuario resuelto en
  `_helpers.get_user_futmondo_client`.
- **Señalización recuperable-vs-fatal (patrón de referencia y su hueco)**: `sofascore_client`
  define `SofascoreIPBanError` y hace `except SofascoreIPBanError: raise` ANTES del
  `except Exception` genérico (fatal se propaga tipado; recuperable → `None`). Es el patrón
  que FR4 debe replicar en `futmondo_client._make_request`, que hoy NO lo sigue (traga
  `Timeout`/`RequestException`/`JSONDecodeError` a `None`). Detalle en
  `code-quality-assessment.md`.
- **Rollback+raise en la capa de conexión**: `db_connection.get_connection()` hace
  `rollback()` + `raise` ante cualquier `Exception` (fatal, no traga); el
  `ThreadedConnectionPool` (5-20) reintenta 3 veces conexiones muertas y recrea el pool.
- **Degradación de pasos no críticos**: `sync_step_status.record_degraded_step` marca
  `StepStatus.DEGRADED` (registra, NO re-lanza), consumido por `sync.py` en `prizes`/
  `phantoms` para que un fallo no crítico NO tumbe la tarea (FR3.1).
- **Autoridad-DB vs. caché best-effort**: `task_service._cache_call` distingue la operación
  que debe tener éxito (DB → `TaskPersistenceError`) de la best-effort (`task_manager`, caché
  que traga y loguea sin fallar).
- **Excepciones amplias heredadas**: los god-files concentran ramas `except Exception`
  (29 en `data_sync_service.py`) y `except: pass` desnudos (3 en `data_manager_v2.py`); el
  linter NO los vigila hoy (`E722` en `ignore`). Anti-patrón a acotar sin ampliar el
  god-file. Detalle y conteos en `code-quality-assessment.md`.
- **Reemplazo transaccional atómico** (DELETE+INSERT en la misma transacción) en el caché de
  Sofascore, frente a la secuencia commit-luego-`DELETE` del bloque de premios (punto de
  corromper-datos). Ver `architecture.md`.
- **Precálculo batch + lectura barata**: la fórmula de premios se ejecuta una vez en
  `sync_prizes` y persiste en `team_prizes`; los endpoints sólo hacen `SELECT`/suma. UPSERT
  con `ON CONFLICT (championship_id, team_id, matchday)` y limpieza defensiva
  `DELETE ... WHERE matchday NOT IN (...)`.
- **Matchday sintético negativo** para las pseudo-jornadas adelantadas de Futmondo.
- **Persistencia mixta**: capa `stores/` estrecha (patrón recomendado) conviviendo con SQL
  crudo disperso (anti-patrón a no ampliar; detalle en `code-quality-assessment.md`).
- **God-files en `services/`**: `data_manager_v2.py` (~166 KB), `data_sync_service.py`
  (~84 KB / 1915 líneas, aloja la fórmula de premios y el worker de sync),
  `assistant_service.py` (~51 KB); no deben crecer.
- **Imports dinámicos dentro de funciones**; preferir import estático. **Idioma en el
  código**: identificadores/docstrings/comentarios en inglés; texto de usuario
  (`HTTPException.detail`) en castellano. Docstrings ricos con trazas a FR/BR en los ficheros
  nuevos/tocados (`sync_step_status.py`, `task_service.py`, `sofascore_client.py`).

### Frontend (Angular 22)

- **Componentes standalone + signals**: sin `NgModule` de app; arranque por
  `bootstrapApplication` y providers en `app.config.ts`; rutas lazy con precarga por
  inactividad (`idle-preloading-strategy`).
- **Interceptor de auth transversal**: `auth.interceptor` añade Bearer, excluye `/auth/*`
  (usa `withCredentials`), encola peticiones y refresca ante 401, fuerza logout ante
  403/refresh fallido. Es el patrón de referencia de spec Vitest ya existente.
- **Servicios por dominio** en `core/services/*.service.ts` (un servicio por área de la API).
- **Tests con Vitest**: los specs importan de `vitest` (`vi`, `describe`, `it`, `expect`) y
  usan `@angular/core/testing` + `@angular/common/http/testing`; `tsconfig.spec.json` incluye
  `types: ["vitest/globals"]`.

### Entrega / CI

- **Doble gate bloqueante** (`ci.yml` PR + `verify` en `fly-deploy.yml`) con `gitleaks`,
  `pytest` y `ng test` bloqueantes; `ruff`/ESLint/`pip-audit`/`npm audit` advisory
  (`continue-on-error`). Asimetría preexistente: `verify` corre `pytest -q` SIN `--cov`.
- **Crons de coste ~0**: máquinas Fly one-shot que se crean, ejecutan y destruyen
  (`trap cleanup EXIT` en `sofascore-sync.yml`).
