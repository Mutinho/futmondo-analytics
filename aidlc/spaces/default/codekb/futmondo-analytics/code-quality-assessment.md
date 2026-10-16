# Code Quality Assessment — futmondo-analytics

## Cobertura de tests

- **Backend**: `backend/tests/` con **62** ficheros `test_*.py`, muchos de
  characterization (`test_sync_*`, `test_data_manager_*`, `test_prizes_*`,
  `test_assistant_*`, `test_durable_*`, `test_auth_*`, `test_jwt_startup.py`).
  Ejecutados DESDE `backend/` (`pythonpath = .`), con fixtures fake in-memory en
  `conftest.py` (sin red, sin BD real, sin credenciales reales).
- **Frontend**: **15** ficheros `*.spec.ts` colocados junto a sus fuentes en
  `src/app/core/**` y `src/app/features/**`.
- **Config de cobertura — PRESENTE y BLOQUEANTE en ambos**:
  - Backend: `pytest.ini` `addopts = -ra --cov-fail-under=27` (line-only;
    requiere `--cov=app`, que pasan `ci.yml` y el job `verify`). Piso real medido
    **27.52% → 27**; el ratchet sólo sube.
  - Frontend: `angular.json` target `test` `coverageThresholds` statements 19 /
    branches 19 / functions 17 / lines 18 (fuente única de umbral; enforcement
    dentro de `ng test`).

## Linting

- **Backend `ruff`** (`backend/ruff.toml`): `target-version = py312`,
  `line-length = 100`, `select = ["E","F","I"]`, `ignore = ["E501","E402"]`.
  `[lint.per-file-ignores]` registra verbatim la deuda de los god-files y los
  adapters DDD extraídos (p. ej. `data_manager_v2.py` → `E722,F841,F401,I001`).
  `ruff check` es **BLOQUEANTE** en ambos gates; `ruff format` **NUNCA** se corre
  en masa (regla afirmada). `E722`/bare-except re-habilitado como advisory en
  intents previos.
- **Frontend ESLint** flat config (`eslint.config.js`) presente, pero sus
  devDependencies **NO instaladas** → `ci.yml` corre `npx ng lint || echo …` en
  modo **advisory** (deuda diferida).

## CI/CD

- **`ci.yml`** (gate de PR, job `quality`): gitleaks + ruff + pytest+cov +
  pip-audit + ng test + npm audit.
- **`fly-deploy.yml`** (push a `main`): job `verify` replica el gate →
  `deploy-backend` → `deploy-frontend` → `smoke-test` (`/health`). Cadena `needs:`
  intacta.
- **Crons**: `daily-sync.yml` y `sofascore-sync.yml` lanzan máquinas Fly
  one-shot. gitleaks unificado a `@v3` en ambos gates. Secretos vía GitHub
  Actions / Fly.io; `JWT_SECRET` efímero no-productivo en CI.

## Documentación

- `README.md` raíz exhaustivo (arquitectura, stack, endpoints, auth, PWA).
- `docs/` extenso: DEPLOY, ROLLBACK, PR-GATE, PROJECT_CONTEXT, varios BACKLOG,
  V2_MIGRATION_PLAN, FRONTEND_IMPROVEMENTS_PLAN, SDD_ANGULAR_MIGRATION,
  MOCKUPS_NAVIGATION.
- Docstrings backend ricos (clasificación de errores FR3.2, notas de seguridad).
  Comentarios mezclados castellano + inglés.

## Deuda técnica (tamaños MEDIDOS en este scan)

> IMPORTANTE: estas cifras son las MEDIDAS por el scan de este run y
> **sustituyen** a las de `project.md`, que están desactualizadas tras las
> descomposiciones DDD de intents 261005/261003.

