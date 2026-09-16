# Deployment Strategy — Optimización del bundle inicial

> Stage 4.1 Deployment Pipeline · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield (fase Operation).
> Sin cambio funcional, coste 0 €. Estrategia existente del proyecto, aplicada a este refactor.

## Sources

- `angular-app/fly.toml` (single-region, 1 máquina), `.github/workflows/fly-deploy.yml`.
- `docs/ROLLBACK.md`, `docs/DEPLOY.md`.

## Estrategia de despliegue

- **Modelo**: entorno único de producción en Fly.io (región `cdg`, `min=max=1` máquina). No hay blue/green ni canary — es un proyecto pequeño a coste 0 € (Fly.io free allowance).
- **Disparador**: deploy-on-merge. Un merge a `main` (tras PR verde) dispara `fly-deploy.yml`.
- **Orden**: verify → backend → frontend → smoke test. Este refactor solo afecta al job `deploy-frontend`.
- **Verificación de release**: smoke test automático contra `/health` (backend). Para este refactor, verificación manual adicional de gráficos (`evolution`, `stats`) y chat del asistente tras el deploy (BR5.1/FR1.3/FR2.3).

## Pasos de despliegue de este refactor

1. Abrir PR con los cambios del refactor hacia `main`. El gate `ci.yml` debe pasar (`ng test` verde — verificado: 11/11).
2. Verificar en local/CI que `ng build --configuration production` pasa con `maximumError: 1MB` (verificado en Build and Test: 819 kB).
3. Merge a `main` → `fly-deploy.yml` despliega el frontend a `futmondo-app`.
4. Smoke test `/health` (automático) + verificación manual de gráficos y chat.

## Criterios de éxito / aborto

- **Éxito**: build de producción pasa con budget 1 MB, smoke test `/health` 200, gráficos y chat funcionan.
- **Aborto/rollback**: si el smoke test falla o se detecta regresión funcional (gráficos/chat rotos), ejecutar el runbook de rollback (`rollback-runbook.md`). Al ser un cambio de código sin migración de datos ni de esquema, el rollback es limpio (redeploy del release anterior del frontend).

## Riesgo

Bajo. Cambio de código frontend sin migración de datos, sin cambio de infraestructura, sin dependencias nuevas. El principal riesgo (referencias rotas por la carga diferida) se cazó y resolvió en Build and Test (NG8001).
