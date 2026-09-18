# Evaluación de Calidad del Código — futmondo-analytics

## Cobertura de Tests, Linting y CI/CD

### Tests

- **Backend**: `pytest` + `pytest-cov`, ejecutado desde `backend/` (`pytest.ini`:
  `testpaths=tests`, `pythonpath=.`). **Sin piso de cobertura bloqueante** — no existe
  `cov-fail-under`/`fail_under`/`coverageThreshold` (ratcheting diferido, decisión de equipo).
- **Frontend**: specs `*.spec.ts` con `ng test` (Vitest + jsdom vía
  `@angular/build:unit-test`).
- **Cobertura existente relevante al área de premios/finanzas (intent activo)**:
  - `test_finance_characterization.py` — **caracteriza el CONSUMO**:
    `player_finances.get_player_finances` (fórmula agregada, orden desc, lectura de
    `team_prizes`, budget por defecto 200M, 500 en error) con doble de `DataManagerV2` +
    `get_db` falso.
  - `test_analytics_service.py` — caracteriza `AnalyticsService` (trends, form, value-trend,
    clause-network, streaks, projections) con `StubDM`.
  - **GAP CRÍTICO (bloquea el intent)**: NO existe ningún test que caracterice la
    **PRODUCCIÓN** del premio, es decir `data_sync_service.sync_prizes()`: ratios de ranking
    flop/top, gating por ronda completa (`round_fully_played`), MVP, dream-team, pseudo-jornada
    negativa y la limpieza defensiva `DELETE ... NOT IN`. `balances` y `matchdays` tampoco
    tienen tests directos. `team.md` exige **characterization-first antes de refactor**: hay
    que congelar el comportamiento (incl. bugs) de `sync_prizes` antes de tocarlo.
- **Cobertura existente relevante a intents anteriores (security)**:
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
  inglés; texto de usuario / `HTTPException.detail` en castellano. `sync_prizes` está bien
  comentado (explica el porqué de la pseudo-jornada negativa y el gating), pese a vivir en un
  god-file.

## Deuda Técnica y Hallazgos

Este artefacto es el propietario del detalle de deuda; el resto de artefactos referencian
aquí en lugar de repetir.

### Área de premios/finanzas (intent activo)

- **Fórmula de premios en un god-file** (`services/data_sync_service.py::sync_prizes`,
  ~1577-1885, dentro de ~84 KB): toda la lógica monetaria de negocio (points/ranking/mvp/
  dream-team, gating, pseudo-jornadas, limpieza defensiva) vive embebida con SQL crudo y
  llamadas a la API de Futmondo intercaladas con `time.sleep()`. Es el punto de intervención
  del intent; debe extraerse tras una capa/función estrecha testeable, **sin ampliar** el
  god-file ni el patrón SQL-en-router (`project.md`).
- **Ausencia de red de caracterización** de `sync_prizes` (ver Tests): el núcleo del intent
  no está congelado. Riesgo alto de regresión al refactorizar sin caracterizar primero.
- **Doble semántica de "puntos"**: coexisten "puntos" como métrica de rendimiento y
  `points_prize` como término monetario derivado (`round_points * money_per_point`). En
  `player_finances`, verificar el doble origen (budget vs premio) para no doblar ni omitir el
  término de puntos. A aclarar en diseño.
- **Resolución de identidad frágil** en `player_finances`: múltiples lookups por
  team_id/user_id/nombre (normalización a lower) con fallback por coincidencia de nombre —
  riesgo de doble conteo/omisión de ajustes.
- **SQL inline en routers de analítica/saldos** (`balances.py`, `analytics.py`:
  classification-full, watchlist): mismo anti-patrón marcado como deuda a no ampliar.
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
  truthy → `return False`, **rechazando tokens ACTIVOS futuros**. Corrección exige actualizar
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