- **God-files backend** (tamaño real en disco):
  - `app/services/analytics/application/calculations.py` — **872 líneas /
    36.028 bytes** (el mayor por tamaño; lógica de cálculo analytics).
  - `app/services/futmondo_client.py` — **720 líneas / 27.267 bytes**.
  - `app/services/data_manager_v2.py` — **685 líneas / 33.368 bytes** (YA
    descompuesto parcialmente a `data_manager/<resp>/{domain,application,
    infrastructure}`; la facade mantiene nombres/firmas byte-for-byte). **La
    memoria del proyecto lo cita como «~166 KB»; el valor ACTUAL en disco es
    33 KB.**
  - `app/api/v1/endpoints/market.py` — **580 líneas / 24.560 bytes**
    (SQL-en-router).
  - `app/services/photo_service.py` — **492 líneas / 22.764 bytes** (`E722`
    registrado como deuda).
  - `app/services/sofascore_client.py` — **392 líneas**.
  - `app/api/v1/endpoints/sync.py` — **407 líneas / 16.864 bytes**.
  - `app/services/data_sync_service.py` — **362 líneas / 15.397 bytes**.
  - `assistant_service.py` — hoy sólo **60 líneas / 2.290 bytes** (shim; la lógica
    real está en el paquete DDD `assistant/`). **La memoria lo cita «~51 KB» —
    desactualizado.**
- **SQL-en-router**: **17** ficheros de `api/v1/endpoints/` ejecutan SQL directo
  (`.execute(`) — acopla persistencia↔HTTP; patrón heredado que las reglas
  afirmadas prohíben ampliar.
- **Dead-ish code multi-engine**: `db_connection.adapt_params()` reescribe
  placeholders `? → %s` en runtime; `DATABASE_PATH` y ramas `db_type != postgres`
  son herencia del soporte SQLite/Turso retirado (tolerado).
- **Manejo de errores**: endurecido recientemente (clasificación
  RECOVERABLE/FATAL en `main.py`, `db_connection.py`, `token_store.py`); los
  `except:` amplios de los god-files quedan como deuda registrada.

## Portabilidad a nativo — riesgos (preservados del scan; relevantes al intent)

1. **Acoplamiento web-DOM alto en la UI**: `features/*` usa Angular **Material +
   CDK** (DOM) y plantillas `.html`; NativeScript no soporta Material ni DOM →
   **toda la capa de vista se reescribe** con `@nativescript/angular`. Los
   **servicios** (`core/services/*`, RxJS/`HttpClient`, signals) y **modelos**
   (`core/models/*`) son portables casi 1:1; los **componentes** no.
2. **PWA / service worker / `localStorage`**: `ngsw-config.json` +
   `provideServiceWorker` + **17** usos de `localStorage` (sesión, tema,
   reconexión de sync) → en nativo se sustituyen por `@nativescript/core`
   ApplicationSettings / SecureStorage. El **access en memoria + refresh en cookie
   HttpOnly** depende de cookies del navegador y `withCredentials` → el modelo de
   sesión cookie-based **NO existe igual en nativo** y es el **riesgo de
   portabilidad #1** (habrá que mover el refresh a almacenamiento seguro nativo).
3. **Chart.js / ng2-charts** (Evolución, Analytics): dependen de `<canvas>` DOM →
   requieren un plugin de charting nativo distinto (reescritura de gráficos).
4. **Discrepancia tamaños god-file vs memoria** (ver arriba): usar las cifras
   MEDIDAS, no las de `project.md`. Sigue siendo backend fuera del alcance de un
   intent de viabilidad de UI nativa.
5. **Coste 0 € y stack Fly.io/Neon**: la viabilidad debe respetar que
   backend/deploy no cambian; NativeScript es OSS, pero distribuir a iPhone 13
   Pro / Samsung A17 implica build nativo (Xcode / Android SDK) y potencialmente
   coste de cuenta de desarrollador Apple — a señalar en feasibility, no resuelto
   aquí.

## Hallazgo de UI relevante al intent

La navegación actual es un **`mat-sidenav` lateral** (no una barra inferior):
`app.html` define `<mat-sidenav>` con `<mat-nav-list>` de **12 items** + acciones
Sincronizar/Modo oscuro/Cerrar sesión; en móvil se abre con `MatToolbar` + botón
`menu` (`isMobile()` vía `BreakpointObserver`). **No existe** hoy ningún
bottom-nav ni concepto de «4 opciones más usadas» → el menú inferior iOS 'liquid
glass' con 4 opciones del intent es **construcción NUEVA** de UI nativa. **No hay
ninguna superficie de widget** (iOS/Android) en el código (0 referencias) → es
greenfield nativo.
