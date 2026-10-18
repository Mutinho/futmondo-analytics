# Reverse Engineering Timestamp

## Run Record

- Date: 2026-10-17T09:12:15Z
- Commit: 7cf4e131bf5711444a307ec85120b4258f1e2ac3

## Alcance del escaneo

Escaneo **parcial** enfocado en la etapa reverse-engineering del intent
`261016-f1-login-nativo` (F1: login nativo iOS). Prioridad: backend de
autenticación, API protegida, cliente Angular de referencia y configuración de
calidad/CI, por ser lo relevante para reutilizar el backend desde un cliente
nativo iOS (D-01).

### Analizado en profundidad (leído y entendido)

- `backend/app/main.py` (AuthMiddleware, routers, `/health`, fotos).
- `backend/app/auth/`: `routes.py`, `jwt_utils.py`, `dependencies.py`,
  `token_store.py`, `session_store.py`, `models.py`.
- `backend/app/core/config.py`, `backend/app/services/integration_errors.py`,
  cabecera de `backend/app/services/futmondo_client.py`.
- `backend/app/api/v1/endpoints/user.py` (`/me`, `/championships`).
- `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`,
  `backend/.pip-audit-allowlist`.
- `angular-app/package.json`, `angular-app/angular.json`,
  `angular-app/src/app/app.config.ts`.
- `angular-app/src/app/core/services/auth.service.ts`,
  `angular-app/src/app/core/interceptors/auth.interceptor.ts`,
  `angular-app/src/app/core/guards/auth.guard.ts`,
  `angular-app/src/app/features/login/login.component.ts`.
- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`.
- `README.md`.

### Solo ojeado (sin lectura profunda)

- Resto de `backend/app/api/v1/endpoints/` (nombres, prefijos y tamaños desde el
  listado y `main.py`).
- Resto de `backend/app/services/` (nombres/tamaños; god-files identificados pero
  no leídos íntegramente).
- `backend/tests/` y `angular-app/src/app/**/*.spec.ts` (inventario por nombre).
- Resto de `angular-app/src/app/features/` y `shared/`.

### Dejado fuera (no abierto)

- `angular-app/node_modules.old-1789382239/`, `angular-app/node_modules/`,
  cachés (`.angular/`, `.ruff_cache/`, `.pytest_cache/`, `__pycache__/`),
  `coverage/`, artefactos de build.
- `spikes/`, `stitch_*`, `cron/`, `proxy/` salvo referencias puntuales.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 261016-f1-login-nativo
fingerprint: unknown
analyzed:
  paths:
    - backend/app/main.py
    - backend/app/auth/
    - backend/app/core/config.py
    - backend/app/services/integration_errors.py
    - backend/app/api/v1/endpoints/user.py
    - backend/requirements.txt
    - backend/pytest.ini
    - backend/ruff.toml
    - angular-app/package.json
    - angular-app/angular.json
    - angular-app/src/app/app.config.ts
    - angular-app/src/app/core/services/auth.service.ts
    - angular-app/src/app/core/interceptors/auth.interceptor.ts
    - angular-app/src/app/core/guards/auth.guard.ts
    - angular-app/src/app/features/login/login.component.ts
    - .github/workflows/ci.yml
    - .github/workflows/fly-deploy.yml
    - README.md
  components:
    - FastAPI app + AuthMiddleware
    - Auth routes
    - JWT utils
    - Auth dependency
    - Token store
    - Session store (memoria)
    - Auth models
    - Session service / repo
    - Credential protection
    - Futmondo client
    - Sofascore client
    - Integration errors
    - Task service / repo
    - Sync service
    - Data manager
    - Photo service
    - Config
    - DB connection
    - AuthService
    - authInterceptor
    - authGuard
    - LoginComponent
    - App config
    - Feature services
    - Feature components
shallow:
  paths:
    - backend/app/api/v1/endpoints/
    - backend/app/services/
    - backend/tests/
    - angular-app/src/app/features/
    - angular-app/src/app/shared/
```

## Sources

- Herramientas de lectura/listado sobre el repo `/home/javi/futmondo-analytics`.
- `aidlc engine now` (timestamp) y `git rev-parse HEAD` (commit).

## Assumptions & Open Questions

- `fingerprint: unknown`: no se ejecutó `codekb-scope-diff --mint` en este
  escaneo; el bloque se completa honestamente con `unknown` según la guía (el
  comando lo imprime así cuando no es computable).
- `kind: partial` y por tanto `analyzed.paths` NO incluye `./` (no fue un
  escaneo completo del repo).
