# Reverse Engineering — Timestamp

- **Fecha del análisis**: 2026-09-27T09:39:04Z
- **Commit hash**: `2d10cd6b2a6aa0f40198993f7649cbb1e4d66990`
- **Intent**: `260927-god-files-refactor` (scope `refactor`, profundidad Minimal)
- **Repositorio**: `futmondo-analytics`
- **Modo**: FOCUSED SCAN (`kind: partial`) — merge sobre store existente de
  verdict UNVERIFIED. Se actualizan/extienden las secciones que cubren los 4
  god files re-analizados y se PRESERVA la prosa previa fuera de esa área.
- **Tipo de proyecto**: Brownfield (en producción).

Este run leyó en profundidad los cuatro god files de la capa de servicios
(`data_manager_v2.py`, `data_sync_service.py`, `assistant_service.py`,
`analytics_service.py`) para identificar responsabilidades/dominios mezclados,
seams de extracción candidatos, superficie pública a preservar y cobertura de
tests actual (material para el plan de descomposición, FR13). La cobertura
profunda del store previo (intent `260925-limpieza-config-residuos`) **no se
pudo re-verificar en este run** y se degrada a `shallow`. Detalle de cobertura
en el bloque siguiente.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 260927-god-files-refactor
fingerprint: 46b55b2f6e9042914b3fdeb2ad2b820ce10209ae
analyzed:
  paths:
    - backend/app/services/data_manager_v2.py
    - backend/app/services/data_sync_service.py
    - backend/app/services/assistant_service.py
    - backend/app/services/analytics_service.py
  components:
    - services
shallow:
  paths:
    - backend/app/core/config.py
    - backend/app/core/constants.py
    - backend/app/services/db_connection.py
    - backend/app/services/data_initializer.py
    - backend/app/services/data_initializer_v2.py
    - backend/app/services/prizes/
    - backend/app/services/integration_errors.py
    - backend/app/services/sync_step_status.py
    - backend/app/services/futmondo_client.py
    - backend/app/main.py
    - backend/nixpacks.toml
    - backend/entrypoint.sh
    - backend/Dockerfile
    - backend/fly.toml
    - backend/requirements.txt
    - backend/pytest.ini
    - backend/ruff.toml
    - backend/conftest.py
    - backend/scripts/migrate_data_to_turso.py
    - backend/scripts/migrate_to_turso.py
    - backend/app/api/v1/endpoints/
    - backend/app/auth/
    - backend/app/stores/
    - backend/app/security/
    - backend/app/models/
    - backend/tests/
    - .github/workflows/ci.yml
    - .github/workflows/fly-deploy.yml
    - .github/workflows/daily-sync.yml
    - .github/workflows/sofascore-sync.yml
    - docker-compose.yml
    - angular-app/nginx.prod.conf
    - angular-app/package.json
    - angular-app/angular.json
    - angular-app/src/app/
    - docs/
    - proxy/
    - cron/
    - .gitignore
    - .nvmrc
```
