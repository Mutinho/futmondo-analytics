# Evaluación de Calidad del Código — futmondo-analytics

## Cobertura de Tests, Linting y CI/CD

### Tests

- **Backend**: `pytest` + `pytest-cov`, ejecutado desde `backend/` (`pytest.ini`:
  `testpaths=tests`, `pythonpath=.`). **Sin piso de cobertura bloqueante** — no existe
  `cov-fail-under`/`fail_under`/`coverageThreshold` (ratcheting diferido, decisión de equipo).
- **Frontend**: specs `*.spec.ts` con `ng test` (Vitest + jsdom vía
  `@angular/build:unit-test`).
- **Cobertura existente relevante a las FR**:
  - **FR18**: `test_db_admin_guard.py` — 404 por defecto, 404 con valor no-afirmativo, 200
    con `ENABLE_DB_ADMIN=1` (con doble de `DataManagerV2`). Guarda ya cubierta.
  - **FR9**: `test_auth_characterization.py` — **caracteriza el bug** de
    `is_refresh_token_valid` (token aware futuro → `False` erróneo; naive futuro → `True`).
    Deberán actualizarse deliberadamente al corregir FR9.
  - **NFR1.1** (contexto): `test_jwt_startup.py` cubre `resolve_jwt_secret`.
  - **Huecos**: sin cobertura directa de `place_bid` (FR6) ni de la exposición de `/photos`
    (FR7); FR8 no tiene test (es configuración).

### Linting

- **Backend**: `ruff` (`backend/ruff.toml`: `select=["E","F","I"]`,
  `ignore=["E501","E402","E722"]`, `line-length=100`) — **advisory** en CI
  (`continue-on-error`).
- **Frontend**: ESLint flat config — **advisory**.

### CI/CD

- **`.github/workflows/ci.yml`** (PR→main): **gitleaks + pytest + ng test BLOQUEANTES**;
  ruff/ESLint/pip-audit/npm audit advisory.
- **`.github/workflows/fly-deploy.yml`** (push→main): job `verify` (gitleaks + pytest **sin
  `--cov`** + ng test) → deploy backend → deploy frontend → smoke `/health` (5 reintentos).
- **Crons**: `daily-sync.yml` (04:30 UTC), `sofascore-sync.yml` (05:00 UTC) — máquinas Fly
  one-shot (coste ~0).

### Documentación

- README extenso; `docs/DEPLOY.md`, `docs/ROLLBACK.md`, `docs/PR-GATE.md`. Docstrings en
  inglés; texto de usuario / `HTTPException.detail` en castellano.

## Deuda Técnica y Hallazgos (por FR)

Este artefacto es el propietario del detalle de deuda; el resto de artefactos referencian
aquí en lugar de repetir.

- **FR6 — validación de puja ausente en backend** (`api/v1/endpoints/market.py::place_bid`):
  acepta `price: int = Query(...)` sin validar rango/positividad y proxya directo a Futmondo.
  La única validación (min = valor de mercado, max = puja máxima, `> 0`) vive en
  `angular-app/.../bid-dialog.component.ts` (frontend), evadible llamando la API directamente.
- **FR7 — exposición del endpoint de fotos**: `GET /api/v1/photos/{player_id}` (definido en
  `main.py`) NO está en `AUTH_EXCLUDED_PATHS`, así que el middleware SÍ exige Bearer (no es
  público). El punto de atención real es `/static/photos/*` (StaticFiles), que queda fuera
  del prefijo protegido; las redirecciones 302 del endpoint apuntan ahí. Trabajo probable:
  documentar/confirmar la intención (¿debe servir `<img>` sin token?) más que cambiar código.
- **FR8 — `SSL_VERIFY=0` huérfano**: declarado en `docker-compose.yml` (local) pero sin
  lector en Python (0 usos en `backend/**`); ausente de `backend/fly.toml [env]`. Hoy inocuo
  (nadie lo consume) pero no aislado/documentado de forma inequívoca.
- **FR9 — bug de precedencia naive/aware** en `token_store.is_refresh_token_valid`
  (confirmado en fuente):
  `if expires_at and datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc) if expires_at.tzinfo is None else expires_at:`.
  Con `expires_at` aware (caso real PostgreSQL/Turso), el ternario evalúa el `else` y
  devuelve el propio `datetime` (truthy) → `return False`, **rechazando tokens ACTIVOS
  futuros**. La corrección exige actualizar los tests de caracterización que hoy congelan el
  fallo.
- **FR18 — guarda de administración**: `_require_db_admin()`/`ENABLE_DB_ADMIN` ya correcta y
  testeada; sólo reforzar/consolidar cobertura si el diseño lo pide.

### Deuda estructural (no ampliar)

- **SQL crudo disperso** en `auth/token_store.py`, `routes._auto_detect_championships`,
  `_helpers.get_championship_config` sin capa repositorio; nueva persistencia debe ir tras
  la capa estrecha `stores/`.
- **God-files** en `services/`: `data_manager_v2.py` (~166 KB), `data_sync_service.py`
  (~84 KB), `assistant_service.py` (~51 KB). No deben crecer.
- **Imports dinámicos** dentro de funciones (p. ej. `import requests` en `get_player_photo`);
  preferir import estático (convención del equipo).

### Riesgos de contexto

- El job `verify` de `fly-deploy.yml` corre `pytest -q` **sin `--cov`** (sí con gitleaks); no
  es idéntico al gate de PR pero es defensa en profundidad (relevante a FR5, fuera de este
  intent).
- `libsql-experimental==0.0.55` sólo compila en Python 3.12 (los tests usan fakes SQLite).
- Restricción dura de coste 0 € en toda propuesta.
