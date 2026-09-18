# Timestamp de Ingeniería Inversa — futmondo-analytics

## Registro del Análisis

- **Fecha**: 2026-09-18
- **Commit**: git:ca0b151d893b0f4ef7ac543739e98f3ed7779779
- **Intent**: `260918-matchday-prizes-calc` (scope `classic`, depth Standard)
- **Tipo de scan**: focused scan sobre un store EXISTENTE con veredicto **STALE**. Se
  actualizó/extiende el área de premios/finanzas y se preservó la prosa previa (área de
  seguridad del intent `260916-backend-security-hardeni`).
- **Enfoque**: cálculo de premios de jornada (matchday prizes). La fórmula real vive en
  `data_sync_service.sync_prizes()` (god-file fuera del snapshot de deep-scan); los endpoints
  de finanzas/saldos sólo leen/suman la tabla `team_prizes`.

## Cómo Leer Este Registro

El bloque `## Scope of Analysis` de abajo es leído por `codekb-scope-diff` en el siguiente
rerun; su exactitud decide si un intent futuro puede reusar la cobertura verificada o debe
mezclarla/reemplazarla. Los nombres bajo `analyzed.components` coinciden verbatim con los
encabezados de `component-inventory.md`.

Como el store previo estaba **STALE**, `analyzed.paths`/`analyzed.components` recogen SOLO lo
verificado en profundidad en ESTE run (área de premios/finanzas), en `kind: partial`. La
cobertura profunda del run anterior (que no pudo re-verificarse) se DEGRADA a `shallow.paths`
junto con los shallow previos y los nuevos skimmed reportados por el developer.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 260918-matchday-prizes-calc
fingerprint: beef86c6baa7e7a137c7b71538ffc8b8007e736e
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
    - angular-app/src/app/features/
  components:
    - backend-app-api-endpoints
    - backend-app-services
    - angular-app
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
    - angular-app/src/app/features/market/bid-dialog.component.ts
    - docker-compose.yml
    - backend/fly.toml
    - .env.example
    - .github/workflows/ci.yml
    - .github/workflows/fly-deploy.yml
    - backend/requirements.txt
    - backend/ruff.toml
    - angular-app/package.json
    - backend/tests/test_db_admin_guard.py
    - backend/tests/test_jwt_startup.py
    - backend/tests/test_auth_characterization.py
    - backend/app/services/
    - backend/app/stores/
    - backend/app/models/
    - backend/app/security/
    - backend/app/api/v1/endpoints/
    - angular-app/src/app/
    - backend/scripts/
    - backend/static/photos/players/
    - proxy/
    - cron/
    - docs/
    - .kiro/
    - aidlc/
```
