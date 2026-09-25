# Reverse Engineering — Timestamp

- **Fecha del análisis**: 2026-09-25T10:14:30Z
- **Commit hash**: `1234e6807f821dcb79d386e0e7c808606155ccb0`
- **Intent**: `260925-limpieza-config-residuos` (scope `refactor`, profundidad Minimal)
- **Repositorio**: `futmondo-analytics`
- **Modo**: RESCAN COMPLETO (`kind: full`) — reemplazo total de los 9 artefactos.
- **Tipo de proyecto**: Brownfield (en producción).

El escaneo cubrió la raíz del workspace (excluyendo `aidlc/`, `node_modules`,
`.git`, `dist`, `build`), con lectura profunda de la config de BD, el manager
multi-backend, el montaje de routers y la superficie de build/CI, y lectura de
superficie (skim) de los routers HTTP, la capa de servicios (god-files), el
frontend Angular y los directorios de docs/proxy/cron. Detalle de cobertura en
el bloque siguiente.

## Scope of Analysis

```yaml
scope_version: 1
kind: full
intent: 260925-limpieza-config-residuos
fingerprint: 901affb69e2ae83d3759996b7b907ee10e489a2c
analyzed:
  paths:
    - ./
    - backend/app/core/config.py
    - backend/app/core/constants.py
    - backend/app/services/db_connection.py
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
    - .github/workflows/ci.yml
    - .github/workflows/fly-deploy.yml
    - docker-compose.yml
    - angular-app/nginx.prod.conf
    - angular-app/package.json
    - angular-app/angular.json
    - .gitignore
    - .nvmrc
  components:
    - core
    - services
    - api/v1/endpoints
    - auth
    - stores
    - security
    - models
    - scripts
    - angular-app
    - proxy / cron
shallow:
  paths:
    - backend/app/api/v1/endpoints/
    - backend/app/services/
    - backend/app/auth/
    - backend/app/stores/
    - backend/app/security/
    - backend/app/models/
    - angular-app/src/app/
    - docs/
    - proxy/
    - cron/
    - .github/workflows/daily-sync.yml
    - .github/workflows/sofascore-sync.yml
```
