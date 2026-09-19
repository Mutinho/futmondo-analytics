# Evaluación de Calidad del Código — futmondo-analytics

## Cobertura de Tests, Linting y CI/CD

### Tests — Backend

- `pytest` + `pytest-cov`, ejecutado desde `backend/` (`pytest.ini`: `testpaths=tests`,
  `pythonpath=.`). **Sin piso de cobertura bloqueante** — no existe
  `cov-fail-under`/`fail_under`/`coverageThreshold` (ratcheting diferido, decisión de equipo).
- **Cobertura existente relevante al área de premios/finanzas**:
  - `test_finance_characterization.py` — **caracteriza el CONSUMO**:
    `player_finances.get_player_finances` (fórmula agregada, orden desc, lectura de
    `team_prizes`, budget por defecto 200M, 500 en error) con doble de `DataManagerV2` +
    `get_db` falso.
  - `test_analytics_service.py` — caracteriza `AnalyticsService` (trends, form, value-trend,
    clause-network, streaks, projections) con `StubDM`.
  - **GAP (área de premios)**: NO existe test que caracterice la **PRODUCCIÓN** del premio
    (`data_sync_service.sync_prizes()`): ratios de ranking flop/top, gating por ronda completa
    (`round_fully_played`), MVP, dream-team, pseudo-jornada negativa y la limpieza defensiva
    `DELETE ... NOT IN`. `balances` y `matchdays` tampoco tienen tests directos.
- **Cobertura existente relevante a intents de seguridad**:
  - **FR18**: `test_db_admin_guard.py` — 404 por defecto, 404 con valor no-afirmativo, 200
    con `ENABLE_DB_ADMIN=1`. Guarda cubierta.
  - **FR9**: `test_auth_characterization.py` — **caracteriza el bug** de
    `is_refresh_token_valid` (token aware futuro → `False` erróneo; naive futuro → `True`).
  - **NFR1.1**: `test_jwt_startup.py` cubre `resolve_jwt_secret`.

### Tests — Frontend (ÁREA CLAVE del intent activo `260918-frontend-coverage-gate`)

Estado ACTUAL (línea base sobre la que interviene el intent). Evidencia en `angular-app/`:

- **Runner**: **Vitest** (`^4.0.8`) + `jsdom` (`^25.0.1`) vía el builder
  `@angular/build:unit-test` (`angular.json` → `architect.test.runner: vitest`,
  `tsConfig: tsconfig.spec.json`, `buildTarget: angular-app:build:development`). Migración a
  Vitest COMPLETA: no quedan restos Karma/Jasmine.
- **`skipTests: true` GLOBAL en `angular.json`** — aplicado a TODOS los schematics
  (`component`, `class`, `directive`, `guard`, `interceptor`, `pipe`, `resolver`, `service`).
  El código nuevo NACE sin spec. **Diana directa de FR10.1** (quitar el flag).
- **Sin infraestructura de cobertura** — NO existe `vitest.config.*` en `angular-app/`;
  `angular.json` no declara opciones de `coverage`; NO hay proveedor instalado
  (`@vitest/coverage-v8`/`istanbul` ausentes en devDependencies) ni `coverage.thresholds`.
  `ng test` ejecuta specs pero **NO mide ni exige cobertura**. **Diana directa de FR10.2**
  (añadir `@vitest/coverage-v8` como devDependency — cambio de `package.json`/lock a
  verificar contra `npm ci`).
- **Cobertura de specs casi nula** — SÓLO **2** specs sobre ~90 fuentes en `src/app/`:
  - `core/interceptors/auth.interceptor.spec.ts` — caracteriza el interceptor (Bearer,
    exclusión `/auth/*`, `withCredentials`, refresh en cola ante 401, logout ante
    403/refresh fallido).
  - `core/preloading/idle-preloading-strategy.spec.ts` — lógica pura de precarga por
    inactividad con fake timers.
  - SIN spec: servicios `core/services/*` (`auth`, `budget`, `sync`, `analytics`…), el guard
    `core/guards/auth.guard.ts`, y los componentes de `features/*` y `shared/*`. Los 2 specs
    existentes fijan el patrón Vitest + `@angular/*/testing` a replicar.

