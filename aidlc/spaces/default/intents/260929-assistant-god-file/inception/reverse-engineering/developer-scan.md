# Developer Scan Handoff — futmondo-analytics (full rescan)

Enlace 1 (developer) de Reverse Engineering. Escaneo profundo de TODO el repo
(`.`) para el intent **Oleada 2 god-files (FR13)**: descomponer
`backend/app/services/assistant_service.py` replicando el patrón DDD de la
Oleada 1 (`prizes/`, `analytics/`). No escribo los 9 artefactos de codekb — los
sintetiza el architect (enlace 2) a partir de este handoff. Cada hallazgo se
registra una vez en su sección y se referencia; no se repite (depth mínima).

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply**:
  - `backend/app/services/assistant_service.py` (objetivo del intent; leído íntegro)
  - `backend/app/services/analytics/` (paquete de referencia Oleada 1: `__init__.py`, `facade.py`, `domain/ports.py`, `infrastructure/data_manager_adapter.py`, `application/calculations.py`)
  - `backend/app/services/analytics_service.py` (shim de re-export de referencia)
  - `backend/app/services/prizes/` (`__init__.py`, `calculator.py`, `team_prizes_writer.py`)
  - `backend/app/services/` (inventario y tamaños de todos los módulos, incluidos los god-files `data_sync_service.py`, `data_manager_v2.py`; `db_connection.py`)
  - `backend/app/api/v1/endpoints/` (inventario completo; `assistant.py` leído)
  - `backend/app/main.py` (montaje de routers, middleware auth/CORS)
  - `backend/app/core/config.py` (config, endurecimiento `JWT_SECRET` NFR1.1)
  - `backend/pytest.ini`, `backend/ruff.toml`, `backend/requirements.txt`, `backend/conftest.py`, `backend/.pip-audit-allowlist`
  - `backend/tests/` (inventario completo de la suite de caracterización)
  - `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml` (gate CI y gate de deploy)
  - `angular-app/` (`package.json`, `angular.json`, `eslint.config.js`; árbol `src/app/` — core/services, features, shared)
  - `README.md`, `docs/` (inventario; `BACKLOG-plan-intents.md` como origen del intent)
- **Skimmed only**:
  - `backend/scripts/`, `backend/app/auth/`, `backend/app/stores/`, `backend/app/security/`, `backend/app/models/` (a granularidad de directorio; no centrales para este intent)
  - `angular-app/src/app/features/*` (a granularidad de directorio; el intent es backend-only)
  - `proxy/`, `cron/`, `stitch_*` (mockups estáticos), `docker-compose.yml`, ficheros `Dockerfile`/`fly.toml`
  - `.kiro/` (framework AI-DLC, fuera del sistema de aplicación)

### Packages Found

- `backend/app` — servicio web — Python 3.12 — FastAPI API (`futmondo-api`)
- `backend/app/services` — capa de servicios/dominio — Python — lógica de negocio; contiene los 3 god-files y los 2 paquetes DDD ya extraídos
- `backend/app/services/analytics` — bounded context DDD (Oleada 1) — Python — **patrón de referencia** (facade + domain/ports + application + infrastructure)
- `backend/app/services/prizes` — paquete de cálculo puro (Oleada 1) — Python — patrón de referencia secundario (cálculo puro + writer de persistencia)
- `backend/app/api/v1/endpoints` — routers HTTP — Python — 22 routers (incluye `assistant.py`)
- `backend/app/auth`, `app/stores`, `app/security`, `app/core`, `app/models` — auth JWT / repositorios durables / protección credenciales / config / modelos
- `angular-app` — frontend — TypeScript — Angular 22 PWA (`futmondo-app`); fuera del alcance de cambio de este intent (solo sube ratchet de cobertura)

### Build System

- **Type**: dual — Python (backend) + npm/Angular CLI (frontend)
- **Config Files**: `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`, `backend/fly.toml`, `backend/Dockerfile`; `angular-app/package.json`, `angular-app/angular.json`, `angular-app/eslint.config.js`, `.nvmrc` (`22.22.3`); `docker-compose.yml` (local); `.github/workflows/*.yml`
- **Build Dependencies**: backend sin gestor de paquetes con lock (pip + `requirements.txt` con pins exactos); frontend `npm ci` sobre `package-lock.json`

### APIs Discovered

