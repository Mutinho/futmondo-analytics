# Reverse Engineering Timestamp — futmondo-analytics

- **Fecha del RE**: 2026-09-29
- **Commit hash**: `git:8ae4fe91841fcc8d76b1e5390e821b012f3a8a9b`
- **Intent**: `assistant-god-file` (Oleada 2 god-files, FR13 — `refactor`)
- **Tipo de escaneo**: rescaneo completo (`kind: full`) — reemplazo total de los
  9 artefactos, construyendo el bloque solo desde esta corrida.
- **Store previo**: STALE (se corrió el backstop de cobertura antes de publicar).

## Scope of Analysis

```yaml
scope_version: 1
kind: full
intent: assistant-god-file
fingerprint: 8ae4fe91841fcc8d76b1e5390e821b012f3a8a9b
analyzed:
  paths:
    - ./
    - backend/app/main.py
    - backend/app/core/config.py
    - backend/app/api/v1/endpoints/
    - backend/app/services/
    - backend/app/services/assistant_service.py
    - backend/app/services/analytics/
    - backend/app/services/analytics_service.py
    - backend/app/services/prizes/
    - backend/app/services/db_connection.py
    - backend/tests/
    - backend/pytest.ini
    - backend/ruff.toml
    - backend/requirements.txt
    - backend/conftest.py
    - .github/workflows/ci.yml
    - .github/workflows/fly-deploy.yml
    - angular-app/
    - README.md
    - docs/
  components:
    - backend-app-core
    - api-v1-endpoints
    - auth-jwt
    - assistant-service
    - services-analytics
    - services-prizes
    - data-manager-v2
    - data-sync-service
    - integration-clients
    - services-support
    - db-connection
    - stores-durable
    - frontend-angular-app
shallow:
  paths:
    - backend/scripts/
    - backend/app/auth/
    - backend/app/stores/
    - backend/app/security/
    - backend/app/models/
    - angular-app/src/app/features/
    - proxy/
    - cron/
    - docker-compose.yml
```
