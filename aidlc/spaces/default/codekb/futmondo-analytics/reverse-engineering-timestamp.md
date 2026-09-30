# Reverse Engineering Timestamp

- **Fecha**: 2026-09-29
- **Intent**: `sync-god-file`
- **Tipo de escaneo**: FULL RESCAN (reemplazo total de los 9 artefactos).
- **Repo**: `futmondo-analytics` (raíz del workspace = codebase).
- **Commit / source fingerprint**: `git:e29abff624ef852aa6002d0d367bfc56a0fa21ca`
- **Cobertura**: el escaneo cubrió `./` en profundidad (kind: full); áreas
  skimmed listadas abajo. Detalle en la sección `Scan Coverage` del handoff del
  desarrollador.

## Scope of Analysis

```yaml
scope_version: 1
kind: full
intent: sync-god-file
fingerprint: e29abff624ef852aa6002d0d367bfc56a0fa21ca
analyzed:
  paths:
    - ./
    - backend/app/services/data_sync_service.py
    - backend/app/services/prizes/
    - backend/app/services/analytics/
    - backend/app/services/assistant_service.py
    - backend/app/services/analytics_service.py
    - backend/app/api/v1/endpoints/sync.py
    - backend/pytest.ini
    - backend/ruff.toml
    - backend/requirements.txt
    - backend/conftest.py
    - .github/workflows/ci.yml
    - angular-app/package.json
    - README.md
  components:
    - backend-fastapi-app
    - api-v1-routers
    - auth-jwt
    - data-sync-service
    - prizes-context
    - analytics-context
    - assistant-context
    - data-manager-v2
    - external-integration-clients
    - services-layer (otros)
    - angular-frontend
    - infra-proxy-cron-ci
shallow:
  paths:
    - backend/app/
    - backend/app/services/
    - backend/tests/
    - backend/scripts/
    - angular-app/src/app/
    - .github/workflows/
    - proxy/
    - docs/
    - cron/
    - scripts/
```
