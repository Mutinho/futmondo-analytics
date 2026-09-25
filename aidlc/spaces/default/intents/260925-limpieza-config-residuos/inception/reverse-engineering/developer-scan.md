# Developer Scan — Handoff (LINK 1, reverse-engineering)

Intent: `260925-limpieza-config-residuos` · Scope `refactor` · Profundidad Minimal · Proyecto BROWNFIELD en producción.
Breadth: RESCAN COMPLETO de la raíz del workspace (excluyendo `aidlc/`, `node_modules`, `.git`, `dist`, `build`).

> Nota Minimal: cada inventario se registra una vez en su sección dueña; el resto cross-referencia. La atención especial va a la deuda de config/residuos (FR14/FR15).

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply** (dentro de `./`):
  - `backend/app/core/config.py` — resolución de tipo de BD y secretos.
  - `backend/app/core/constants.py` — IDs hardcodeados y catálogo de equipos.
  - `backend/app/services/db_connection.py` — manager multi-backend SQLite/PostgreSQL/Turso.
  - `backend/app/main.py` — app FastAPI, middleware auth, montaje de routers y estáticos.
  - `backend/nixpacks.toml`, `backend/entrypoint.sh`, `backend/Dockerfile`, `backend/fly.toml`, `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`, `backend/conftest.py`.
  - `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`.
  - `docker-compose.yml`, `angular-app/nginx.prod.conf`, `angular-app/package.json`, `angular-app/angular.json`, `.gitignore`, `.nvmrc`.
  - `backend/scripts/migrate_data_to_turso.py`, `backend/scripts/migrate_to_turso.py` (cabeceras/propósito).
