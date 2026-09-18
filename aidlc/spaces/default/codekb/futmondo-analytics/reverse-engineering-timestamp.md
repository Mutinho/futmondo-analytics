# Timestamp de Ingeniería Inversa — futmondo-analytics

## Registro del Análisis

- **Fecha**: 2026-09-16
- **Commit**: git:51a9fd26b1befefde15cbd2040ba574e08a98d3b
- **Intent**: `260916-backend-security-hardeni` (scope `security-patch`, depth Minimal)
- **Tipo de scan**: full rescan (reemplazo completo de los 9 artefactos del CodeKB).
- **Enfoque**: hardening de seguridad del backend FastAPI (FR6, FR7, FR8, FR9, FR18); las
  áreas de negocio y de durabilidad se cubrieron a nivel directorio (shallow) por scope.

## Cómo Leer Este Registro

El bloque `## Scope of Analysis` de abajo es leído por `codekb-scope-diff` en el siguiente
rerun; su exactitud decide si un intent futuro puede reusar la cobertura verificada o debe
mezclarla/reemplazarla. Los nombres bajo `analyzed.components` coinciden verbatim con los
encabezados de `component-inventory.md`. La línea `fingerprint:` queda como
`PENDING_CONDUCTOR_MINT`: el conductor la sustituye por el valor minteado sobre el
`analyzed.paths` final antes de publicar.

## Scope of Analysis

```yaml
scope_version: 1
kind: full
intent: 260916-backend-security-hardeni
fingerprint: 51a9fd26b1befefde15cbd2040ba574e08a98d3b
analyzed:
  paths:
    - ./
    - backend/app/main.py
    - backend/app/core/config.py
    - backend/app/core/constants.py
    - backend/app/auth/token_store.py
    - backend/app/auth/session_store.py
    - backend/app/auth/routes.py
    - backend/app/api/v1/endpoints/market.py
    - backend/app/api/v1/endpoints/reset_db.py
    - backend/app/api/v1/endpoints/_helpers.py
    - angular-app/src/app/features/market/bid-dialog.component.ts
    - docker-compose.yml
    - backend/fly.toml
    - .env.example
    - .github/workflows/ci.yml
    - .github/workflows/fly-deploy.yml
    - backend/requirements.txt
    - backend/pytest.ini
    - backend/ruff.toml
    - angular-app/package.json
    - backend/tests/test_db_admin_guard.py
    - backend/tests/test_jwt_startup.py
    - backend/tests/test_auth_characterization.py
  components:
    - backend-app-main
    - backend-app-auth
    - backend-app-api-endpoints
    - backend-app-core
    - backend-app-services
    - backend-app-stores
    - backend-app-security
    - angular-app
    - proxy-nginx
    - cron-worker
shallow:
  paths:
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