- **REST interno (FastAPI)** — `backend/app/api/v1/endpoints/` — 22 routers montados en `main.py` bajo `/api/v1/*` (auth por `AuthMiddleware`, Bearer JWT; excluidos `/auth/*`, `/health`, `/`, `/docs`)
- **Asistente IA** — `backend/app/api/v1/endpoints/assistant.py` — chat + persistencia de conversaciones; consume la superficie pública `get_assistant_service()` + `await service.ask(...)` de `assistant_service.py`
- **Auth** — `backend/app/auth/routes.py` — `/auth/login|refresh|logout`
- **Integraciones externas (salientes)** — API Futmondo (`futmondo_client.py`), API Sofascore vía `curl_cffi` (`sofascore_client.py`), y **LLM externos** consumidos por el asistente: Groq (`openai/gpt-oss-120b`) con fallback a Gemini (`google-genai`)

### Frameworks & Libraries

Backend (pins exactos en `requirements.txt`): `fastapi==0.141.1`, `uvicorn[standard]==0.54.0`, `pydantic==2.13.5`, `psycopg2-binary==2.9.13`, `curl_cffi==0.16.3`, `PyJWT==2.13.0`, `requests==2.34.2`, `google-genai==1.14.0`, `groq==0.25.0`, `python-dotenv==1.2.3`, `python-multipart==0.0.32`; test: `pytest==9.1.1`, `pytest-cov==7.1.0`, `httpx==0.28.1`. Frontend: Angular 22 + Material 22 (PWA), Chart.js/ng2-charts, `@vitest/coverage-v8==4.1.11` (ver `package.json`).

### Test Coverage

- **Test Directories**: `backend/tests/` (32 ficheros `test_*.py`, suite de caracterización); frontend `*.spec.ts` colocados junto a servicios/componentes en `angular-app/src/app/`
- **Test Frameworks**: pytest + pytest-cov (backend); Angular `ng test` con builder `@angular/build:unit-test` + Vitest coverage-v8 (frontend)
- **Coverage Config**: backend `pytest.ini` → `--cov-fail-under=27` bloqueante (line-only, sin `--cov-branch`); frontend `angular.json` `coverageThresholds` (statements 15 / branches 15 / functions 13 / lines 14). Fakes in-memory en `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor` SQLite `:memory:`, `clean_jwt_env`, `fake_db`) — sin red, sin BD real, sin credenciales reales

### Code Quality Indicators

- **Linting**: `backend/ruff.toml` (`py312`, `line-length=100`, `select=["E","F","I"]`, `ignore=["E501","E402"]`; `[lint.per-file-ignores]` para tests/conftest y **god-files** — `assistant_service.py` tiene `["I001"]`, `data_manager_v2.py` `["E722","F841","F401","I001"]`, `data_sync_service.py` `["F401","I001"]`, `photo_service.py` `["E722","F841"]`). `ruff check` **ya bloqueante** en ambos gates. Frontend ESLint aún advisory (`continue-on-error`)
- **CI/CD**: `.github/workflows/ci.yml` (PR→main, job `quality`) y `fly-deploy.yml` (push→main, job `verify` que replica el gate; luego `deploy-backend`→`deploy-frontend`→`smoke-test /health`). Bloqueantes: gitleaks `@v3` (unificado), `pytest --cov=app`, `ruff check`, `pip-audit` (entorno instalado + allowlist expiry), `npm audit --audit-level=high`, `ng test`. Crons `daily-sync.yml`/`sofascore-sync.yml`
- **Documentation**: `README.md` completo; `docs/` extenso (BACKLOG, DEPLOY, ROLLBACK, PROJECT_CONTEXT); docstrings de calidad en los paquetes DDD de referencia

### Technical Debt Signals

- **God-files** (regla afirmada: NUNCA ampliarlos ni el patrón SQL-en-router; saneo quirúrgico solo): `assistant_service.py` (**51 681 bytes / 1158 líneas** — objetivo del intent), `data_manager_v2.py` (166 173 bytes), `data_sync_service.py` (84 591 bytes), `photo_service.py` (22 764 bytes)
- **SQL inline en la capa de servicio**: `assistant_service.py` contiene **42 `cursor.execute`** con SQL crudo embebido, esparcidos por los seams objetivo — patrón que la Oleada 1 relocó tras un `AnalyticsDataPort` (Protocol) + adapter de infraestructura
- **`except Exception` amplio / silencioso**: en `assistant_service.py` (p. ej. `_ctx_market_from_db`, `_save_market_to_db` con `except: return ""` / `logger.warning`), y bare-except registrados como deuda en `data_manager_v2.py`/`photo_service.py` (E722 en per-file-ignores)
- **`CREATE TABLE IF NOT EXISTS` en caliente**: `AssistantUsageTracker._ensure_table()` crea `assistant_usage`; `_save_market_to_db` crea `market_today`; el endpoint crea `assistant_conversations` — esquema implícito, sin migraciones
- **Cobertura directa CERO del objetivo**: ningún test de `backend/tests/` referencia el asistente (verificado: 0 matches de "assistant" en la suite) → **characterization-first obligatorio antes de refactorizar** (mandato afirmado)
- **Rangos de modelo LLM frágiles**: lista hardcodeada `["gemini-3.6-flash","gemini-3.5-flash"]` y `openai/gpt-oss-120b`; formaciones hardcodeadas en `_ctx_formations`