- **Skimmed only** (directorio, sin lectura profunda):
  - `backend/app/api/v1/endpoints/` (24 routers — inventario de superficie por nombre/prefijo desde `main.py`).
  - `backend/app/services/` (god-files `data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB, `assistant_service.py`, `analytics_service.py`; NO ampliar — regla afirmada).
  - `backend/app/auth/`, `backend/app/stores/`, `backend/app/security/`, `backend/app/models/`.
  - `angular-app/src/app/` (frontend Angular 22; no relevante al alcance FR14/FR15 salvo doble prefijo consumido).
  - `docs/`, `proxy/`, `cron/`, `.github/workflows/daily-sync.yml`+`sofascore-sync.yml`.

### Packages Found

- `backend/app/` — FastAPI (Python 3.12): subpaquetes `core` (config/constants), `services` (lógica de negocio + integraciones), `api/v1/endpoints` (routers HTTP), `auth` (JWT + token/session store), `stores` (repositorios durables task/session), `security` (protección de credenciales), `models`.
- `backend/scripts/` — utilidades one-shot (sync, export, migraciones Turso, init_db).
- `angular-app/` — SPA Angular 22 (PWA), servida por nginx en producción.
- `proxy/`, `cron/` — nginx reverse proxy local y app Fly.io de crons.

### Build System

- **Backend**: Docker (`backend/Dockerfile`, base `python:3.12-slim`) → despliegue Fly.io (`backend/fly.toml`, región `cdg`, check `/health`). Dependencias en `requirements.txt` (rangos abiertos salvo `libsql-experimental==0.0.55`, `PyJWT==2.9.0`, `google-genai`, `groq` pinneados).
- **Frontend**: Angular CLI 22 (`@angular/build:application`), Node fijado en `.nvmrc` = `22.22.3`; deploy Fly.io.
- **Orquestación local**: `docker-compose.yml` (proxy + backend + frontend).
- **Residuo de build no usado**: `backend/nixpacks.toml` — config de Railway/Nixpacks (`python311`), incoherente con Python 3.12 real y con Fly.io/Docker. Ver Deuda Técnica.

### APIs Discovered

- **API interna (REST, FastAPI)** — 24 routers montados en `main.py` bajo `/api/v1/*` (auth vía `AuthMiddleware`, Bearer JWT); públicos: `/`, `/health`, `/auth/*`, `/static/photos/*`, `/docs`. Endpoints principales: sync, market, balances, analytics, player-finances, roster, transactions, favorites, sofascore, assistant, championships, matchdays, user.
- **API externa consumida**: Futmondo API (`futmondo_client.py`), Sofascore (`sofascore_client.py`, curl_cffi). Gemini/Groq para el assistant.
- **Contrato de errores de integración**: módulo `integration_errors.py` (raíz `IntegrationError`, excepciones tipadas propagadas — FR4 previo).

### Frameworks & Libraries

- Backend: FastAPI, uvicorn[standard], pydantic v2, PyJWT 2.9.0, psycopg2-binary, curl_cffi, libsql-experimental 0.0.55, google-genai, groq, python-dotenv. (Detalle de versiones en `backend/requirements.txt`.)
- Frontend: Angular 22.1.x, Angular Material 22, chart.js 4.5 + ng2-charts 10, marked 18, rxjs 7.8. (Detalle en `angular-app/package.json`.)

### Test Coverage

- **Test Directories**: `backend/tests/` (≈28 ficheros pytest, characterization-first). Frontend: specs en `angular-app/src/app/`.
- **Test Frameworks**: pytest + pytest-cov (backend, fixtures en `conftest.py`: `_FakeInMemoryDB`/`_FakeCursor` SQLite `:memory:`, `clean_jwt_env`, `fake_db` — sin red/BD real/credenciales). Frontend: Vitest vía `@angular/build:unit-test` + `@vitest/coverage-v8` 4.1.11 (pin).
- **Coverage Config**: backend `--cov=app` observability-only (SIN `cov-fail-under`); frontend con umbrales por métrica en `angular.json` (statements 15 / branches 15 / functions 13 / lines 14, trinquete). Asimetría conocida: `ci.yml` mide `--cov`, `fly-deploy.yml verify` corre `pytest -q` sin `--cov` (deuda diferida afirmada).

### Code Quality Indicators

- **Linting**: backend `ruff` (`backend/ruff.toml`, `select=["E","F","I"]`, `ignore=["E501","E402"]` — `E722` ya re-habilitado como advisory), advisory en CI. Frontend ESLint (`eslint.config.js`) advisory. Prettier (`.prettierrc`).
- **CI/CD**: `ci.yml` (PR→main): gitleaks + pytest + ng test BLOQUEANTES; ruff/ESLint/pip-audit/npm-audit advisory. `fly-deploy.yml` (push→main): job `verify` (gitleaks+pytest+ng test) → deploy-backend → deploy-frontend → smoke `/health`.
- **Documentación**: `README.md`, `docs/` (DEPLOY, ROLLBACK, PR-GATE, PROJECT_CONTEXT, varios BACKLOG y planes históricos).

### Technical Debt Signals

Foco del intent (FR14/FR15), con evidencia:

- **FR14 — Ramas muertas SQLite/Turso vs Neon**:
  - `config.py`: resolución en cascada `DATABASE_URL`(PostgreSQL) → `TURSO_DATABASE_URL`(turso) → fallback `sqlite`; expone `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`, `POSTGRES_*` manuales. Producción usa Neon (PostgreSQL) — las ramas Turso/SQLite están vivas en código pero muertas en operación.
  - `db_connection.py`: `_init_turso()` (libsql embedded replica), `_TursoCursorWrapper`, `_init_sqlite()`, y ramas `turso`/`sqlite` en `get_connection`/`adapt_sql`/`adapt_params`/`get_last_insert_id`/`sync`. Comentarios "Railway" obsoletos (proyecto está en Fly.io).
  - `requirements.txt`: `libsql-experimental==0.0.55` (no compila fuera de 3.12; no lo ejercitan los tests — usan fake SQLite).
  - `backend/nixpacks.toml`: config Railway/Nixpacks huérfana (deploy real es Docker+Fly.io); `python311` incoherente con 3.12.
  - `backend/scripts/migrate_to_turso.py` (14 KB) y `backend/scripts/migrate_data_to_turso.py` (5 KB): scripts de migración a Turso, sin uso en el flujo Neon actual.
  - `backend/entrypoint.sh`: arranca `cron` + uvicorn duplicando el `CMD` del Dockerfile; no referenciado por Dockerfile ni fly.toml (candidato a residuo).
- **FR14 — IDs hardcodeados en `constants.py`/`config.py`**: `CHAMPIONSHIP_ID` y `LEAGUE_ID` tienen DEFAULTS hardcodeados en `config.py` (no en `constants.py`; el nombre real del fichero difiere del enunciado). App es multi-usuario/multi-campeonato → estos defaults globales son residuo de la etapa mono-usuario. `constants.py` sí contiene el catálogo estático `LALIGA_TEAMS` (legítimo fallback, no residuo).
- **FR15 — Doble montaje de `matchdays`**: confirmado en `main.py` — el mismo router se incluye DOS veces: `prefix="/api/v1/matchdays"` y `prefix="/v1/matchdays"` (comentario "avoid redirect loops"). Superficie duplicada a unificar.
- **FR15 — Artefactos basura versionados** (raíz del repo, owner=root varios):
  - `*.jpg:Zone.Identifier` (marcadores NTFS de Windows): `42874.jpg:Zone.Identifier`, `30825.jpg:Zone.Identifier`, `IMG_9904.PNG:Zone.Identifier`; imágenes sueltas `42874.jpg` (≈580 KB).
  - Directorios `stitch_team_card_dashboard/` y `stitch_angular_material_card_redesign/` (mockups HTML+PNG de diseño, ≈370 KB).
  - `angular-app/node_modules.old-1789382239/` (backup de node_modules; ya cubierto por `.gitignore` `node_modules.old-*/`, verificar si está trackeado).
  - `backend/futmondo_data.db` (SQLite local; `.gitignore` ignora `*.db`, verificar tracking histórico).
- **God-files (NO ampliar — regla afirmada)**: `data_manager_v2.py` ~166 KB, `data_sync_service.py` ~84 KB, `assistant_service.py` ~51 KB. Fuera del alcance de este intent salvo lectura de contexto.
- **Otros**: comentarios "Railway" obsoletos dispersos en `config.py`/`db_connection.py`/`docker-compose.yml` (menciona "Turso"); `.env` presente en el árbol de trabajo (ignorado por `.gitignore`, no leído).

## Handoff Summary

- **Intent-relevant finding**: Las ramas SQLite/Turso son un dead-path operativo completo y aislado (`config.py` cascada + `db_connection.py` `_init_turso`/`_init_sqlite`/`_TursoCursorWrapper` + `libsql-experimental` + `nixpacks.toml` + 2 scripts `migrate_*to_turso` + `entrypoint.sh`), mientras producción corre solo Neon PostgreSQL vía `DATABASE_URL`. El doble montaje de `matchdays` está en `main.py` (dos `include_router` con prefijos `/api/v1/matchdays` y `/v1/matchdays`). Los IDs hardcodeados a limpiar (`CHAMPIONSHIP_ID`/`LEAGUE_ID`) están realmente en `config.py`, no en `constants.py` (el enunciado FR14 nombra el fichero equivocado).
- **Risks / follow-up**:
  - Eliminar la rama Turso/SQLite exige verificar que ningún llamador de `db_connection` dependa de `adapt_params`/`adapt_sql` con `?` (SQLite) en producción Neon; caracterizar (characterization-first) antes de tocar `db_connection.py` para no alterar el contrato del cursor bajo PostgreSQL.
  - `test_db_engine_characterization.py` y el `fake_db` de `conftest.py` usan `db_type="sqlite"` deliberadamente: retirar SQLite del código de producción NO debe romper el doble de test (es un fake in-memory, no la rama de producción) — confirmar la separación antes de borrar.
  - Quitar el segundo montaje `/v1/matchdays` puede romper clientes que aún llamen a esa ruta legacy: verificar consumo en el frontend/Sofascore antes de retirarlo.
  - Retirar `libsql-experimental` de `requirements.txt` es coherente con coste 0 € y con el learning ya afirmado (no compila fuera de 3.12); confirmar que no queda import vivo tras eliminar `_init_turso`.
  - Confirmar el estado de tracking en git de los artefactos basura (`.gitignore` ya cubre `*.db`, `node_modules.old-*/`); los `:Zone.Identifier`, `stitch_*` e imágenes sueltas NO están cubiertos y requieren `git rm` explícito.
