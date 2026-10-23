# Deployment Pipeline — Preguntas

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés. Sin decisiones nuevas.

## Consolidated Summary Confirmation

Resumen de Deployment Pipeline:

- **Sin despliegue de servidor**: la capa de diseño va embebida en la app iOS; no toca la topología Fly.io (backend/frontend producción intactos).
- **Entrega iOS**: `xtool dev build` en el iPhone 13 Pro (firma gratuita, coste 0 €) tras `swift build && swift test` verde.
- **CD del repo**: `fly-deploy.yml` heredado, no modificado.
- **Rollback**: `git revert` del squash-commit del intent + reinstalar la build anterior; producción no afectada.
- NO-APLICA: pipeline CD cloud, blue/green, canary.

¿Does this all look correct?

[Answer]: Looks correct
