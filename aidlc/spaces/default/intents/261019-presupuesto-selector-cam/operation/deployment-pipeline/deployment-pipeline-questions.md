# Deployment Pipeline — Questions (F2)

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Deployment Pipeline (adaptado al stack, coste 0 €):

- **NO-APLICA despliegue nuevo**: F2 es app nativa cliente; no despliega a Fly.io/Neon ni cambia `fly-deploy.yml`. El pipeline de CD existente (backend+frontend on-merge) queda intacto y no lo ejecuta este intent.
- **Distribución** = instalación en dispositivo vía `xtool dev run` (desarrollo, firma gratuita ~7 días); publicación en App Store fuera de alcance (Apple Developer Program no activado).
- **Rollback** = `git revert` del PR de F2 + reinstalar la build anterior; la sesión de F1 no se ve afectada; el rollback del backend (`docs/ROLLBACK.md`) sigue vigente pero F2 no lo invoca.

¿Does this all look correct?

[Answer]: Looks correct
