# Health Check Report — refactor DDD del asistente

Intent `260929-assistant-god-file`, scope `refactor`, fase Operation. Valida el health check del
despliegue, adaptado al stack Fly.io + Neon a coste 0 €.

## Health checks configurados (vigentes, sin cambios)

| App | Check | Definición |
|-----|-------|------------|
| `futmondo-api` (backend) | `GET /health` → 200 `{"status":"healthy"}` | Fly.io health check (puerto 8000) + job `smoke-test` del pipeline |
| `futmondo-app` (frontend) | `GET /` (nginx) | Fly.io health check (puerto 80) |

El refactor no cambia los health checks ni su configuración: el endpoint `/health` del backend es
independiente del paquete `assistant/` refactorizado.

## Métrica de salud y de error (adaptación coste 0 €)

- **Métrica de salud**: disponibilidad del endpoint `/health` (200) — observada vía el smoke test
  post-deploy y `fly status`.
- **Métrica de error**: presencia de errores/`degraded` inesperados en `fly logs` (logging
  estructurado). El asistente refactorizado preserva los modos de degradación observables (LLM y
  lecturas de contexto degradan sin romper; BR3.3/BR5.3), así que la señal de error no cambia.

## Estado de validación

- **Pre-merge**: el arranque sano del servicio se valida indirectamente por la suite verde y el
  import histórico OK (ver `smoke-test-results.md`).
- **Post-deploy (pendiente del merge)**: el smoke test `/health` y `fly status` confirman la salud
  en producción tras el merge. Registrado como pendiente; no ejecutado por el agente.

## SLO / observabilidad (adaptación al stack)

- **Sin SLO formal con burn-rate** (requiere servicios de pago → NO-APLICA por coste 0 €). SLI
  informal: `/health` 200 + ausencia de pasos `degraded` inesperados en `fly logs`.
- **Sin tracing distribuido ni anomaly detection ML** (de pago → NO-APLICA). Correlación por log
  estructurado.
- Cada app mantiene al menos una métrica de salud (`/health`, `/`) y la señal de error por `fly
  logs`, cumpliendo el guardrail de observabilidad de la fase Operation dentro del tier gratuito.

## Escalado / incidentes

- Single-maintainer: la notificación de fallo del pipeline (GitHub Actions) es la ruta de escalado.
  Ante `/health` en rojo post-deploy, seguir `../deployment-pipeline/rollback-runbook.md`
  (`fly releases rollback`).