### Linting

- **Backend**: `ruff` (`backend/ruff.toml`: `select=["E","F","I"]`,
  `ignore=["E501","E402","E722"]`, `line-length=100`) — **advisory** en CI
  (`continue-on-error`).
- **Frontend**: ESLint flat config (`eslint.config.js`, Angular) — **advisory** (arranca
  tolerante; CI lo corre con `continue-on-error: true`). Dependencias de ESLint declaradas
  pero no instaladas (ver `dependencies.md`). Prettier `^3.8.1` disponible.

### CI/CD

Dos caminos de verificación, AMBOS con `ng test --watch=false` BLOQUEANTE — un threshold de
cobertura activado en `ng test` se propaga a los dos automáticamente:

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

- README extenso (raíz y `angular-app/`); `docs/` incluye
  `docs/BACKLOG-cobertura-frontend-y-pipeline.md` (backlog del intent activo), `docs/DEPLOY.md`,
  `docs/ROLLBACK.md`, `docs/PR-GATE.md`; `AGENTS.md`. Docstrings en inglés; texto de usuario /
  `HTTPException.detail` en castellano. `sync_prizes` está bien comentado pese al god-file. Los
  2 specs frontend llevan docstrings de caracterización con trazas a FR/BR.

## Deuda Técnica y Hallazgos

Este artefacto es el propietario del detalle de deuda; el resto de artefactos referencian
aquí en lugar de repetir.

### Cobertura del frontend y pipeline (intent activo — hallazgo propietario)

- **FR10.1 — `skipTests: true` global** en `angular.json` (todos los schematics): el código
  nuevo nace sin spec. Bloquea que la cobertura crezca de forma natural.
- **FR10.2 — ausencia total de infraestructura de cobertura**: sin `vitest.config.*`, sin
  proveedor (`@vitest/coverage-v8`/`istanbul`) instalado, sin `coverage.thresholds`.
  `ng test` no mide cobertura hoy. Requiere añadir el proveedor (OSS, coste 0 €) y configurar
  un umbral **bajo-y-trinquete (ratcheting)**: el estado base es ~2 specs / ~90 fuentes, así
  que un piso alto rompería de inmediato el gate BLOQUEANTE.
- **FR17.1 — la brecha es de MEANINGFULNESS, no de ausencia de ejecución**: el job `verify`
  de `fly-deploy.yml` YA corre `ng test --watch=false` (bloqueante) en el camino push→`main`.
  No es que el frontend no se pruebe antes de producción; es que esos tests hoy NO imponen
  cobertura (no hay threshold que rompa). Al activar el threshold en `ng test` (FR10.2), la
  meaningfulness se propaga a `verify` sin tocar dos sitios. Orden correcto: **FR10 → FR17.1**.
- **Secuenciación obligada**: sembrar specs de servicios/guard/interceptores críticos ANTES
  de subir el threshold, para no romper el gate bloqueante; `auth.interceptor.spec.ts` e
  `idle-preloading-strategy.spec.ts` ya fijan el patrón.
- **Riesgo de tooling**: añadir `@vitest/coverage-v8` cambia `package.json`/`package-lock.json`;
  verificar `npm ci` + `ng test` en local o contenedor `node:22.22.3` antes de pushear
  (mandato afirmado en `project.md`), pues CI usa `node-version: '22'` y `.nvmrc` (22.22.3)
  vive SÓLO en la raíz.
- **Deuda de paridad de pipeline (preexistente, DIFERIDA — Q5=A)**: `verify` corre `pytest -q`
  **sin `--cov`** mientras `ci.yml` mide `--cov=app`. Es una diferencia de SEÑAL DE COBERTURA,
  **no de seguridad**: gitleaks es BLOQUEANTE en AMBOS caminos (`@v3` en PR, `@v2` en `verify`,
  sin `continue-on-error`). Queda **fuera de alcance** de este intent como deuda de pipeline
  registrada (decisión de calidad/pipeline diferida a un diseño futuro), NO cerrada por
  omisión.
- **Dependencias de ESLint declaradas pero no instaladas** (`angular-eslint`/
  `typescript-eslint`/`@eslint/js`): lint frontend sólo advisory best-effort. Fuera del
  alcance de cobertura; afecta la superficie del gate.
