# Preguntas — Deployment Execution (Optimización del bundle inicial)

> Stage 4.3 Deployment Execution · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield (fase Operation).
> Etapa final. Despliegue por **deploy-on-merge** (merge a `main` → GitHub Actions → Fly.io). El agente NO despliega a producción ni hace push a `main` por su cuenta (acción de alto impacto, decisión del usuario).

## Sources

- `operation/deployment-pipeline/cd-config.md`, `deployment-strategy.md`, `rollback-runbook.md`.
- `construction/build-and-test/test-results.md` — build 819 kB < 1 MB, suite 11/11 verde.
- `.github/workflows/fly-deploy.yml` — pipeline de deploy real.

## Pre-deployment checks (Step 2)

### Q1 — ¿Pasan todas las comprobaciones pre-despliegue?
**Respuesta:** Sí. Build de producción verde con `maximumError: 1MB` (819 kB), suite 11/11 verde, bundle verificado (chart.js/ng2-charts/marked fuera del inicial). El gate de CI (`ci.yml`) volverá a ejecutar `ng test` en el PR.

### Q2 — ¿Se requieren migraciones de base de datos y están probadas?
**Respuesta:** No. Este refactor es solo frontend (composición del bundle); no toca esquema ni datos. Sin migraciones.

### Q3 — ¿Los servicios dependientes están disponibles y sanos?
**Respuesta:** Sí. El backend `futmondo-api` no cambia con este refactor. El smoke test post-deploy verifica `/health`.

### Q4 — ¿Cuál es la ventana de despliegue?
**Respuesta:** A discreción del usuario. Al ser deploy-on-merge en un entorno único sin staging, el despliegue ocurre cuando el usuario mergea el PR a `main`. Sin ventana crítica (app de uso personal).

## Estado del despliegue

- **Estado actual:** los cambios del refactor están en el workspace local, **sin commitear/pushear**. El despliegue real está PENDIENTE de la acción del usuario (abrir PR → gate CI verde → merge a `main` → deploy automático).
- **El agente no ejecuta el deploy** (`flyctl deploy` ni push a `main`): es una acción de alto impacto en producción y el flujo del proyecto es deploy-on-merge controlado por el usuario.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
