# Estructura del Código — Futmondo Analytics

> Reverse-engineering (escaneo FULL). Organización de paquetes/módulos,
> clasificación de ficheros y patrones de código observados.

## Organización de paquetes/módulos

Repo único (workspace root) con cinco áreas de nivel superior:

```
futmondo-analytics/
├── angular-app/          # Frontend Angular 22 (PWA)
├── backend/              # Backend FastAPI (Python 3.12)
├── proxy/                # nginx reverse proxy (solo local)
├── cron/                 # App Fly.io futmondo-cron (reutiliza imagen backend)
└── docs/                 # Documentación de contexto y planes
```

### Backend (por capas)

```
backend/app/
├── main.py               # Bootstrap FastAPI, CORS, AuthMiddleware, 23 routers
├── core/                 # config.py, constants.py (config y constantes)
├── auth/                 # routes.py, jwt_utils.py, token_store.py,
│                         #   session_store.py, dependencies.py, models.py
├── services/             # capa de datos y lógica (ver "god files")
│   ├── db_connection.py        # abstracción BD (PostgreSQL/SQLite/Turso)
│   ├── futmondo_client.py      # cliente API Futmondo (requests)
│   ├── sofascore_client.py     # cliente API Sofascore (curl_cffi)
│   ├── task_manager.py         # estado in-memory de tareas de sync
│   ├── data_manager_v2.py      # 166 KB — acceso a datos (god file)
│   ├── data_sync_service.py    # 84 KB — orquestación de sync (god file)
│   ├── assistant_service.py    # 51 KB — asistente IA (god file)
│   ├── analytics_service.py    # 34 KB — analítica (god file)
│   └── photo_service.py        # 23 KB — gestión de fotos de jugadores
├── api/v1/endpoints/     # 23 routers por dominio (sync, market, analytics, …)
├── models/               # modelos de dominio
├── scripts/              # jobs one-shot y migraciones heredadas
└── tests/                # 6 ficheros de caracterización (pytest)
```

### Frontend (por feature)

```
angular-app/src/app/
├── core/                 # services/, interceptors/, guards/ (transversal)
├── shared/               # componentes/utilidades compartidas
└── features/             # 17 features standalone (Angular 22)
```

## Clasificación de ficheros

| Categoría | Ubicación | Ejemplos |
|-----------|-----------|----------|
| Bootstrap/entrypoint | `backend/app/main.py`, `backend/run.py`, `backend/entrypoint.sh` | montaje de routers, arranque uvicorn |
| Configuración runtime | `backend/app/core/` | `config.py`, `constants.py` |
| Auth | `backend/app/auth/` | JWT, token store, session store, middleware |
| Endpoints/API | `backend/app/api/v1/endpoints/` | 23 routers por dominio |
| Servicios/lógica | `backend/app/services/` | sync, analytics, clientes externos, asistente |
| Scripts/jobs | `backend/scripts/` | `sync_data.py` (cron), migraciones a Turso, exportadores |
| Tests | `backend/tests/`, `angular-app/**/*.spec.ts` | 6 ficheros pytest; 1 solo `.spec.ts` frontend |
| Build/deploy | raíz y por app | `Dockerfile`, `fly.toml`, `docker-compose.yml`, workflows |
| Frontend features | `angular-app/src/app/features/` | 17 features standalone |
| Frontend core | `angular-app/src/app/core/` | `auth.interceptor.ts`, `auth.service.ts`, guards |

## Patrones de código

- **Router-per-domain (FastAPI)**: cada dominio tiene su router en
  `api/v1/endpoints/` montado en `main.py` con su prefijo. Un dominio
  (`matchdays`) se monta doblemente (`/api/v1/matchdays` y `/v1/matchdays`) para
  evitar redirect loops — superficie duplicada.
- **Middleware de autenticación central**: `AuthMiddleware` en `main.py` valida
  Bearer para todo `/api/v1/*` salvo `AUTH_EXCLUDED_PATHS`, y adjunta
  `request.state.user`.
- **Abstracción de BD con adaptación de parámetros**: patrón
  `sql = db.adapt_params(sql)` + `cursor.execute(...)` para soportar múltiples
  backends con placeholders homogéneos (`?`).
- **Sync desacoplada por hilo + polling**: `threading.Thread(daemon=True)` sobre
  `_run_sync_in_background`, progreso vía `TaskManager` (patrón task-id +
  polling).
- **Standalone components + signals (Angular 22)**: features standalone; core con
  interceptor de auth y guards. `angular.json` configura `skipTests: true` en los
  schematics.
- **Anti-patrones observados**: `except Exception: pass` silencioso en arranque y
  migraciones; "god files" que superan con creces el objetivo de <300 líneas;
  estado no durable en memoria; ramas muertas de configuración multi-backend.

## Convenciones

- Comentarios en castellano con referencias a NFRs/FRs (endurecimiento previo).
- Formato: Prettier (frontend) + ruff format (backend). Lint: ruff (backend,
  advisory en CI) y ESLint (frontend, advisory en CI).
