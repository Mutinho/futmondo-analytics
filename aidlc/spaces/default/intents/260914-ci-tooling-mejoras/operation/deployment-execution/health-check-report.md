# Informe de Health Checks — Mejoras de CI/Tooling

> Etapa Deployment Execution (Operation) · Intent `260914-ci-tooling-mejoras` · Scope `refactor`.
> Health checks configurados en la infraestructura existente (Fly.io). Este intent no los modifica.

## Health checks configurados

| Componente | Tipo | Endpoint | Intervalo | Fuente |
|------------|------|----------|-----------|--------|
| Frontend (`futmondo-app`) | HTTP | `/` (puerto 80) | 30s, timeout 5s | `angular-app/fly.toml [checks.health]` |
| Backend (`futmondo-api`) | HTTP | `/health` | (docker-compose local: 30s) + smoke test en deploy | `backend/fly.toml` / `fly-deploy.yml` |

## Verificación

- Los health checks son parte de la infraestructura existente y **no cambian** con este intent (solo se tocó CI/tooling, dependencias de test y `.nvmrc`).
- Tras el deploy (vía pipeline al integrar a `main`), el health check `/` del frontend y el smoke test `/health` del backend confirman que las apps arrancan correctamente.
- No hay cambios en la lógica de arranque de las apps que puedan afectar a los health checks (NFR2, no regresión funcional).

## Estado en esta sesión

| Health check | Estado | Nota |
|--------------|--------|------|
| Frontend `/` | Pendiente (post-deploy) | Se valida en Fly.io tras el despliegue |
| Backend `/health` | Pendiente (post-deploy) | Se valida en el job smoke-test del pipeline |

## Riesgos / observaciones

- Ninguna de las 5 mejoras modifica el arranque de las apps ni sus endpoints de health, por lo que no hay riesgo introducido para los health checks.
- Si tras integrar a `main` el health check o el smoke test fallaran, aplicar el `rollback-runbook.md` (rollback nativo Fly.io).
