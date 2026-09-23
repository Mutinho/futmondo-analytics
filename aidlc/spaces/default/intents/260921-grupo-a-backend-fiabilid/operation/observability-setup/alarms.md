# Alarmas — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: Fly.io + Neon, coste
> 0 €. Sin CloudWatch Alarms ni SNS (servicios de pago).

## Alarmas efectivas a coste 0 €

| Alarma | Disparador | Mecanismo gratuito | Severidad | Acción |
|---|---|---|---|---|
| Release no sano | `smoke-test` `/health` ≠ 200 tras deploy | job `smoke-test` de `fly-deploy.yml` (falla el workflow) | Alta | rollback (`rollback-runbook.md`) |
| App caída / reinicios | healthcheck de Fly.io en rojo | `fly status` / notificación de la plataforma | Alta | investigar `fly logs`; rollback si procede |
| Paso de sync degradado | `logger.warning "sync step degraded"` | inspección de `fly logs` (bajo demanda / tras sync) | Media | revisar `reason`; relanzar sync si aplica |

- El único gate automático real es el `smoke-test` post-deploy: convierte un
  release no sano en un fallo de workflow visible. El resto es observación por
  `fly logs`/`fly status` (pull), no alertas push.

## NO-APLICA / diferido (servicios de pago)

- Alarmas gestionadas con umbrales, ruteo SNS/PagerDuty y escalado automático:
  se difieren (exigen servicio de alertas de pago). En su lugar, el healthcheck
  de Fly.io y el `smoke-test` cubren la señal crítica de disponibilidad a coste
  0 €.

## Escalado (manual, coste 0 €)

- El fallo del `smoke-test` o un `/health` en rojo escala a la persona de
  guardia del proyecto (single-maintainer); el runbook de rollback es la primera
  acción. (Ver `incident-response` para el detalle de contactos/escalado.)

## Sources

- `.github/workflows/fly-deploy.yml` (smoke-test), `operation/deployment-pipeline/rollback-runbook.md`,
  `construction/sync-reliability/functional-design/functional-spec.md`.

## Assumptions & Open Questions

None.
