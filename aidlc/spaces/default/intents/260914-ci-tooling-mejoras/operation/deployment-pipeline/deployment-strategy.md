# Estrategia de Despliegue — Mejoras de CI/Tooling

> Etapa Deployment Pipeline (Operation) · Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Brownfield.
> Documenta la estrategia **existente**. Este intent de CI/tooling no la modifica.

## Estrategia

**Deploy on merge a `main`** (trunk-based). Cada push a `main` que pasa el gate `verify` dispara el despliegue a Fly.io. No hay entornos staging separados: la verificación de release es el smoke test contra `/health` (según `org.md` ## Deployment y las notas de `fly-deploy.yml`).

## Mecanismo de despliegue

- **Tipo**: reemplazo de máquina en Fly.io (`flyctl deploy`), no blue/green ni canary.
- **Frontend** (`futmondo-app`): `min_machines_running = 1`, `max_machines_running = 1`, `force_https`, health check HTTP `/` cada 30s.
- **Backend** (`futmondo-api`): health check `/health`.
- **Orden**: backend primero, frontend después (el frontend depende del backend por contrato REST).

## Gates de promoción

| Gate | Criterio | Dónde |
|------|----------|-------|
| CI Gate (PR) | Lint advisory + tests bloqueantes (pytest, Vitest) + secret scan bloqueante | `ci.yml` + branch protection en `main` |
| Verify (push a main) | Reejecuta lint + tests; gatea los deploys via `needs` | `fly-deploy.yml` job `verify` |
| Smoke test | `/health` responde 200 tras el deploy | `fly-deploy.yml` job `smoke-test` |

## Criterio transversal de no regresión (BR6.1 / FR6.2)

Tras cada mejora, la suite de tests permanece en verde y `fly-deploy.yml` sigue desplegando. Verificado: tests 6/6 verdes con Vitest; el pipeline conserva su estructura (solo cambian setup-node y el runner de test).

## Sin cambios de estrategia en este intent

Las 5 mejoras (actions, punycode, animaciones, Karma→Vitest, Node local) no alteran el modelo de despliegue, los objetivos Fly.io ni los gates. Solo actualizan el tooling dentro del job `verify`.

## Producción / aprobación

`org.md` ## Deployment indica que los deploys a producción pueden gatear con aprobación manual. En este proyecto, el gate efectivo es el `verify` + smoke test; no hay entorno de staging separado (decisión de proyecto, coste 0€).
