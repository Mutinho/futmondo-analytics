# CD Config — F2 (Deployment Pipeline)

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Aplicabilidad

**NO-APLICA despliegue nuevo.** F2 añade código de app nativa iOS (`ios/`); no despliega a Fly.io/Neon ni cambia `fly-deploy.yml`. El pipeline de CD existente (backend `futmondo-api` + frontend `futmondo-app` on-merge a `main`) queda **intacto** y no se ejecuta por este intent.

- La "distribución" de la app nativa es la **instalación en dispositivo** vía `xtool dev run` (desarrollo, firma gratuita ~7 días), no un pipeline de CD. La publicación en App Store (Apple Developer Program) sigue sin activarse en este intent.
- No hay artefacto de release nuevo que desplegar a servidor.

## Sources

- `aidlc/spaces/default/memory/team.md` (Deployment on-merge Fly.io; este intent no despliega)
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/infrastructure-design/cicd-pipeline.md`

## Assumptions & Open Questions

None.
