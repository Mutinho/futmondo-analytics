# Health Check Report — sync god-file refactor

## Estado

Readiness contra el healthcheck `/health`, adaptado al stack real (Fly.io + Neon,
coste 0 €). La validación en producción se ejecuta on-merge (job `smoke-test`);
esta etapa documenta la preparación y los criterios.

## Healthchecks del stack

| App | Check | Criterio |
|-----|-------|----------|
| Backend `futmondo-api` (Fly.io, puerto 8000) | `/health` | HTTP 200, `{"status":"healthy"}` |
| Frontend `futmondo-app` (Fly.io, nginx) | `/` | HTTP 200 |
| Neon PostgreSQL (Frankfurt, free) | conectividad desde el backend | sin cambios en este refactor |

## Métricas de salud y error (adaptación al stack)

Regla afirmada: adaptar el conocimiento AWS/CloudWatch al stack real y marcar
NO-APLICA/diferido lo de pago, con la alternativa gratuita.

- **Health metric**: healthcheck `/health` (HTTP 200) — SLI informal de
  disponibilidad. Observación pull vía `fly status` + el smoke test del release.
- **Error rate metric**: ausencia de pasos `degraded` inesperados y de errores en
  `fly logs` (correlación por log estructurado / `task_id`). No hay dashboard de
  métricas gestionado (CloudWatch NO-APLICA; coste 0 €).
- **SLO formal con burn-rate**: **diferido** (requiere servicio de pago). SLI
  informal = `/health` 200 + logs limpios.
- **Alerting**: notificación de GitHub Actions en rojo (gate/smoke test); escalado
  single-maintainer. Alertas por umbral gestionadas NO-APLICA.

## Impacto del refactor en la salud

- Sin cambios en el arranque del servicio, el contrato REST, ni la conectividad a
  Neon. La extracción de `match_odds` es interna (facade delgado + orquestador +
  adapter) y preserva la superficie pública, así que no introduce nuevos modos de
  fallo observables en `/health`.
- El estado en memoria (`TaskManager`, syncs en curso) se pierde en redeploy — es
  la limitación aceptada de siempre, no alterada por este refactor.

## Readiness

- **Deployment-ready** para el alcance del piloto: checks en verde, equivalencia
  verificada, sin migraciones, healthcheck sin cambios esperados. La validación de
  salud real se confirma con el smoke test `/health` on-merge.
