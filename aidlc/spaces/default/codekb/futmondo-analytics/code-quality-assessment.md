# Code Quality Assessment — Futmondo Analytics

## Gate de CI (bloqueante)

El sistema tiene un **gate de CI bloqueante operativo** replicado en dos
workflows para cubrir PR y push directo:

- `.github/workflows/ci.yml` — job `quality`, disparo `pull_request → main`
  (required status check vía branch protection).
- `.github/workflows/fly-deploy.yml` — job `verify`, disparo `push → main`; los
  deploys dependen de él vía `needs:` (los `needs:` no cruzan workflows, por eso
  el gate se replica). Cadena: `verify → deploy-backend → deploy-frontend →
  smoke-test`.

Pasos bloqueantes verificados en **ambos** gates:

| Check | Herramienta | Nota |
|---|---|---|
| Secretos | gitleaks-action **@v3** (unificado) | Bloqueante desde el inicio |
| Lint backend | `ruff check .` (ruff **0.16.9** pin) | Promovido a bloqueante; sin `--fix` ni `ruff format` |
| Tests backend | `pytest -q --cov=app` con piso | `--cov-fail-under=27` (en `pytest.ini`) |
| Allowlist pip-audit | `scripts/check-allowlist-expiry.sh` | Entrada caducada vuelve a bloquear |
| Dep audit backend | `pip-audit` (entorno instalado, sin `-r`; pin **2.10.1**) | Bloquea findings CON fix; sin fix → allowlist versionada |
| Tests frontend | `ng test --watch=false` (Vitest) | Umbrales de cobertura dentro de `ng test` |
| Dep audit frontend | `npm audit --audit-level=high` | Trinquete de severidad solo endurece |

CI inyecta un `JWT_SECRET` efímero no productivo (`ci-ephemeral-secret-not-a-real-one`)
para que la app importe (fail-fast NFR1.1 en `config.resolve_jwt_secret`).

## Pisos de cobertura heredados (ratchet solo sube)

- **Backend**: `--cov-fail-under=27` (line-coverage total, sin `--cov-branch`),
  definido en `backend/pytest.ini`. Valor medido exacto sin margen (cobertura
  real ~27.52% al fijarlo). Reportado en paridad en `ci.yml` y el job `verify`.
- **Frontend**: `coverageThresholds` en `angular.json` (target `test`):
  `statements 19`, `branches 19`, `functions 17`, `lines 18`. Enforcement dentro
  de `ng test` (builder `@angular/build:unit-test`, runner Vitest), sin pasos
  extra ni `continue-on-error`.

Regla afirmada: NUNCA bajar/relajar un umbral para pasar el gate; el flapping se
arregla en el test no-determinista.

## Suite de tests existente

- **Backend** (`backend/tests/`): suite amplia **characterization-first** (~50+
  ficheros `test_*.py`). Cubre:
  - **Auth**: `test_auth_characterization.py`, `test_jwt_startup.py`
    (endurecimiento NFR1.1), `test_token_store_migrations.py`,
    `test_durable_session_*` (sesión durable), `test_durable_task_*`.
  - **Integración/errores**: `test_integration_errors.py`,
    `test_futmondo_client_typed_failures.py`, `test_error_layer_hardening.py`,
    `test_sync_integration_failure_effect.py`, `test_sync_degraded_steps.py`,
    `test_tls_verification.py`.
  - **Dominio/sync/premios**: numerosos `test_sync_*` y `test_data_manager_*`
    (characterization de ramas de sync y data manager), `test_prizes_*`,
    `test_finance_characterization.py`, `test_analytics_service.py`,
    `test_market_bid_*`, `test_assistant_*`.
  - Fixtures fake in-memory en `conftest.py` (SQLite), **sin red, sin DB real y
    sin credenciales/tokens reales** (gitleaks escanea también los tests).
- **Frontend** (`angular-app/src/**`): specs Vitest, incluidos los de auth
  **directamente relevantes para F1**: `auth.service.spec.ts`,
  `auth.interceptor.spec.ts`, `auth.guard.spec.ts`, más specs de servicios de
  feature (budget, stats, market, roster, sync, favorites, analytics, assistant,
  championship, evolution) e `idle-preloading-strategy.spec.ts`.

## God-files como deuda conocida (NO ampliar)

Regla durable afirmada: NUNCA ampliar ni reescribir los god-files; el código
nuevo va tras una capa/función estrecha y testeable.

- `app/services/data_manager_v2.py` — ~33 KB observado en disco (ref. histórica
  ~166 KB; parte extraída a `data_manager/.../infrastructure/*_adapter.py`).
  `ruff.toml` lo registra con `E722,F841,F401,I001` como deuda, en vez de
  sanearlo tocando el fichero.
- `app/services/data_sync_service.py` — ~15 KB observado (ref. histórica ~84 KB).
  `ruff.toml`: `F401,I001`.
- `app/services/assistant_service.py` (~2 KB real; `I001` en ignore) y
  `photo_service.py` (~23 KB; `E722,F841` registrado como deuda afirmada Q6).

Patrón de SQL-en-router/endpoint también presente (p. ej. consultas inline en
`auth/routes.py` y `api/v1/endpoints/user.py`): deuda a no ampliar.

## Señales de calidad / endurecimientos positivos

- **Manejo de errores tipado** (`integration_errors.py`): jerarquía
  recoverable/fatal con constructor que **no acepta** material de credencial
  (imposibilidad de fuga en `str/repr/args`, NFR3).
- **Seguridad de credenciales**: password Futmondo **nunca** en memoria
  (`session_store.UserSession`), handle de re-auth cifrado en reposo
  (`FUTMONDO_CRED_KEY`); JWT fail-fast en arranque del web (NFR1.1,
  `test_jwt_startup.py`).
- **Arranque resiliente**: schemas idempotentes degradan a warning
  (FR3.2.2/BR1.6) en vez de tumbar el proceso.
- `ruff.toml` arranca con `select = ["E","F","I"]`, `line-length=100`,
  `target-version=py312`; el comentario de cabecera quedó **stale** (describe modo
  advisory) aunque el gate ya corre `ruff check` bloqueante — deuda de
  documentación registrada en `team.md`.

## Relevancia para F1 (login nativo iOS)

- El contrato de auth está **bien cubierto por tests** (characterization backend +
  specs frontend), lo que da una red de seguridad para el ajuste aditivo D-01:
  cualquier cambio del transporte del refresh token debe preservar la suite verde
  y respetar los pisos de cobertura (ratchet solo sube).
- Reglas de seguridad durables aplicables a F1: refresh token en **Keychain**,
  nunca en claro; nunca `JWT_SECRET` por defecto en producción; sin credenciales
  reales en specs.

## Sources

- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`
- `backend/pytest.ini`, `backend/ruff.toml`, `backend/.pip-audit-allowlist`
- `angular-app/angular.json`, `angular-app/package.json`, `angular-app/eslint.config.js`
- Listado de `backend/tests/` y `angular-app/src/app/core/**/*.spec.ts`
- `backend/app/services/integration_errors.py`, `backend/app/core/config.py`,
  `backend/app/auth/session_store.py`

## Assumptions & Open Questions

- El porcentaje de cobertura actual no se recomputó en este escaneo; se reporta
  el **piso** configurado (backend 27, frontend 19/19/17/18) y el valor histórico
  (~27.52%) que motivó el piso backend, verificado por los comentarios de
  `pytest.ini`.
