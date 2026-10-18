# Code Structure — Futmondo Analytics

Monorepo con dos aplicaciones (`backend/` FastAPI, `angular-app/` Angular) más
`proxy/`, `cron/`, `docs/`, `scripts/` y orquestación local (`docker-compose.yml`).

## backend/ (FastAPI, Python 3.12)

```
backend/
├── app/
│   ├── main.py                 # Entrypoint FastAPI: CORS, AuthMiddleware, routers, static photos, /health
│   ├── auth/                   # Autenticación (clave para F1)
│   │   ├── routes.py           # /auth/login, /auth/refresh, /auth/logout + auto-detección de campeonatos
│   │   ├── jwt_utils.py        # create/verify access & refresh tokens (PyJWT, HS256), hash_token
│   │   ├── dependencies.py     # get_current_user (Bearer -> payload)
│   │   ├── token_store.py      # Tablas auth (app_users, refresh_tokens, user_championships) + revocación
│   │   ├── session_store.py    # Caché en memoria de FutmondoClient por usuario (TTL 12h, sin password)
│   │   └── models.py           # LoginRequest / TokenResponse / Refresh* (pydantic)
│   ├── api/v1/endpoints/       # Routers REST (ver api-documentation.md)
│   │   ├── user.py             # /api/v1/user/me, /championships
│   │   ├── market.py, roster.py, sync.py, analytics.py, balances.py,
│   │   │   player_finances.py, transactions.py, favorites.py,
│   │   │   clausulable_players.py, statistics.py, user_stats.py,
│   │   │   championships.py, phantoms.py, matchdays.py, initialize.py,
│   │   │   reset_db.py, sofascore_sync.py, sofascore_detail.py, assistant.py
│   │   └── _helpers.py, _sofascore_helpers.py
│   ├── services/               # Lógica de negocio e integraciones
│   │   ├── futmondo_client.py  # Cliente API Futmondo (login, _make_request, errores tipados)
│   │   ├── sofascore_client.py # Cliente API Sofascore
│   │   ├── integration_errors.py  # Jerarquía de errores de integración tipados (FR4)
│   │   ├── session_service.py / session_repository (stores/) # Sesión durable + rehidratación
│   │   ├── task_service.py / task_repository (stores/)       # Tareas de sync durables
│   │   ├── sync/, prizes/, analytics/, assistant/            # Paquetes de dominio
│   │   ├── data_manager/        # Paquete DDD extraído del god-file (adapters de infraestructura)
│   │   ├── data_manager_v2.py   # God-file heredado (DEUDA CONOCIDA, NO ampliar) — ver abajo
│   │   ├── data_sync_service.py # God-file heredado (DEUDA CONOCIDA, NO ampliar) — ver abajo
│   │   ├── photo_service.py, futmondo_service.py, db_connection.py, sync_step_status.py
│   │   └── data_initializer*.py
│   ├── stores/                 # Repositorios de persistencia (session_repository, task_repository)
│   ├── security/               # credential_protection.py (cifrado del handle de re-auth)
│   ├── core/                   # config.py (env + JWT_SECRET), constants.py
│   └── models/                 # models.py (modelos de dominio)
├── tests/                      # Suite pytest (characterization-first) — ver code-quality-assessment.md
├── conftest.py                 # Fixtures fake in-memory (SQLite), sin red ni DB real
├── requirements.txt, pytest.ini, ruff.toml, .pip-audit-allowlist
├── Dockerfile, fly.toml, run.py
└── scripts/                    # Scripts de sync/exportación (fuera del servicio web)
```

### God-files heredados (deuda conocida — NO ampliar)

Regla afirmada en `project.md`/`team.md`: NUNCA ampliar ni reescribir los
god-files; el código nuevo va tras una capa/función estrecha testeable.

- `app/services/data_manager_v2.py` — tamaño observado en disco **~33 KB (1253
  líneas aprox. no verificadas)**; registrado en `ruff.toml` `per-file-ignores`
  con `E722`/`F841`/`F401`/`I001`. Parte de su lógica se ha extraído a
  `app/services/data_manager/.../infrastructure/*_adapter.py` (deuda verbatim).
- `app/services/data_sync_service.py` — tamaño observado **~15 KB**; también en
  `per-file-ignores`.

> Nota de alcance: las referencias históricas en `memory/` citan tamaños mayores
> (`data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB). Los tamaños que
> este escaneo observó en disco son los indicados arriba; la discrepancia es
> coherente con la descomposición DDD parcial ya realizada (`data_manager/`).
> Mantener la regla de NO ampliar en cualquier caso.

## angular-app/ (Angular 22 + Material 22, PWA)

```
angular-app/
├── src/
│   ├── main.ts, index.html, styles.scss
│   └── app/
│       ├── app.config.ts        # provideHttpClient(withInterceptors([authInterceptor])), router, service worker
│       ├── app.routes.ts, app.ts
│       ├── core/
│       │   ├── services/
│       │   │   ├── auth.service.ts        # Login/refresh/logout; access token EN MEMORIA (ref. F1)
│       │   │   ├── analytics|budget|stats|market|roster|sync|... .service.ts
│       │   ├── interceptors/auth.interceptor.ts  # Añade Bearer + withCredentials; refresh en 401; logout en 403
│       │   ├── guards/auth.guard.ts       # CanActivate: recupera sesión / redirige a /login
│       │   ├── preloading/, models/
│       ├── features/
│       │   ├── login/login.component.ts   # Formulario de login (ref. F1)
│       │   ├── splash/, budget/, market/, finances/, calculator/,
│       │   │   transactions/, my-roster/, favorites/, clausulable/,
│       │   │   classification/, evolution/, stats/, settings/, analytics/
│       └── shared/              # components/, utils/, pipes/, styles/
├── angular.json                 # builder @angular/build:*, target test con Vitest + coverageThresholds
├── package.json                 # Angular 22, Material 22, Vitest 4.1.11
├── eslint.config.js (advisory), .prettierrc, nginx.prod.conf, Dockerfile, fly.toml
└── ngsw-config.json, public/     # PWA (service worker + manifest + iconos)
```

## Áreas de interés para F1 (login nativo iOS)

- **Backend auth** (`app/auth/`): routes + jwt_utils + token_store son el
  contrato a reutilizar/extender (D-01).
- **Frontend auth como referencia de comportamiento**: `auth.service.ts`
  (access en memoria, refresh por cookie, `tryRecoverSession`),
  `auth.interceptor.ts` (reintento en 401) y `login.component.ts` modelan el flujo
  que el cliente nativo iOS debe replicar con su propio almacén (Keychain) en vez
  de cookie de navegador.

## Sources

- Listados de directorios de `backend/` y `angular-app/` (herramienta de lectura)
- `backend/app/main.py`, `backend/app/auth/*.py`, `backend/ruff.toml`
- `angular-app/src/app/app.config.ts`, `angular-app/angular.json`
- `backend/app/services/integration_errors.py`

## Assumptions & Open Questions

- No se abrieron todos los `*_adapter.py` del paquete `data_manager/`; su
  clasificación como "deuda verbatim extraída del god-file" se toma del comentario
  verificado en `ruff.toml`. El conteo exacto de líneas de los god-files no se
  verificó con `wc` sobre cada fichero más allá del tamaño en bytes.
