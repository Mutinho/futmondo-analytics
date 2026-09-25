# Deployment Pipeline — Preguntas · Operación (FR3.2 + FR4)

El CD **ya existe y es maduro**: on-merge a `main` → Fly.io (`fly-deploy.yml`:
`verify` → `deploy-backend` → `deploy-frontend` → `smoke-test /health`), con
runbook de rollback en `docs/ROLLBACK.md`. Este intent **no cambia la topología
ni el orden de despliegue** (afirmado en memoria). Adaptado a Fly.io + coste 0 €
(los patrones AWS del conocimiento se marcan NO-APLICA). Una sola pregunta.

## Q1 — Alcance del pipeline de despliegue (CD) en este intent

- A. **Sin cambios de CD**: documentar el pipeline de despliegue Fly.io
  existente, la estrategia (on-merge, sin blue/green ni canary — topología fija
  `min=max=1`, coste 0 €) y el runbook de rollback (`docs/ROLLBACK.md`, redeploy
  de la release previa) tal cual. Sin gates de promoción nuevos (no hay staging
  separado; el smoke `/health` es la verificación de release).
- B. Introducir cambios de CD (p. ej. entorno de staging, blue/green, aprobación
  de producción formal).
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
