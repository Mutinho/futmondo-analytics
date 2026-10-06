# Code Structure — futmondo-analytics

## Package / Module Organization

```
futmondo-analytics/
├── angular-app/          # Frontend Angular 22 + Material (PWA)
├── backend/              # Backend FastAPI (Python 3.12)
├── proxy/                # Nginx reverse proxy (local)
├── cron/                 # Fly one-shot machines (daily-sync, sofascore-sync)
├── docs/                 # Documentación (DEPLOY, ROLLBACK, PR-GATE, ...)
├── docker-compose.yml    # Orquestación local
└── .github/workflows/    # ci.yml, fly-deploy.yml, daily-sync.yml, sofascore-sync.yml
```

### angular-app/
- `src/app/app.routes.ts` — rutas lazy con `authGuard`.
- `src/app/features/calculator/` — pantalla `/calculator` (`calculator.component.ts`
  + `.html`): planificador de ventas/proyección de balance (foco del intent).
- `src/app/features/**` — resto de pantallas: `budget`, `market`, `stats`,
  `evolution`, `analytics` (sub-tabs), `finances`, etc.
- `src/app/core/services/**` — servicios HTTP (incl. `rosterService`).
- `src/app/core/interceptors/**`, `core/guards/**` — interceptor de auth, `authGuard`.
- `src/app/shared/**` — componentes/utilidades compartidas.
- Config: `package.json`, `angular.json`, `tsconfig*.json`, `eslint.config.js`,
  `.prettierrc`, `ngsw-config.json`.

### backend/
- `app/main.py` — app FastAPI, montaje de routers `/api/v1/*` y `/auth/*`,
  `AuthMiddleware`, mount público `/static/photos/*`.
- `app/core/config.py` — configuración; fail-fast si falta/por defecto `JWT_SECRET`.
- `app/api/v1/endpoints/` — routers por recurso (`player_finances.py`, `roster.py`,
  `market`, `analytics`, `balances`, `sync`, `transactions`, `user`, `assistant`, ...).
- `app/services/prizes/` — `calculator.py` (función pura), `team_prizes_writer.py`
  (reemplazo transaccional atómico).
- `app/services/data_manager/**` — 12 submódulos DDD extraídos del god-file,
  estructura uniforme `{application,infrastructure,domain}`.
- `app/services/sync/**` — 11 orquestadores de sync con la misma forma DDD.
- `app/services/analytics/**`, `app/services/assistant/**` — fachadas + puertos +
  adaptadores.
- `app/services/data_sync_service.py`, `app/services/data_manager_v2.py` —
  god-files en descomposición (ver `code-quality-assessment.md`).
- `app/auth/**`, `app/stores/**`, `app/security/**` — auth, almacenes, cifrado.
- `tests/` — ~55 archivos, mayoría `*_characterization.py`.
- Config: `requirements.txt`, `pytest.ini`, `ruff.toml`, `conftest.py`, `Dockerfile`,
  `run.py`.

### proxy/ y cron/
- `proxy/` + `angular-app/nginx*.conf` — reverse proxy local y prod.
- `cron/` — máquinas Fly one-shot para sync programado.

## File Classification

- **Entrypoints**: `backend/app/main.py` (+ `run.py`), `angular-app/src/main.ts`.
- **Routers / API surface**: `backend/app/api/v1/endpoints/**`, `app/auth/**`.
- **Dominio puro / sin I/O**: `prizes/calculator.py` (reglas BR1.1-BR3.2).
- **Persistencia / adaptadores**: `prizes/team_prizes_writer.py`,
  `data_manager/**/infrastructure`, `stores/**`.
- **Deuda registrada**: `data_manager_v2.py`, `data_sync_service.py`,
  `assistant_service.py`, SQL inline en `player_finances.py` y `main.py`.
- **Tests**: `backend/tests/**` (fakes in-memory), `angular-app/**/*.spec.ts`.

## Code Patterns

- **DDD por responsabilidad** en backend: `application` (casos de uso) / `domain`
  (puertos, reglas) / `infrastructure` (adaptadores). Inversión de dependencias vía
  puertos (`analytics/domain/ports.py`, `assistant/domain/ports.py`).
- **Función pura + escritor transaccional** para el dinero de premio (patrón de
  referencia para lógica nueva testeable).
- **Angular signals + `computed()` + `OnPush`**, componentes standalone, rutas lazy.
- **Idioma**: identificadores/docstrings/comentarios en inglés; texto de usuario y
  mensajes de commit en castellano (regla afirmada).

## Sources

- `developer-scan.md`: Scan Coverage, Packages Found, Technical Debt Signals.
- `README.md`: árbol de carpetas y stack.
- Inventario de componentes y responsabilidades en `component-inventory.md`.
