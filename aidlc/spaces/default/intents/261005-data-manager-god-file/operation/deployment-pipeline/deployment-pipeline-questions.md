# Deployment Pipeline — Questions

> Scope `refactor` (equivalencia). El sistema **ya está en producción** con un
> pipeline Fly.io maduro (`ci.yml` + `fly-deploy.yml`). Este refactor **no cambia
> la topología ni el orden de despliegue**; la etapa documenta el CD existente
> aplicado a este cambio y confirma el rollback. Las respuestas recomendadas se
> fundamentan en el workspace (no son decisiones abiertas); confirma o corrige.

## Q1 — Estrategia de despliegue (blue/green, canary, rolling, recreate)

Recomendado (del `fly-deploy.yml` existente): **recreate / redeploy on-merge**,
sin blue/green ni canary. Cadena `verify → deploy-backend → deploy-frontend →
smoke-test`. Un refactor de equivalencia no justifica introducir canary (coste y
complejidad; mandato coste 0 €).

[Answer]: A. Mantener la estrategia existente (recreate on-merge, sin cambios)

## Q2 — Gates de promoción de entornos (dev → staging → prod)

Recomendado: **sin staging separado** (ya es la realidad del stack). El gate es
el job `verify` bloqueante (gitleaks + pip-audit + ruff + pytest con cobertura +
npm audit + ng test) y la verificación de release es el smoke test `/health`
(5 reintentos, HTTP 200).

[Answer]: A. Mantener el gate `verify` bloqueante + smoke `/health`, sin staging

## Q3 — Flujo de aprobación para producción

Recomendado: **merge a `main`** (trunk-based, squash) con el gate de CI
bloqueante como required status check; el push a `main` re-ejecuta el gate en
`verify`. Sin aprobación manual adicional (single-maintainer).

[Answer]: A. Merge a main gateado por CI (sin aprobación manual extra)

## Q4 — Procedimiento de rollback

Recomendado: el runbook existente `docs/ROLLBACK.md` — `fly releases rollback
<vN>` (o redeploy de la imagen previa), verificado con `/health`. **Clave para
este refactor**: cada módulo se extrajo en commit aislado (squash por MR), de
modo que el rollback quirúrgico por responsabilidad es trivial (revertir el
commit del módulo problemático).

[Answer]: A. Reusar docs/ROLLBACK.md (fly releases rollback) + commits aislados por módulo

## Q5 — Estrategia de feature flags

Recomendado: **ninguna / no aplica**. Un refactor de equivalencia no introduce
comportamiento nuevo que ocultar tras un flag; el resultado observable es nulo.

[Answer]: A. Sin feature flags (no aplica a un refactor de equivalencia)

## Consolidated Summary Confirmation

Resumen de lo que se generará (todo = mantener el CD de producción existente,
documentado aplicado a este refactor de equivalencia):

- **deployment-strategy.md**: recreate/redeploy on-merge a Fly.io (región `cdg`),
  cadena `verify → deploy-backend → deploy-frontend → smoke-test`; sin
  blue/green ni canary; sin staging; verificación de release = smoke `/health`.
- **cd-config.md**: el pipeline `fly-deploy.yml` existente (job `verify`
  bloqueante: gitleaks + pip-audit + ruff + pytest con cobertura + npm audit +
  ng test; luego deploys y smoke), sin cambios de topología ni orden.
- **rollback-runbook.md**: reusa `docs/ROLLBACK.md` (`fly releases rollback`),
  reforzado por commits aislados por módulo → rollback quirúrgico por
  responsabilidad.
- Sin feature flags (no aplica).

[Answer]: Looks correct