## Handoff Summary

- **Intent-relevant finding**: `assistant_service.py` (1158 líneas, 51 KB, cobertura CERO) es descomponible al patrón DDD de la Oleada 1 con seams limpiamente delimitados y una superficie pública mínima que preservar. Superficie pública a mantener intacta: el singleton `get_assistant_service()` (líneas ~1150-1158) y `async def ask(...)` (línea 507), consumidos por `app/api/v1/endpoints/assistant.py` (`from app.services.assistant_service import get_assistant_service`). Seams identificados con evidencia de fichero:
  - **AssistantUsageTracker** (clase, línea ~155): agregado con tabla `assistant_usage` (`_ensure_table`, `can_make_request`, `record_usage`, `get_usage_summary`) — candidato a módulo/infra con su propio port de persistencia.
  - **Capa factual** (`_try_factual_answer` línea 356 + 4 handlers `_factual_balance`/`_factual_roster`/`_factual_standings`/`_factual_team_value`, líneas 367-497) + constante `FACTUAL_PATTERNS`.
  - **ContextBuilder** (`_build_context` línea 700 + 10 métodos `_ctx_*`, líneas 737-1127): concentra la mayoría de los **42 `cursor.execute`**; es el seam con más SQL crudo → relocar tras un data-port como `AnalyticsDataPort`.
  - **Guardrails** (`_check_guardrails` línea ~130 + `ALLOWED_KEYWORDS`/`BLOCKED_PATTERNS`/`GUARDRAIL_RESPONSE`): módulo **puro** (solo regex/strings, sin I/O) → el más fácil de extraer y testear.
  - `ask()` queda como orquestador delgado (guardrails → identidad → factual → LLM con fallback Groq→Gemini).
- **Reference pattern (Oleada 1) a replicar** — `backend/app/services/analytics/`: `__init__.py` re-exporta la fachada; `facade.py` (`AnalyticsService`) preserva superficie pública y solo delega, con inyección por constructor con default (`data: Optional[AnalyticsDataPort] = None`); `domain/ports.py` define un `typing.Protocol` consumer-owned SIN SQL ni framework; `application/calculations.py` es la lógica pura sobre el port; `infrastructure/data_manager_adapter.py` es el ÚNICO sitio con SQL crudo (`db.adapt_params` + `?`-placeholders). Además `analytics_service.py` queda como **shim de re-export** para no romper el import histórico. `prizes/` es el patrón secundario (cálculo puro `calculator.py` + `team_prizes_writer.py` para persistencia). Recomendación: para `assistant/` replicar fachada delgada (`get_assistant_service()`+`ask()`), guardrails como módulo puro, ContextBuilder + AssistantUsageTracker tras ports con adapters de infraestructura sobre `db_connection.get_db()`, y dejar `assistant_service.py` como shim de re-export.
- **Risks / follow-up**:
  - Cobertura CERO del objetivo → **characterization-first** con los fakes de `conftest.py` (`fake_db`) antes de mover una sola línea; la reviewer corre `ruff check` (no `format`), y `assistant_service.py` solo tiene `I001` en per-file-ignores → al crear el paquete, formatear SOLO los ficheros nuevos (no en masa) para no invalidar el pase de revisión ni romper el gate.
  - `assistant_service.py` mezcla I/O de red (Groq/Gemini) con SQL y con lógica pura; el `except Exception` amplio alrededor de las llamadas LLM y de las lecturas de mercado debe preservarse en comportamiento (degradar, no romper) al reubicarse.
  - Tablas creadas en caliente (`assistant_usage`, `market_today`, `assistant_conversations`) atan el tracker/context al esquema implícito; el adapter de infra debe preservar ese `CREATE TABLE IF NOT EXISTS` idempotente para no cambiar comportamiento observable.
  - Restricciones duras a honrar en el diseño: coste 0 € (tiers gratuitos), gate CI bloqueante intacto (gitleaks+pytest+ng test), NO ampliar god-files ni SQL-en-router, NO reformateo masivo, NO bajar el piso de cobertura (`--cov-fail-under=27`, solo sube por trinquete).
