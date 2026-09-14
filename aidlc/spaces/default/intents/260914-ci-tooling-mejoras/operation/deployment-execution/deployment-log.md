# Log de Ejecución de Despliegue — Mejoras de CI/Tooling

> Etapa Deployment Execution (Operation) · Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Brownfield.
> El despliegue de estas mejoras se realiza vía el pipeline `fly-deploy.yml` al integrar a `main`. **No se ejecutó `fly deploy` ni push a `main` desde esta sesión** (acción sobre producción, decisión del humano; el trabajo aún no está commiteado).

## Naturaleza del despliegue

Las 5 mejoras son cambios de CI/tooling, dependencias y configuración de entorno. Su "despliegue" es la integración a `main`, que dispara el pipeline de CD existente. No hay artefacto de aplicación nuevo que desplegar manualmente.

## Plan de ejecución (a realizar por el humano)

1. Commit de los cambios (ver `source-manifest.json` de code-generation para el conjunto de ficheros).
2. Verificación pre-push (BR4.4): `cd angular-app && npm ci && npx ng test --watch=false` (o el equivalente en contenedor `node:22.22.3`). Estado: **verde (6/6)** ya verificado.
3. Push/merge a `main` (trunk-based, squash-merge).
4. El pipeline `fly-deploy.yml` se dispara automáticamente:
   - `verify`: lint + tests backend (pytest) + frontend (Vitest) — bloqueante.
   - `deploy-backend`: `flyctl deploy` a `futmondo-api`.
   - `deploy-frontend`: `flyctl deploy` a `futmondo-app`.
   - `smoke-test`: `/health` del backend responde 200.

## Estado de ejecución en esta sesión

| Paso | Estado | Evidencia |
|------|--------|-----------|
| Cambios aplicados en workspace | Hecho | 11 ficheros (ver code-summary.md / source-manifest.json) |
| Verificación de tests (Vitest) | Verde (6/6) | Contenedor node:22.22.3, 0 vulnerabilidades |
| `npm ci` / lock | Limpio, sin Karma, con Vitest | package-lock.json regenerado |
| Commit + push/merge a `main` | **Pendiente (humano)** | Acción sobre producción, fuera de esta sesión |
| Ejecución del pipeline `fly-deploy.yml` | Pendiente (se dispara con el push) | GitHub Actions |
| Deploy a Fly.io | Pendiente (lo ejecuta el pipeline) | — |

## Migraciones de base de datos

Ninguna. Estas mejoras no tocan esquema ni datos (Neon PostgreSQL intacto).

## Rollback

Ver `../deployment-pipeline/rollback-runbook.md`: rollback nativo de Fly.io (`fly releases` + redeploy) y `git revert` por mejora. Coste 0€.

## Nota sobre el fallo de build preexistente

El `ng build` de producción falla por presupuesto de bundle (1.03 MB > 1 MB), deuda **preexistente** ajena al intent (`test-results.md`). No bloquea la integración de estas mejoras de tooling; el gate de CI del frontend usa `ng test` (verde), no `ng build`. La optimización del bundle es un trabajo aparte.
