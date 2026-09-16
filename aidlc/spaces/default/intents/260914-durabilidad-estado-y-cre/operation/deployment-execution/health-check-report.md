# Health Check Report — Durabilidad del estado

> Etapa Deployment Execution (Operation). Reporte de los health checks configurados y el resultado
> esperado tras el despliegue (que ocurre al fusionar a `main`). No ejecutado desde el workflow: el
> despliegue aún no ha ocurrido.

## Estado

- **Estado**: PLANIFICADO — los health checks corren en Fly.io tras el deploy y en el smoke test del pipeline.

## Health checks configurados

| App | Check | Config | Fuente |
|-----|-------|--------|--------|
| `futmondo-api` (backend) | HTTP `/health` puerto 8000 | `interval=30s`, `timeout=5s` | `backend/fly.toml` `[checks.health]` |
| `futmondo-app` (frontend) | HTTP `/` puerto 80 | (nginx) | `team.md` / topología |

## Resultado esperado tras el deploy

- **Backend `/health`**: HTTP 200. El endpoint no depende del estado durable nuevo, así que responde
  200 independientemente de si `FUTMONDO_CRED_KEY` está fijado.
- **Arranque del backend**: crea el esquema durable idempotente (`sync_session`, `sync_task`) y ejecuta
  el sweep `mark_interrupted_on_startup` (FR1.5) sin bloquear el arranque ni el health check.
- **Frontend `/`**: HTTP 200 (nginx sirve la SPA).
- **Guard de arranque**: si `JWT_SECRET` fuese default/vacío, el arranque abortaría (NFR1.1) y el
  health check fallaría — señal correcta de configuración incompleta.

## Criterios de aceptación del despliegue

- El job `smoke-test` de `fly-deploy.yml` obtiene HTTP 200 de `/health` (5 reintentos) → release verificado.
- Ambas máquinas Fly (`min=max=1`) quedan sanas tras el deploy.

## Observaciones

- No hay endpoint de health específico de la durabilidad; el `/health` existente es suficiente como
  verificación de release (decisión del equipo: sin staging separado, el health check ES la verificación).
- Métricas/observabilidad de la durabilidad (p. ej. errores de rehidratación) se abordan en la etapa
  siguiente, Observability Setup, si aplica.
