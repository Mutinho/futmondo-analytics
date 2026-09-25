# Alarms — Observabilidad (FR3.2 + FR4)

Alerting adaptado a coste 0 € (single-maintainer). No hay CloudWatch Alarms /
SNS / PagerDuty (de pago → NO-APLICA); la señal es la notificación nativa de
GitHub Actions + inspección de `fly logs`.

## Señales de alerta (síntomas, no causas)

| Alerta | Condición | Severidad | Ruta |
|---|---|---|---|
| Release fallida | `smoke-test /health` ≠ 200 tras deploy | Alta | Job de GitHub Actions en rojo (notificación) → rollback (`rollback-runbook.md`) |
| Cron fallido | `daily-sync.yml` / `sofascore-sync.yml` en rojo | Alta | Notificación de GitHub Actions |
| Fallo fatal de integración | `level=ERROR failure_mode=…` en `fly logs` durante un sync | Media | Inspección manual (`fly logs \| grep level=ERROR`) |
| `DEGRADED` inesperado repetido | pasos `DEGRADED` fuera de lo normal | Baja/Media | Inspección manual (`fly logs \| grep failure_mode=`) |

## Escalado

- **Single-maintainer**: el escalado es la notificación de GitHub Actions
  (deploy/cron) y la revisión manual. No hay on-call rotativo (coste 0 €).
- Cada alerta enlaza a su acción: release fallida → `rollback-runbook.md`;
  fallo fatal → `incident-response` (etapa 4.5).

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- CloudWatch Alarms, SNS, PagerDuty, umbrales automáticos por burn-rate →
  NO-APLICA. Documentado con su alternativa gratuita (notificación GitHub +
  `fly logs`), no inventado.

## Assumptions & Open Questions

None.
