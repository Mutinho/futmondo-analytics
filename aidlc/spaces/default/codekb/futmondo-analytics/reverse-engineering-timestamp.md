# Reverse Engineering Timestamp — futmondo-analytics

## Reverse Engineering Run

- **Date**: 2026-10-06
- **Commit / source fingerprint**: `git:da8ce0c6a7d7debb97b52e1d04ee86f6ef314b98`
- **Intent**: `angular-native-feasibili`
- **Kind**: full rescan (reemplazo íntegro de los 9 artefactos; raíz `./`)
- **Pipeline**: Reverse Engineering — link 1 developer (scan), link 2 architect
  (síntesis + publicación). Depth Standard.

Este run cubrió el repositorio completo en profundidad y reemplaza íntegramente
el CodeKB previo (store anterior era STALE). El bloque Scope of Analysis
siguiente se construyó únicamente a partir de este run.

## Scope of Analysis

```yaml
scope_version: 1
kind: full
intent: angular-native-feasibili
fingerprint: da8ce0c6a7d7debb97b52e1d04ee86f6ef314b98
analyzed:
  paths:
    - ./
    - README.md
    - docker-compose.yml
    - .nvmrc
    - angular-app/
    - backend/
    - proxy/
    - cron/
    - docs/
    - .github/workflows/
  components:
    - angular-app (frontend SPA/PWA)
    - calculator-component
    - analytics-and-charts
    - backend (FastAPI app)
    - api-endpoints
    - data-manager
    - data-sync-service
    - analytics-and-assistant
    - auth-and-security
    - external-clients
    - photo-service
    - proxy-nginx
    - cron-jobs
shallow:
  paths:
    - backend/tests/
    - backend/scripts/
    - angular-app/src/
```
