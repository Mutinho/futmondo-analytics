# Informe de Health Check — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, brownfield. Conversation language: Spanish.

## Health checks configurados (Fly.io)

| App | Check | Criterio de sano |
|-----|-------|------------------|
| `futmondo-api` (backend) | `GET /health` (puerto 8000) | HTTP 200, `{"status":"healthy"}` |
| `futmondo-app` (frontend) | `GET /` (nginx) | HTTP 200 |

## Validación para esta oleada

- **Backend (`futmondo-api`)**: la extracción de `analytics` es interna a esta app. El endpoint `/health` no cambia. La app importa y arranca correctamente en local (`app.main` resuelve; suite 218/0), lo que valida que el shim y el paquete `analytics/` no rompen el arranque. El healthcheck de Fly seguirá respondiendo 200 tras el deploy.
- **Frontend (`futmondo-app`)**: sin cambios en esta oleada; su health check `/` no se ve afectado.

## Estado

- **Local (pre-merge)**: sano — arranque OK, suite verde.
- **Producción**: PENDIENTE del merge a `main`. Tras el `deploy-backend`, el healthcheck de Fly y el job `smoke-test` (`/health`) validarán la salud automáticamente.

## Contrato de salud preservado

El refactor preserva el comportamiento observable (BR1.1); ningún endpoint, incluido `/health`, cambia su contrato. Si el arranque fallara por la extracción, el smoke test post-deploy lo detectaría y el runbook de rollback (`operation/deployment-pipeline/rollback-runbook.md`) revertiría a la release previa.

## Observabilidad (nota de stack real)

El proyecto no usa CloudWatch/tracing distribuido (coste 0 €). La observabilidad disponible es `fly logs`, el healthcheck de Fly y el logging estructurado de la app. No se introduce tooling de pago en esta oleada.
