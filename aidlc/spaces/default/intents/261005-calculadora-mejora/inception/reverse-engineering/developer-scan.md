# Developer Code Scan — futmondo-analytics (link 1 / pipeline)

> Escaneo profundo del repositorio completo (FULL RESCAN, raíz `./`) para el intent
> `calculadora-mejora`. Este archivo es el work product del link DEVELOPER; el
> link ARCHITECT lo sintetiza en los 9 artefactos del CodeKB. Prosa en castellano;
> identificadores, rutas, nombres de framework y los encabezados de sección en
> inglés se conservan como preserved tokens.

## Developer Code Scan Results

### Scan Coverage

**Analyzed deeply**
- `README.md`
- `docker-compose.yml`
- `angular-app/package.json`
- `angular-app/angular.json`
- `angular-app/src/app/app.routes.ts`
- `angular-app/src/app/features/calculator/calculator.component.ts`
- `angular-app/src/app/features/calculator/calculator.component.html` (revisado estructuralmente)
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/api/v1/endpoints/player_finances.py`
- `backend/app/api/v1/endpoints/roster.py`
- `backend/app/services/prizes/calculator.py`
- `backend/app/services/prizes/team_prizes_writer.py`
- `backend/app/services/analytics/application/calculations.py` (cabecera + helpers de resolución)
- `backend/app/services/data_sync_service.py` (cabecera + estructura de clase)
- `backend/app/services/data_manager_v2.py` (cabecera + patrón de delegación DDD)
- `backend/pytest.ini`
- `backend/ruff.toml`
- `backend/conftest.py` (fixtures fake in-memory)
- `.github/workflows/ci.yml`

**Skimmed only**
- `backend/app/api/v1/endpoints/` (resto de routers: market, analytics, balances, sync, transactions, user, assistant, etc. — inventariados por nombre/tamaño)
- `backend/app/services/data_manager/**` (12 submódulos DDD extraídos del god-file, estructura `application/infrastructure/domain` uniforme)
- `backend/app/services/sync/**` (11 orquestadores de sync con misma forma DDD)
- `backend/app/services/assistant/**`, `backend/app/services/analytics/**` (fachadas + puertos + adaptadores)
- `backend/app/auth/**`, `backend/app/stores/**`, `backend/app/security/**`
- `backend/tests/**` (~55 archivos de test, inventariados por nombre)
- `angular-app/src/app/features/**` (resto de pantallas: budget, market, stats, evolution, analytics sub-tabs, etc.)
- `angular-app/src/app/core/services/**`, `core/interceptors/**`, `shared/**`
- `.github/workflows/fly-deploy.yml`, `daily-sync.yml`, `sofascore-sync.yml`
- `docs/**`, `proxy/**`, `cron/**`, `scripts/**`, `backend/scripts/**`
- `.kiro/**` (toolchain AI-DLC — fuera del alcance de la aplicación)

### Packages Found
- `angular-app` — frontend SPA/PWA — TypeScript — pantallas de usuario (incluida `calculator`), servicios HTTP, interceptor de auth.
- `backend` — API HTTP + lógica de negocio — Python — FastAPI app, servicios de dominio, sync de datos, cálculo de premios/finanzas.
- `proxy` / `angular-app/nginx*.conf` — Nginx reverse proxy (local y prod).
- `cron` — máquinas Fly one-shot para sync programado (`daily-sync`, `sofascore-sync`).

### Build System
- **Type**: npm (frontend) + pip/venv (backend); orquestación local con Docker Compose.
- **Config Files**: `angular-app/package.json`, `angular-app/angular.json`, `angular-app/tsconfig*.json`, `angular-app/eslint.config.js`, `angular-app/.prettierrc`, `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`, `docker-compose.yml`, `backend/Dockerfile`, `angular-app/Dockerfile`, `*/fly.toml`, `.nvmrc` (`22.22.3`).
- **Build Dependencies**: Angular CLI 22 (`@angular/build:application`) → bundle PWA con service worker (`ngsw-config.json`); backend arranca con `uvicorn` (`run.py`). Node fijado por `.nvmrc`.

### APIs Discovered
- **REST (externas / consumidas por el frontend)** — montadas en `backend/app/main.py` bajo prefijos `/api/v1/*` y `/auth/*`. Todas las `/api/v1/*` exigen Bearer JWT vía `AuthMiddleware`; excluidas: `/auth/login|refresh|logout`, `/health`, `/`, `/docs`, `/openapi.json`, `/redoc`, y el mount público `/static/photos/*`.
  - `/api/v1/player-finances/` (GET) — **cálculo de finanzas por usuario** (foco del intent, ver Handoff Summary).
  - `/api/v1/roster/sell`, `/api/v1/roster/*` (POST/GET) — alta/baja al mercado y plantilla; **consumidos por la pantalla Calculadora**.
  - `/api/v1/market/today` (GET) — balance + pujas activas; **consumido por la Calculadora**.
  - Otros routers: `matchdays`, `initialize`, `database`(reset), `statistics`, `user-stats`, `clausulable-players`, `sync`, `analytics`, `balances`, `championships`, `phantoms`, `market`, `favorites`, `transactions`, `sofascore`(sync+detail), `user`, `assistant`.
  - `/api/v1/photos/{player_id}` (GET, autenticado) — redirige 302 al mount público.
- **Internas (contratos de dominio)**: `prizes/calculator.py:calculate_round_prizes()` (función pura, sin I/O); `prizes/team_prizes_writer.py:replace_team_prizes()` (reemplazo transaccional atómico); puertos DDD (`analytics/domain/ports.py`, `assistant/domain/ports.py`) con inversión de dependencias.
- **Integraciones externas (salientes)**: API Futmondo (`futmondo_client.py`, auth por usuario), API Sofascore (`sofascore_client.py`, vía `curl_cffi`), Gemini / Groq (asistente IA).

### Frameworks & Libraries
- **Frontend**: Angular `^22.2.1` (standalone components, signals, `OnPush`, lazy routes), Angular Material `^22.2.1` + CDK, `chart.js` `^4.5.1` + `ng2-charts` `^10.0.0`, `rxjs` `~7.8.0`, `marked` `^18.0.11`, service worker (`@angular/service-worker`). Dev: `@angular/build`/`cli` `^22.2.0`, `vitest` `4.1.11` + `@vitest/coverage-v8` `4.1.11` (pin exacto), `typescript` `~6.0.2`, `jsdom`, `prettier`. `packageManager: npm@11.12.1`.
- **Backend**: FastAPI `0.141.1`, uvicorn `0.54.0`, pydantic `2.13.5`, `PyJWT` `2.15.0`, `psycopg2-binary` `2.9.13` (Neon PostgreSQL), `requests` `2.34.2`, `curl_cffi` `0.16.3`, `python-multipart`, `python-dotenv`, `google-genai` `1.14.0`, `groq` `0.25.0`. Test: `pytest` `9.1.1`, `pytest-cov` `7.1.0`, `httpx` `0.28.1`.
  - **Nota (corrección de contexto)**: `requirements.txt` está **ya pinneado a versión exacta** (`==`); los rangos abiertos descritos en `team.md` corresponden a un estado anterior ya resuelto por un intent previo.

### Test Coverage
- **Test Directories**: `backend/tests/` (~55 archivos, mayoría `*_characterization.py`: prizes, sync_*, data_manager_* por responsabilidad, auth, finance, durable session/task, integration errors, jwt startup, etc.); specs del frontend junto al código (`*.spec.ts` en `core/services`, `core/guards`, `core/interceptors`, `features/market`).
- **Test Frameworks**: `pytest` (backend, fakes in-memory en `conftest.py`: `_FakeInMemoryDB`/`_FakeCursor` sobre SQLite `:memory:`, `clean_jwt_env`, `fake_db`); `vitest` vía `ng test` (builder `@angular/build:unit-test`, runner `vitest`) en el frontend.
- **Coverage Config**: Backend — piso **bloqueante** `--cov-fail-under=27` en `pytest.ini` (line-only, sin `--cov-branch`; cobertura real medida ~27.52%). Frontend — umbrales por métrica en `angular.json > test.coverageThresholds`: statements 19 / branches 19 / functions 17 / lines 18 (ratchet manual; sólo sube).

### Code Quality Indicators
- **Linting**: `ruff` backend (`backend/ruff.toml`, `py312`, `line-length=100`, `select=["E","F","I"]`, `ignore=["E501","E402"]`, `per-file-ignores` para god-files/adaptadores/tests). ESLint frontend: config presente (`eslint.config.js`) pero **advisory** y sus devDependencies no instaladas (deuda diferida). Prettier configurado (`.prettierrc`).
- **CI/CD**: `.github/workflows/ci.yml` (gate en `pull_request → main`) y `fly-deploy.yml` (push a `main` → deploy Fly.io). Crons: `daily-sync.yml`, `sofascore-sync.yml`.
  - **Nota (corrección de contexto)**: en `ci.yml` el **`ruff check`, `pip-audit` y `npm audit --audit-level=high` ya están BLOQUEANTES** (con pins `ruff==0.16.9`, `pip-audit==2.10.1`); `pytest --cov=app --cov-fail-under` y `ng test` bloqueantes; `gitleaks-action@v3` bloqueante; **ESLint sigue advisory** (`continue-on-error`). El estado "advisory" descrito en `team.md`/`project.md` para audits/lint ya fue endurecido por un intent anterior.
- **Documentation**: README raíz detallado + `docs/` extenso (DEPLOY, ROLLBACK, PR-GATE, PROJECT_CONTEXT, planes de migración/backlog). Docstrings de módulo ricos en los componentes nuevos extraídos (DDD).

### Technical Debt Signals
- **God-files** (regla afirmada: NUNCA ampliar/reescribir) — `data_manager_v2.py` (~33 KB en disco hoy, antes ~166 KB; ahora delega a submódulos DDD `data_manager/<responsabilidad>/{application,infrastructure,domain}`), `data_sync_service.py` (~15 KB tras extracciones), `assistant_service.py` (~2 KB, fachada fina). La descomposición DDD está **en curso y avanzada**; los `per-file-ignores` de `ruff.toml` registran `E722`/`F841`/`F401`/`I001` como **deuda registrada** movida verbatim a los adaptadores (no saneada, para preservar comportamiento byte-a-byte).
- **Patrón SQL-en-router / SQL inline** — persiste en `player_finances.py` (`_get_finance_config` ejecuta `SELECT` directo) y en `main.py` (ruta de fotos con `SELECT` inline). Regla afirmada: código nuevo debe ir tras una capa/función estrecha testeable, no ampliar este patrón.
- **`bare-except` / broad-except** — deuda registrada en `data_manager_v2.py`, `photo_service.py` y adaptadores extraídos; `E722` re-habilitado como advisory por trinquete pero silenciado por fichero en los god-files.
- **ESLint frontend sin instalar** — `npx ng lint` tolerante a ausencia; deuda diferida explícita.
- **DB SQLite local commiteada** — `backend/futmondo_data.db` (65 KB) presente en el árbol; en prod sólo se usa Neon PostgreSQL (`DATABASE_URL`).
- **`node_modules.old-*`** — directorio obsoleto gigante en `angular-app/` (ruido de workspace, no afecta build).
- **Secrets handling (positivo)**: `config.py` fuerza fail-fast si `JWT_SECRET` falta o es el default inseguro en el servicio web; credenciales Futmondo nunca en claro (clave de cifrado `FUTMONDO_CRED_KEY`). No se observaron secretos hardcodeados en el código de aplicación.

## Handoff Summary

- **Intent-relevant finding (foco Calculadora)**: La pantalla **Calculadora** (`angular-app/src/app/features/calculator/calculator.component.ts`, ruta `/calculator` con `authGuard`) es hoy un **planificador de ventas/proyección de balance**, NO una calculadora de premios. Lee tres fuentes en paralelo en `loadData()`: `rosterService.getMyRoster()`, `GET /api/v1/market/today` (balance + `active_bids_total`/`active_bids_count`) y `rosterService.getOnSale()`. Sus cómputos viven en `computed()` de signals: `selectedTotal` (valor de jugadores seleccionados proyectado por `change * daysAhead`), `onSaleTotal`, y `futureBalance = balance + selectedTotal + onSaleTotal − activeBidsTotal`. Acciones: `sellPlayers()` → `POST /api/v1/roster/sell`, `cancelSale()`. La proyección temporal (`getProjectedValue`) es **lineal** (`value + change * días`). **El cálculo de finanzas/premios por usuario** vive en el backend en `GET /api/v1/player-finances/` (`player_finances.py`), que agrega `initial_budget + transaction_profit + ranking + mvp + dream_team + points + net_adjustment`, leyendo **todo el dinero de premio desde la tabla `team_prizes`** (single source of truth) — y esa tabla la puebla `DataSyncService.sync_prizes()` usando la **función pura** `prizes/calculator.py:calculate_round_prizes()` (reglas BR1.1–BR3.2: points siempre, ranking/MVP/dream-team sólo si la ronda está cerrada, split proporcional flop/top, empates compartidos) y el **escritor transaccional atómico** `prizes/team_prizes_writer.py:replace_team_prizes()`. Nota: la Calculadora frontend **no** consume hoy `/api/v1/player-finances/` (eso lo hace la pantalla `finances`); si la mejora busca cálculo financiero/de premios en la Calculadora, ese endpoint y los módulos `prizes/` son el punto de integración natural tras una capa estrecha testeable.
- **Risks / follow-up**:
  - **No ampliar god-files ni SQL-en-router**: cualquier lógica nueva de cálculo debe ir tras una función/capa estrecha testeable (patrón ya establecido por `prizes/calculator.py` puro + `conftest.py` fakes), no dentro de `data_manager_v2.py`/`data_sync_service.py` ni como `SELECT` inline en el router (deuda viva en `player_finances.py`).
  - **Characterization-first**: `calculator.component.ts` y los `computed()` de proyección de balance **no tienen spec** hoy (sí hay `bid-dialog.component.spec.ts` en market, pero ninguno de calculator); congelar su comportamiento con `vitest` antes de refactorizar/extender es coherente con el mandato afirmado.
  - **Trazabilidad de dinero**: cualquier cambio que toque premios debe respetar el invariante `team_prizes` = única fuente de verdad y el reemplazo atómico (`replace_team_prizes`), para no reintroducir el estado mixto que el escritor transaccional corrige.
  - **Pisos de cobertura sólo suben** (backend `--cov-fail-under=27`, frontend thresholds 19/19/17/18); el código nuevo de la Calculadora debe venir con specs que aseveren el efecto para no romper el gate ni forzar bajar el piso.
  - **Correcciones de contexto para el architect**: (1) `requirements.txt` ya está pinneado a `==`; (2) en `ci.yml` ruff/pip-audit/npm audit **ya son bloqueantes** (sólo ESLint frontend sigue advisory). Varias afirmaciones de `team.md`/`project.md` describen un estado previo al endurecimiento ya aplicado — sintetizar el estado **actual del código**, no el histórico de las reglas.
