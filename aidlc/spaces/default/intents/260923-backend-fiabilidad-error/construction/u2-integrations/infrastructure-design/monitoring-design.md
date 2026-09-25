# Monitoring Design — u2-integrations (Integraciones)

Implementación en Fly.io de la estrategia de `observability-design.md`: logging
estructurado consultable con `fly logs` + `grep`, a coste 0 €. Sin agregador,
dashboards ni tracing de pago (NO-APLICA/adaptado).

Consume: `observability-design.md`, `reliability-design.md`, `security-design.md`,
`logical-components.md`. Perspectivas inline: plataforma (Fly.io) + DevSecOps + Compliance.

## Metrics & KPIs

| Metric | Source | Threshold | Why it matters |
|---|---|---|---|
| Salud del backend | Fly healthcheck `/health` | HTTP 200; 5 reintentos en smoke test | Verificación de release; app viva |
| Pasos `DEGRADED` por sync | logs `fly logs` (`failure_mode=` + `DEGRADED`) | 0 inesperados | SLI informal de fiabilidad (NFR2.2) |
| Fallos fatales de integración | logs `level=ERROR failure_mode=` | 0 | Señal de baneo/fatal (NFR2.3) |
| Estado del cron | resultado del job GitHub Actions (`daily-sync`, `sofascore-sync`) | success | Un fallo de cron notifica por GitHub |

## Alerts

| Alert | Condition | Severity | Routes to |
|---|---|---|---|
| Fallo fatal de integración | `level=ERROR` en `fly logs` durante un sync | alta | Inspección manual del maintainer (`fly logs`) |
| `DEGRADED` inesperado | paso marcado `DEGRADED` fuera de lo esperado | media | Inspección manual |
| Cron fallido | job GitHub Actions en rojo | alta | Notificación nativa de GitHub Actions |
| Release fallida | smoke test `/health` no 200 tras deploy | alta | Falla el deploy; notificación de GitHub |

Sin alerting automatizado de pago (PagerDuty/SNS → NO-APLICA). Escalado
single-maintainer.

## SLIs / SLOs

| SLI | SLO target | Measurement window |
|---|---|---|
| Ausencia de `DEGRADED` inesperado | informal (sin porcentaje formal) | por ejecución de sync |
| No-corrupción de `team_prizes` | verificada por spec (todo-o-nada) | por cambio (test), no runtime |
| Salud `/health` | 200 tras cada release | por deploy (smoke test) |

SLO formal con burn-rate → **NO-APLICA/diferido** (requiere métricas gestionadas
de pago; alternativa gratuita = `fly logs` + `grep` + healthcheck).

## Logs & Tracing

- **Agregación**: no hay agregador; `fly logs` es el plano de consulta. Los logs
  van a stdout/stderr (formato clave=valor de una línea, ver observability-design).
- **Consulta**: `fly logs | grep task_id=<id>` reconstruye un sync;
  `grep failure_mode=` filtra por modo de fallo.
- **Tracing**: correlación por `task_id` en los logs; tracing distribuido
  (X-Ray/Jaeger) → **NO-APLICA** (de pago).
- **Dashboards**: sin dashboards gestionados (CloudWatch/Grafana → NO-APLICA);
  `fly status` da el estado de las apps.

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- CloudWatch metrics/dashboards/alarms, X-Ray, anomaly detection ML, PagerDuty →
  NO-APLICA (de pago). Documentado con su alternativa gratuita, no inventado.

## Assumptions & Open Questions

None.
