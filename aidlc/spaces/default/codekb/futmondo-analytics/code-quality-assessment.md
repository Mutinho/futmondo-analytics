# Code Quality Assessment — futmondo-analytics

## Cobertura de test

- **Backend**: `backend/tests/` con 32 ficheros `test_*.py` (suite de
  caracterización). Framework `pytest` + `pytest-cov`. Piso bloqueante
  `--cov-fail-under=27` en `pytest.ini` (line-only, sin `--cov-branch`); solo
  sube por trinquete. Fakes in-memory en `conftest.py` (`_FakeInMemoryDB`/
  `_FakeCursor` SQLite `:memory:`, `clean_jwt_env`, `fake_db`) — sin red, sin BD
  real, sin credenciales reales.
- **Frontend**: `*.spec.ts` colocados junto a servicios/componentes; `ng test`
  (builder `@angular/build:unit-test` + `@vitest/coverage-v8==4.1.11`) con
  umbrales por métrica en `angular.json` (`coverageThresholds`: statements 15 /
  branches 15 / functions 13 / lines 14).
- **Deuda crítica — cobertura CERO del asistente**: ningún test de
  `backend/tests/` referencia el asistente (0 matches de "assistant" en la
  suite). Esto **obliga characterization-first** (mandato afirmado) antes de
  descomponer `assistant_service.py`: congelar el comportamiento por seam con los
  fakes de `conftest.py` antes de mover una sola línea.

## Linting

- `backend/ruff.toml`: `target-version = py312`, `line-length = 100`,
  `select = ["E","F","I"]`, `ignore = ["E501","E402"]`. `[lint.per-file-ignores]`
  para `tests/**`/`conftest.py` y para los god-files:
  `assistant_service.py` → `["I001"]`; `data_manager_v2.py` →
  `["E722","F841","F401","I001"]`; `data_sync_service.py` → `["F401","I001"]`;
  `photo_service.py` → `["E722","F841"]`.
- `ruff check` **ya es bloqueante** en ambos gates; `ruff format` NO lo corre la
  reviewer. Implicación para el intent: formatear SOLO ficheros nuevos (no en
  masa) al crear `assistant/`, para no invalidar el pase de revisión en vuelo ni
  romper el gate.
- Frontend ESLint aún advisory (`continue-on-error`) — deuda diferida.

## CI/CD

- `.github/workflows/ci.yml` (PR → main, job `quality`, required status check).
- `.github/workflows/fly-deploy.yml` (push → main, job `verify` que replica el
  gate; luego `deploy-backend` → `deploy-frontend` → `smoke-test` contra
  `/health`, 5 reintentos HTTP 200).
- Checks bloqueantes: gitleaks `@v3` (unificado), `pytest --cov=app`,
  `ruff check`, `pip-audit` (entorno instalado + allowlist con caducidad),
  `npm audit --audit-level=high`, `ng test`.
- Crons de coste ~0: `daily-sync.yml`, `sofascore-sync.yml` (máquinas Fly
  one-shot).
- Restricción dura: coste 0 € (tiers gratuitos); un rojo nunca llega a
  producción.

## Calidad de documentación

- `README.md` completo (arquitectura, stack, endpoints, deploy).
- `docs/` extenso: `BACKLOG-plan-intents.md` (origen del intent), `DEPLOY.md`,
  `ROLLBACK.md`, `PROJECT_CONTEXT`.
- Docstrings de calidad en los paquetes DDD de referencia (`analytics/`,
  `prizes/`); los god-files carecen de esa disciplina.

## Deuda técnica (registro)

- **God-files** (NUNCA ampliar ni extender SQL-en-router; saneo quirúrgico solo):
  `data_manager_v2.py` (166 173 bytes), `data_sync_service.py` (84 591 bytes),
  `assistant_service.py` (51 681 bytes / 1158 líneas — objetivo del intent),
  `photo_service.py` (22 764 bytes).
- **SQL inline en la capa de servicio**: `assistant_service.py` contiene **42
  `cursor.execute`** con SQL crudo, concentrados en `ContextBuilder` (`_ctx_*`).
  Patrón que la Oleada 1 relocó tras `AnalyticsDataPort` (Protocol) + adaptador.
- **`except Exception` amplio / silencioso**: en `assistant_service.py` (p. ej.
  `_ctx_market_from_db`, `_save_market_to_db` con `except: return ""` /
  `logger.warning`); bare-except registrados como deuda (E722 en per-file-ignores
  de `data_manager_v2.py`/`photo_service.py`). Al reubicar, preservar el
  comportamiento (degradar, no romper).
- **`CREATE TABLE IF NOT EXISTS` en caliente** (esquema implícito, sin
  migraciones): `AssistantUsageTracker._ensure_table()` (`assistant_usage`);
  `_save_market_to_db` (`market_today`); el endpoint del asistente
  (`assistant_conversations`, verificado en `assistant.py`); y esquemas durables
  de auth/sesión/tarea al arranque en `main.py` (idempotentes, degradan a
  warning). El adaptador de infra debe preservar la idempotencia para no cambiar
  comportamiento observable.
- **Rangos de modelo LLM frágiles**: listas hardcodeadas
  (`["gemini-3.6-flash","gemini-3.5-flash"]`, `openai/gpt-oss-120b`) y
  formaciones hardcodeadas en `_ctx_formations`.
- **Pin de tooling frontend**: `vitest` en rango abierto `^4.0.8` frente al pin
  de su plugin `@vitest/coverage-v8==4.1.11` — asimetría de pin señalada.

## Postura de seguridad (direccionada)

- `JWT_SECRET` no-default obligatorio en arranque (NFR1.1; endurecido en
  `test_jwt_startup.py`).
- Nunca contraseña/token Futmondo en claro (memoria o BD) ni en
  mensaje/`repr`/`exc_info` de excepciones (reglas afirmadas); las excepciones de
  integración llevan modo de fallo + contexto no sensible.
- gitleaks escanea también los tests → los tests usan fakes/dobles, sin
  credenciales reales.
- Superficie pública intencional `/static/photos/*` documentada en `main.py`
  (FR7/NFR1.6): no colocar recursos sensibles bajo ese mount.
