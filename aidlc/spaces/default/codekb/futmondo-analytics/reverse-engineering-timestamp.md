# Timestamp de Ingeniería Inversa — futmondo-analytics

## Registro del Análisis

- **Fecha**: 2026-09-23
- **Intent**: `260923-backend-fiabilidad-error` (backend reliability: FR3.2 manejo de errores
  + FR4 contratos de integración; brownfield, depth Standard).
- **Tipo de scan**: focused scan sobre un store EXISTENTE con veredicto **STALE** (store
  construido por el intent `260918-frontend-coverage-gate`). Al estar STALE, la cobertura
  profunda previa NO se pudo re-verificar: se registra ÚNICAMENTE este run en
  `analyzed.paths`/`analyzed.components`, se PRESERVA la prosa previa fuera del área de
  fiabilidad, y las rutas antes analizadas por el store se DEMOTAN a `shallow.paths`.
- **Enfoque**: área de fiabilidad del backend FastAPI en `backend/` — manejo de excepciones,
  señalización recuperable-vs-fatal y puntos de escritura del camino de sync ("no corromper
  datos"). Se profundizó en `main.py`, `db_connection.py`, `sofascore_client.py`,
  `futmondo_client.py`, `data_sync_service.py` (región de premios en detalle; resto
  catalogado por conteo/localización de `except`), `sync_step_status.py`, `task_manager.py`,
  `task_service.py`, `backend/scripts/` y `backend/tests/`.

## Cómo Leer Este Registro

El bloque `## Scope of Analysis` de abajo es leído por `codekb-scope-diff` en el siguiente
rerun; su exactitud decide si un intent futuro puede reusar la cobertura verificada o debe
mezclarla/reemplazarla. Los nombres bajo `analyzed.components` coinciden verbatim con los
encabezados de `component-inventory.md`.

Como el store previo estaba **STALE**, `analyzed.paths`/`analyzed.components` recogen SÓLO lo
verificado en profundidad por ESTE run, en `kind: partial` (un bloque `partial` NO puede
reclamar `./`). Las rutas antes profundas del store (área de premios/finanzas del frontend y
del backend) se DEMOTAN a `shallow.paths` porque su cobertura profunda no se re-verificó en
este run. La prosa previa de esas áreas se PRESERVA en los 9 artefactos.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 260923-backend-fiabilidad-error
fingerprint: c1bd16d9faf51fb041c9ce8e82dd74eced029fd1
analyzed:
  paths:
    - backend/app/main.py
    - backend/app/services/db_connection.py
    - backend/app/services/sofascore_client.py
    - backend/app/services/futmondo_client.py
    - backend/app/services/data_sync_service.py
    - backend/app/services/sync_step_status.py
    - backend/app/services/task_manager.py
    - backend/app/services/task_service.py
    - backend/scripts/
    - backend/tests/
  components:
    - backend-app-main
    - backend-app-services
    - backend-app-stores
    - backend-app-api-endpoints
    - cron-worker
shallow:
  paths:
    - backend/app/api/v1/endpoints/player_finances.py
    - backend/app/api/v1/endpoints/matchdays.py
    - backend/app/api/v1/endpoints/analytics.py
    - backend/app/api/v1/endpoints/balances.py
    - backend/app/api/v1/endpoints/market.py
    - backend/app/api/v1/endpoints/reset_db.py
    - backend/app/api/v1/endpoints/sync.py
    - backend/app/api/v1/endpoints/_helpers.py
    - backend/app/api/v1/endpoints/
    - backend/app/services/analytics_service.py
    - backend/app/services/data_manager_v2.py
    - backend/app/services/photo_service.py
    - backend/app/services/
    - backend/app/models/models.py
    - backend/app/models/
    - backend/app/stores/
    - backend/app/auth/token_store.py
    - backend/app/auth/session_store.py
    - backend/app/auth/routes.py
    - backend/app/core/config.py
    - backend/app/core/constants.py
    - backend/app/security/
    - backend/pytest.ini
    - backend/ruff.toml
    - backend/requirements.txt
    - backend/fly.toml
    - backend/static/photos/players/
    - angular-app/
    - .github/workflows/
    - docker-compose.yml
    - .env.example
    - proxy/
    - cron/
    - docs/
    - .nvmrc
    - .kiro/
    - aidlc/
```
