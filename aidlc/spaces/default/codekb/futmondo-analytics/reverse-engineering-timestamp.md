# Reverse Engineering Timestamp — Futmondo Analytics

> Artefacto CodeKB (architect). Registra cuándo se realizó el reverse engineering.

## Registro

- **Fecha de análisis**: 2026-09-15
- **Source commit**: `git:8d71c88ecafa79e796794feec64fcc4c9d2e671b`
- **Source fingerprint previo**: `git:349059d113480c24c1dfef2ecb8be28deb50a448` (snapshot del run anterior)
- **Intent**: `260914-durabilidad-estado-y-cre`
- **Tipo de escaneo**: FOCUSED SCAN sobre el backend `backend/` (durabilidad de estado y credenciales Futmondo, FR1 + FR5)
- **Links del pipeline**: link 1 (developer scan) → link 2 (architect synthesis, este CodeKB)
- **Base primaria**: `aidlc/spaces/default/intents/260914-durabilidad-estado-y-cre/inception/reverse-engineering/developer-scan.md`
- **Nota de merge**: store previo **STALE** (análisis del intent `260914-bundle-optimization`, foco frontend). Se preserva la prosa fuera del foco (frontend, cron, proxy, bundle, CI/CD) y se actualiza/extiende la del backend (auth/`SessionStore`, `TaskManager`, persistencia Neon, sync). Por ser STALE, el bloque de scope registra **solo este run** en `analyzed`; las `analyzed.paths` profundas previas del store (frontend `angular-app/`) se **degradan a `shallow.paths`** porque su cobertura profunda no se pudo re-verificar, junto a las shallow existentes y las nuevas de este run.

## Scope of Analysis

```yaml
scope_version: 1
kind: partial
intent: 260914-durabilidad-estado-y-cre
fingerprint: d2b01ebcf98fb0aa136bc02b6101309768d34cbe
analyzed:
  paths:
    - backend/app/auth/session_store.py
    - backend/app/auth/token_store.py
    - backend/app/auth/routes.py
    - backend/app/auth/jwt_utils.py
    - backend/app/auth/dependencies.py
    - backend/app/auth/models.py
    - backend/app/services/task_manager.py
    - backend/app/services/db_connection.py
    - backend/app/services/futmondo_client.py
    - backend/app/api/v1/endpoints/sync.py
    - backend/app/api/v1/endpoints/_helpers.py
    - backend/app/core/config.py
    - backend/app/main.py
    - backend/scripts/init_db.py
    - backend/requirements.txt
    - backend/Dockerfile
    - backend/ruff.toml
    - backend/pytest.ini
    - backend/conftest.py
    - backend/nixpacks.toml
    - backend/fly.toml
  components:
    - backend
shallow:
  paths:
    - backend/app/services/
    - backend/app/api/v1/endpoints/
    - backend/scripts/
    - backend/tests/
    - backend/static/photos/
    - backend/entrypoint.sh
    - backend/run.py
    - angular-app/package.json
    - angular-app/package-lock.json
    - angular-app/angular.json
    - angular-app/tsconfig.json
    - angular-app/tsconfig.app.json
    - angular-app/tsconfig.spec.json
    - angular-app/eslint.config.js
    - angular-app/src/main.ts
    - angular-app/src/styles.scss
    - angular-app/src/app/app.config.ts
    - angular-app/src/app/app.ts
    - angular-app/src/app/app.routes.ts
    - angular-app/src/app/features/analytics/analytics.routes.ts
    - angular-app/src/app/features/budget/budget.routes.ts
    - angular-app/src/app/shared/components/assistant-fab.component.ts
    - angular-app/src/app/shared/components/assistant-chat.component.ts
    - angular-app/src/app/features/evolution/evolution.component.ts
    - angular-app/src/app/features/stats/stats.component.ts
    - angular-app/src/app/features/
    - angular-app/src/app/core/
    - angular-app/src/app/shared/
    - angular-app/Dockerfile
    - angular-app/fly.toml
    - angular-app/nginx.conf
    - angular-app/nginx.prod.conf
    - angular-app/ngsw-config.json
    - .github/workflows/ci.yml
    - .github/workflows/fly-deploy.yml
    - .github/workflows/daily-sync.yml
    - .github/workflows/sofascore-sync.yml
    - cron/fly.toml
    - proxy/nginx.conf
    - docker-compose.yml
    - docs/
```
