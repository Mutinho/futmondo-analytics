# Timestamp de Ingeniería Inversa — futmondo-analytics

## Registro del Análisis

- **Fecha**: 2026-09-18
- **Commit**: git:7a48bd3793c85e743eb94628e0d4b14f45998dbb
- **Intent**: `260918-frontend-coverage-gate` (scope `classic`, depth Standard)
- **Tipo de scan**: focused scan sobre un store EXISTENTE con veredicto **CURRENT** (store
  construido por el intent `260918-matchday-prizes-calc`, cobertura `partial`). Se
  actualizó/extiende el área de calidad del frontend Angular (`angular-app/`, tooling de
  test/cobertura) y del pipeline CI/CD (`.github/workflows/`), y se PRESERVÓ la prosa previa
  del área backend de premios/finanzas y seguridad.
- **Enfoque**: cobertura de tests del frontend (FR10) y significatividad de los tests del
  job `verify` del pipeline (FR17.1). El backend se recorrió sólo a nivel estructural (ya
  profundo en el store) para preservar/fusionar.

## Cómo Leer Este Registro

El bloque `## Scope of Analysis` de abajo es leído por `codekb-scope-diff` en el siguiente
rerun; su exactitud decide si un intent futuro puede reusar la cobertura verificada o debe
mezclarla/reemplazarla. Los nombres bajo `analyzed.components` coinciden verbatim con los
encabezados de `component-inventory.md`.

Como el store previo estaba **CURRENT**, `analyzed.paths`/`analyzed.components` recogen la
**UNIÓN** de lo verificado en profundidad por el store y por ESTE run, en `kind: partial`
(un store `partial` no puede reclamar `./`). El área backend de premios/finanzas (ya
profunda en el store) se PRESERVA en `analyzed.paths`; este run añade en profundidad
`angular-app/` y `.github/workflows/`. `angular-app/src/app/features/` del store queda
subsumido por el `angular-app/` más amplio de este run (se mantiene el directorio raíz de la
app, que cubre igualmente la cobertura previa de `features/`).

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 260918-frontend-coverage-gate
fingerprint: 7a48bd3793c85e743eb94628e0d4b14f45998dbb
analyzed:
  paths:
    - backend/app/api/v1/endpoints/player_finances.py
    - backend/app/api/v1/endpoints/matchdays.py
    - backend/app/api/v1/endpoints/analytics.py
    - backend/app/api/v1/endpoints/balances.py
    - backend/app/services/analytics_service.py
    - backend/app/models/models.py
    - backend/tests/test_analytics_service.py
    - backend/tests/test_finance_characterization.py
    - angular-app/
    - .github/workflows/
  components:
    - backend-app-api-endpoints
    - backend-app-services
    - angular-app
    - ci-workflow
    - fly-deploy-workflow
    - cron-sync-workflows
shallow:
  paths:
    - backend/app/services/data_sync_service.py
    - backend/app/api/v1/endpoints/_helpers.py
    - backend/pytest.ini
    - backend/tests/
    - backend/app/main.py
    - backend/app/core/config.py
    - backend/app/core/constants.py
    - backend/app/auth/token_store.py
    - backend/app/auth/session_store.py
    - backend/app/auth/routes.py
    - backend/app/api/v1/endpoints/market.py
    - backend/app/api/v1/endpoints/reset_db.py
    - docker-compose.yml
    - backend/fly.toml
    - .env.example
    - backend/requirements.txt
    - backend/ruff.toml
    - backend/tests/test_db_admin_guard.py
    - backend/tests/test_jwt_startup.py
    - backend/tests/test_auth_characterization.py
    - backend/app/services/
    - backend/app/stores/
    - backend/app/models/
    - backend/app/security/
    - backend/app/api/v1/endpoints/
    - backend/scripts/
    - backend/static/photos/players/
    - proxy/
    - cron/
    - docs/
    - .nvmrc
    - .kiro/
    - aidlc/
```
