# Deployment Pipeline — Questions

Intent `260929-assistant-god-file`, scope `refactor` (Minimal), fase Operation. **Brownfield**: el
sistema ya está en producción con un pipeline Fly.io maduro (`.github/workflows/fly-deploy.yml`) y
un runbook de rollback (`docs/ROLLBACK.md`). Este refactor **no cambia el comportamiento
observable**; el shim de re-export preserva la superficie pública, así que el artefacto desplegado
(la app FastAPI) se despliega igual que hoy. La regla afirmada manda **no cambiar la topología ni
el orden de despliegue**.

Cada pregunta está anclada a la evidencia del pipeline existente; las respuestas propuestas
documentan lo vigente (no rediseñan).

## Q1 — Estrategia de despliegue (blue/green, canary, rolling)

El pipeline actual despliega con `flyctl deploy` a dos apps Fly.io (`futmondo-api`,
`futmondo-app`) en la región `cdg`, con verificación por smoke test `/health` post-deploy. Es un
**recreate/rolling gestionado por Fly.io** en un único entorno de producción (sin staging). Sin
AWS: blue/green y canary gestionados (CodeDeploy/Evidently) son NO-APLICA por el mandato de coste
0 €.

- A. Mantener la estrategia actual sin cambios (recreate/rolling de Fly.io + smoke `/health`).
- X. Other (please specify)

[Answer]: A

## Q2 — Gates de promoción entre entornos (dev → staging → prod)

No hay entornos separados: se **despliega on-merge a `main`** directamente a producción. El gate
de promoción es el job `verify` (gitleaks + pip-audit + ruff + pytest con cobertura + npm audit +
ng test) del que dependen los deploys vía `needs:`; un rojo nunca llega a producción.

- A. Mantener el gate `verify` on-merge como única promoción (sin staging separado; coste 0 €).
- X. Other (please specify)

[Answer]: A

## Q3 — Workflow de aprobación para producción

Despliegue continuo on-merge a `main`: la aprobación efectiva es el Merge Request con el gate de
CI bloqueante + branch protection (required status check). No hay aprobación manual adicional
pre-deploy (single-maintainer).

- A. Mantener el modelo actual (MR + gate CI bloqueante como aprobación; deploy automático on-merge).
- X. Other (please specify)

[Answer]: A

## Q4 — Procedimiento de rollback

Documentado en `docs/ROLLBACK.md`: rollback **manual** vía `fly releases rollback <vN>` (o redeploy
de la imagen previa), verificado con `curl /health`. Limitación aceptada: el estado en memoria
(`TaskManager`, syncs en curso) se pierde en el redeploy.

- A. Mantener el runbook de rollback existente (`fly releases rollback` + verificación `/health`).
- X. Other (please specify)

[Answer]: A

## Q5 — Estrategia de feature flags

El proyecto **no usa feature flags** (AppConfig/Evidently son AWS de pago → NO-APLICA por coste
0 €). El refactor no introduce comportamiento nuevo que requiera flag: la superficie pública es
idéntica, así que no hay lanzamiento progresivo que gestionar.

- A. Sin feature flags (no aplican; refactor sin cambio de comportamiento; coste 0 €).
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Resumen de las decisiones confirmadas para el pipeline de despliegue (todas mantienen lo vigente,
por ser un refactor sin cambio de comportamiento sobre un sistema ya en producción):

- **Q1 Estrategia**: recreate/rolling gestionado por Fly.io + smoke `/health`; sin blue/green ni
  canary (AWS de pago, NO-APLICA por coste 0 €).
- **Q2 Gates de promoción**: gate `verify` on-merge a `main` como única promoción; sin staging.
- **Q3 Aprobación de producción**: MR + gate CI bloqueante + branch protection; deploy automático
  on-merge (single-maintainer).
- **Q4 Rollback**: runbook existente `docs/ROLLBACK.md` (`fly releases rollback` + verificación
  `/health`); pérdida de estado en memoria aceptada.
- **Q5 Feature flags**: ninguno (no aplican; superficie pública idéntica).

Los artefactos (`cd-config.md`, `deployment-strategy.md`, `rollback-runbook.md`) documentarán este
pipeline vigente sin cambiar su topología ni su orden (regla afirmada), marcando NO-APLICA lo de
pago.

- Looks correct
- Request changes

[Answer]: Looks correct
