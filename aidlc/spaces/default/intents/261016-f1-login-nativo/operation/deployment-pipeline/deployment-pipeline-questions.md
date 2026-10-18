# Deployment Pipeline — Preguntas y confirmación — F1: Login nativo end-to-end

> Fase: operación (deployment-pipeline). Idioma: castellano; tokens técnicos verbatim en inglés.

## Preguntas de clarificación

Las preguntas del stage (estrategia de despliegue, gates de promoción, aprobaciones de producción,
rollback, feature flags) se resuelven con decisiones ya tomadas y documentadas en el stack real; no
hay preguntas abiertas que requieran nueva entrada del propietario:

- **Estrategia de despliegue**: recreate on-merge a Fly.io (backend) + instalación manual con
  `xtool` (iOS). Sin blue/green ni canary (entorno único, coste 0 €).
- **Gates de promoción**: job `verify` bloqueante antes del deploy; sin staging (el smoke `/health`
  es la verificación de release).
- **Aprobación de producción**: gate de CI bloqueante + revisión de PR (single-maintainer); push a
  `main` reejecuta el gate en `verify`.
- **Rollback**: manual vía `flyctl` (`docs/ROLLBACK.md`) para backend; reinstalar build previo para
  iOS.
- **Feature flags**: NO-APLICA — D-01 es aditivo y retrocompatible por precedencia (cookie → header
  → body), no necesita flag.

## Consolidated Summary Confirmation

Resumen de lo producido en deployment-pipeline para F1:

- **Backend D-01**: se reutiliza el CD on-merge a Fly.io ya operativo (`fly-deploy.yml`,
  `verify → deploy-backend → deploy-frontend → smoke-test`), sin cambios. D-01 es aditivo,
  retrocompatible y sin migraciones de BD; ya desplegado a `futmondo-api`.
- **App iOS**: distribución por firma gratuita con `xtool` desde WSL (`install-app.sh`), instalación
  manual en el iPhone 13 Pro. Publicación en App Store **diferida (B-09)** (Apple Developer Program
  de pago, excepción acotada de coste).
- **Estrategia**: recreate on-merge (backend) + recreate por reinstalación (iOS); sin blue/green,
  canary ni feature flags, con rationale documentado. Verificación: smoke `/health` (backend) +
  validación manual login → auto-login → logout (iOS).
- **Rollback**: `rollback-runbook.md` reutiliza `docs/ROLLBACK.md` (backend, `flyctl`) y añade el
  canal iOS (reinstalar build previo); limitaciones del entorno único documentadas.
- **Adaptación al stack**: AWS/CloudWatch mapeado a equivalentes gratuitos; DR multi-región,
  canary con métricas y feature flags gestionados marcados NO-APLICA/diferido (coste 0 €). No se
  inventa infraestructura: `infrastructure-specification`/`cicd-pipeline` no existen porque
  infrastructure-design se reportó `skipped` en los 3 bolts.

¿Es todo correcto?

[Answer]: Looks correct
