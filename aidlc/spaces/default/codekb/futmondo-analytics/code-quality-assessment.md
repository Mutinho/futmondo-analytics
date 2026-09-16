# Code Quality Assessment — Futmondo Analytics

> Artefacto CodeKB (architect). Base: `developer-scan.md`. Store STALE tras FOCUSED SCAN del backend `backend/`. El backend refleja lo verificado en este run; la prosa del frontend y de CI/CD se preserva del análisis previo.

## Cobertura de tests

- **Backend** (verificado este run): `backend/tests/` con 7 ficheros — `test_auth_characterization.py`, `test_jwt_startup.py`, `test_db_admin_guard.py`, `test_db_engine_characterization.py`, `test_finance_characterization.py`, `test_analytics_service.py`, `test_sofascore_sync_characterization.py` — + `conftest.py` (provee `clean_jwt_env`, fija `sys.path`). Runner `pytest` (`pytest.ini`: `testpaths = tests`, `pythonpath = .`; se ejecuta desde `backend/`), con `pytest-cov` presente pero **sin piso bloqueante** (activable con `--cov=app`). Sesgo characterization-first.
  - **Hueco crítico para el intent**: **no hay tests directos de `SessionStore` ni de `TaskManager`** — el estado en memoria (núcleo del intent) está sin cobertura. Antes de refactorizar hacia durabilidad conviene congelar comportamiento con tests de caracterización.
  - **Guard de arranque JWT** ya endurecido y cubierto (`test_jwt_startup.py`, NFR1.1).
- **Frontend** (preservado): un único `.spec.ts` real (`auth.interceptor.spec.ts`), runner Vitest + jsdom vía `@angular/build:unit-test`; cobertura casi nula por `skipTests: true` en schematics.

## Linting y formato

- **Backend** (verificado este run): `ruff` (`backend/ruff.toml`, `select = [E, F, I]`, `ignore = [E501, E402, E722]`, `line-length = 100`, `target-version = py312`) — modo **advisory/tolerante** en CI (continue-on-error) por fase de saneamiento.
- **Frontend** (preservado): ESLint flat config (`typescript-eslint` + `angular-eslint`, reglas base a `warn`) — advisory; `prettier ^3.8.1`.

## CI/CD

> Preservado del análisis previo.

4 workflows en `.github/workflows/`:

| Workflow | Disparo | Contenido |
|----------|---------|-----------|
| `ci.yml` | PR→main | gitleaks (BLOQUEANTE), pytest+cobertura (BLOQUEANTE), test del frontend (BLOQUEANTE); ruff, ESLint, pip-audit, npm audit advisory |
| `fly-deploy.yml` | push→main | `verify` (pytest + test frontend) → `deploy-backend` → `deploy-frontend` → `smoke-test` contra `/health` |
| `daily-sync.yml` | cron 4:30 UTC | máquina Fly one-shot (coste ~0) |
| `sofascore-sync.yml` | cron 5:00 UTC | máquina Fly one-shot (coste ~0) |

Despliegue Fly.io on-merge; healthcheck `/health`.

## Calidad de documentación

- Docstrings de módulo/función presentes y descriptivos en el área auth/sync; OpenAPI automático de FastAPI en `/docs`.
- `README.md` raíz + `angular-app/README.md`; `docs/` extenso (`DEPLOY`, `ROLLBACK`, `PR-GATE`, `PROJECT_CONTEXT`, `REVERSE_ENGINEERING`, backlogs).
- **Señal de deuda documental**: el docstring de `_helpers.get_user_futmondo_client` menciona re-crear la sesión desde credenciales guardadas, pero el código real devuelve **403** tras un reinicio (las credenciales ya no existen). Divergencia comentario↔comportamiento a corregir.

## Deuda técnica del backend (foco del intent `260914-durabilidad-estado-y-cre`)

Verificado este run; evidencia y orden de remediación en `architecture.md` → ADR.

1. **Estado 100 % en memoria, no durable (FR1)** — `SessionStore` (`app/auth/session_store.py`) y `TaskManager` (`app/services/task_manager.py`) son singletons de proceso; un reinicio/redeploy en Fly.io los borra. La sesión Futmondo no se reconstruye (`_helpers` → 403); una tarea de sync en curso queda huérfana (hilo daemon muerto), sin persistencia ni idempotencia. `fly.toml` fija `min=max=1`: oculta el problema multi-instancia pero no el de reinicio. **Núcleo del intent.**
2. **Credenciales Futmondo en claro en memoria (FR5)** — `UserSession` guarda `email`/`password` en texto plano. Deuda de seguridad central: cualquier diseño de durabilidad debe cifrar en reposo o evitar guardar el `password`, y **no** reintroducir el patrón en BD.
3. **`/auth/refresh` no reconstruye la sesión Futmondo** — renueva el access JWT pero deja al usuario con 403 en endpoints que usan el cliente Futmondo hasta re-login.
4. **Migraciones ad-hoc sin versionado** — `token_store.init_auth_tables()` con `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE` en `try/except: pass`; sin herramienta tipo Alembic. Riesgo al evolucionar el esquema (p. ej. para persistir sesión/estado).
5. **`except Exception: pass` en varios puntos** (migraciones, auto-detección de campeonatos) — enmascara fallos.
6. **Posible bug de precedencia** en la comparación de expiración de `is_refresh_token_valid` (ternaria sin paréntesis) — revisar.
7. **`__import__(...)` dinámico de `get_db` en `refresh`** — acoplamiento oculto; sustituir por import estático.
8. **Divergencia de runtime Python** 3.12 (Docker) vs 3.11 (Nixpacks) — normalizar si el diseño toca dependencias.

## Consideraciones transversales (steering activo)

- **Coste 0 €**: la durabilidad debe apoyarse en Neon (ya disponible) o Turso (alternativa), sin introducir servicios de pago (p. ej. Redis). Respetar tiers gratuitos Neon/Fly.io/GitHub Actions.
- **No asumir instancia única**: aunque `fly.toml` fije 1 máquina, el diseño debe soportar reinicio y potencial escalado.
- **Characterization-first**: congelar comportamiento de `SessionStore`/`TaskManager` antes de refactorizar.

## Deuda técnica fuera del foco (preservada del análisis previo)

- Ejes del bundle inicial del frontend (Chart.js/ng2-charts eager, `marked` eager, `PreloadAllModules`, budget relajado) — detalle en el historial del store y en `architecture.md`.
- `libsql-experimental==0.0.55` y `nixpacks.toml` (Railway) parecen restos previos; confirmar si siguen vivos.
- Señal de seguridad (frontend, fuera de scope): `ng build` de producción usa `NODE_TLS_REJECT_UNAUTHORIZED=0`.

## Referencias cruzadas

- Versiones afectadas: `technology-stack.md`.
- Relaciones de dependencia impactadas: `dependencies.md`.
- Flujos y ADR de durabilidad: `architecture.md`.
