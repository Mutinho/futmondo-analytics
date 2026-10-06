# Reverse Engineering Timestamp — futmondo-analytics

## Reverse Engineering Run

- **Date**: 2026-10-05
- **Commit / source fingerprint**: `git:6ceb8e7103f7300c9ed9b7750299671066aa12d3`
- **Intent**: `calculadora-mejora`
- **Kind**: full rescan (reemplazo íntegro de los 9 artefactos; raíz `./`)
- **Pipeline**: Reverse Engineering — link 1 developer (scan), link 2 architect
  (síntesis + publicación). Depth Minimal.

Este run cubrió el repositorio completo en profundidad y reemplaza íntegramente el
CodeKB previo. El bloque Scope of Analysis siguiente se construyó únicamente a
partir de este run.

## Scope of Analysis

```yaml
scope_version: 1
kind: full
intent: calculadora-mejora
fingerprint: 6ceb8e7103f7300c9ed9b7750299671066aa12d3
analyzed:
  paths:
    - ./
    - README.md
    - docker-compose.yml
    - angular-app/
    - backend/
    - proxy/
    - cron/
    - docs/
    - .github/workflows/
  components:
    - angular-app (frontend SPA/PWA)
    - calculator-component
    - backend (FastAPI app)
    - prizes-domain
    - player-finances-endpoint
    - data-sync-service
    - data-manager
    - analytics-and-assistant
    - auth-and-security
    - external-clients
    - proxy-nginx
    - cron-jobs
shallow:
  paths:
    - .kiro/
```