- **Directorio residual** `angular-app/node_modules.old-1789382239/`: árbol `node_modules`
  antiguo en disco (ruido de repo; no afecta build con `npm ci`).

### Área de premios/finanzas

- **Fórmula de premios en un god-file** (`services/data_sync_service.py::sync_prizes`,
  ~1577-1885, dentro de ~84 KB): toda la lógica monetaria de negocio (points/ranking/mvp/
  dream-team, gating, pseudo-jornadas, limpieza defensiva) vive embebida con SQL crudo y
  llamadas a la API de Futmondo intercaladas con `time.sleep()`. Debe extraerse tras una
  capa/función estrecha testeable, **sin ampliar** el god-file ni el patrón SQL-en-router
  (`project.md`).
- **Ausencia de red de caracterización** de `sync_prizes` (ver Tests). Riesgo alto de
  regresión al refactorizar sin caracterizar primero.
- **Doble semántica de "puntos"**: coexisten "puntos" como métrica y `points_prize` como
  término monetario derivado (`round_points * money_per_point`). A aclarar en diseño.
- **Resolución de identidad frágil** en `player_finances`: lookups por
  team_id/user_id/nombre con fallback por coincidencia de nombre — riesgo de doble
  conteo/omisión.
- **SQL inline en routers de analítica/saldos** (`balances.py`, `analytics.py`:
  classification-full, watchlist): anti-patrón a no ampliar.
- **Dependencia dura de la API de Futmondo** en el cálculo: exige dobles/fakes para test a
  coste 0 € (ver `dependencies.md`).

### Área de seguridad (intents anteriores, por FR)

- **FR6 — validación de puja ausente en backend** (`api/v1/endpoints/market.py::place_bid`):
  acepta `price: int = Query(...)` sin validar rango/positividad y proxya directo a Futmondo.
  La única validación vive en el frontend (`bid-dialog.component.ts`), evadible.
- **FR7 — exposición del endpoint de fotos**: `GET /api/v1/photos/{player_id}` NO está en
  `AUTH_EXCLUDED_PATHS` (el middleware SÍ exige Bearer). El punto real es `/static/photos/*`
  (StaticFiles) fuera del prefijo protegido; las 302 apuntan ahí.
- **FR8 — `SSL_VERIFY=0` huérfano**: declarado en `docker-compose.yml` (local) pero sin
  lector en Python (0 usos); ausente de `backend/fly.toml [env]`. Inocuo hoy pero no
  aislado/documentado de forma inequívoca.
- **FR9 — bug de precedencia naive/aware** en `token_store.is_refresh_token_valid`:
  con `expires_at` aware (caso real PostgreSQL/Turso) el ternario devuelve un `datetime`
  truthy → `return False`, **rechazando tokens ACTIVOS futuros**. Corregirlo exige actualizar
  los tests de caracterización que congelan el fallo.
- **FR18 — guarda de administración**: `_require_db_admin()`/`ENABLE_DB_ADMIN` ya correcta y
  testeada.

### Deuda estructural (no ampliar)

- **SQL crudo disperso** en `auth/token_store.py`, `routes._auto_detect_championships`,
  `_helpers.get_championship_config`, `balances.py`, `analytics.py` sin capa repositorio;
  nueva persistencia debe ir tras la capa estrecha `stores/`.
- **God-files** en `services/`: `data_manager_v2.py` (~166 KB), `data_sync_service.py`
  (~84 KB), `assistant_service.py` (~51 KB). No deben crecer.
- **Imports dinámicos** dentro de funciones (p. ej. `import requests` en `get_player_photo`);
  preferir import estático (convención del equipo).
- **Cobertura de errores amplia**: bloques `except Exception` que mapean a 500 sin distinguir
  causas.

### Riesgos de contexto

- El job `verify` de `fly-deploy.yml` corre `pytest -q` **sin `--cov`** (sí con gitleaks); no
  es idéntico al gate de PR pero es defensa en profundidad.
- `libsql-experimental==0.0.55` sólo compila en Python 3.12 (los tests usan fakes SQLite).
- Restricción dura de coste 0 € en toda propuesta.
