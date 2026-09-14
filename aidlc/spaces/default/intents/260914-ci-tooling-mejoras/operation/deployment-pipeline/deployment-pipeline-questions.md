# Preguntas — Deployment Pipeline (Mejoras de CI/Tooling)

> Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Depth Minimal · Brownfield.
> El pipeline de CD ya existe (`.github/workflows/fly-deploy.yml`, Fly.io). Este intent de CI/tooling no cambia la estrategia de despliegue; solo actualizó actions de Node (mejora 1) y retiró Chrome headless de los tests (mejora 4).

## Q1 — Alcance de esta etapa de Deployment Pipeline

Dado que el pipeline de CD ya está operativo y las 5 mejoras no cambian el modelo de despliegue (verify → deploy backend → deploy frontend → smoke test `/health`), ¿qué alcance quieres para esta etapa?

- A. Documentar el pipeline de CD existente reflejando los cambios de las mejoras (setup-node@v5, tests sin Chrome), sin modificar la estrategia. (recomendado)
- B. Además, proponer mejoras opcionales del pipeline de CD (coste 0€) para futura consideración.
- C. Rediseñar la estrategia de despliegue (fuera del alcance de este intent).
- X. Other (please specify)

[Answer]: A

## Q2 — Estrategia de rollback a documentar

El despliegue actual en Fly.io es un reemplazo de máquina con health check `/health` (backend) y `/` (frontend). ¿Qué rollback documentar en el runbook?

- A. Rollback nativo de Fly.io (`fly releases` + `fly deploy --image <release-anterior>` / `fly machine update`), que es el mecanismo disponible en tier gratuito. (recomendado)
- B. Blue/green con doble app (introduce coste, descartado por regla de coste 0€).
- C. Sin rollback documentado.
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

Resumen de decisiones:
- Q1: A — Documentar el pipeline de CD existente (`fly-deploy.yml`, Fly.io) reflejando los cambios de las mejoras (setup-node@v5, tests sin Chrome headless), sin modificar la estrategia de despliegue.
- Q2: A — Documentar el rollback nativo de Fly.io (`fly releases` + redeploy de release anterior), único mecanismo en tier gratuito (coste 0€).

Se generarán: `cd-config.md`, `deployment-strategy.md`, `rollback-runbook.md`.

- Looks correct
- Request changes

[Answer]: Looks correct
