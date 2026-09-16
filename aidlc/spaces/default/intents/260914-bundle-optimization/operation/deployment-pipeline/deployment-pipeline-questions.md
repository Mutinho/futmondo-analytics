# Preguntas — Deployment Pipeline (Optimización del bundle inicial)

> Stage 4.1 Deployment Pipeline · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield (fase Operation).
> El proyecto YA tiene un pipeline de CD completo y documentado. Este refactor de frontend NO cambia la infraestructura ni el pipeline; se despliega por el flujo existente. Las respuestas están resueltas por el estado actual del proyecto (evidencia), no re-decididas.

## Sources

- `.github/workflows/ci.yml` — gate de calidad en cada PR a `main` (pytest + ng test bloqueantes; gitleaks bloqueante; ruff/ESLint/audits advisory).
- `.github/workflows/fly-deploy.yml` — deploy en push a `main`: job `verify` → `deploy-backend` → `deploy-frontend` → `smoke-test` contra `/health`.
- `angular-app/fly.toml`, `angular-app/Dockerfile`, `angular-app/nginx.prod.conf` — despliegue del frontend en Fly.io (nginx sirve la SPA).
- `docs/ROLLBACK.md`, `docs/PR-GATE.md` — runbook de rollback y política de gate del PR.
- Regla de proyecto: coste 0 € (Fly.io free allowance, GitHub Actions free).

## Preguntas y respuestas resueltas

### Q1 — ¿Qué estrategia de despliegue (blue/green, canary, rolling)?
**Respuesta (existente):** Recreate/rolling simple sobre un único entorno de producción en Fly.io (`min_machines_running = 1`, `max_machines_running = 1`). No hay blue/green ni canary: es una app pequeña a coste 0 €. La verificación de release es el smoke test `/health` post-deploy. Este refactor no cambia esto.

### Q2 — ¿Qué gates de promoción de entornos (dev → staging → prod)?
**Respuesta (existente):** No hay staging separado (NFR2.2 del proyecto). El gate es: PR verde en `ci.yml` (branch protection en `main`) → merge → `fly-deploy.yml` reejecuta verify → deploy → smoke test. Un rojo nunca llega a producción (defensa en profundidad, replicada en el push directo).

### Q3 — ¿Qué workflow de aprobación para producción?
**Respuesta (existente):** Aprobación vía revisión de PR + branch protection en `main` (no push directo). El merge a `main` dispara el deploy automáticamente (deploy-on-merge). No hay aprobación manual adicional en CodePipeline: es un proyecto personal a coste 0 €.

### Q4 — ¿Qué procedimiento de rollback?
**Respuesta (existente):** `docs/ROLLBACK.md` — rollback manual con `fly releases rollback <vN>` (o redeploy de la imagen previa), seguido de verificación `/health`. Aplica igual a este refactor: si el bundle rompiera algo, se revierte al release anterior del frontend.

### Q5 — ¿Qué estrategia de feature flags?
**Respuesta (existente):** Ninguna. El proyecto no usa feature flags (coste 0 €, sin AppConfig/Evidently). No aplica a este refactor.

## Particularidad de este refactor

- El único cambio relevante para el pipeline: el frontend debe seguir compilando con el budget `maximumError: 1MB` restaurado. El gate de CI (`ng test`) y el deploy (`flyctl deploy`, que ejecuta `ng build --configuration production` en el Dockerfile) fallarían si el bundle superara 1 MB — fail-closed que protege el objetivo NFR1 en cada despliegue futuro. Verificado en Build and Test: 819 kB < 1 MB.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
