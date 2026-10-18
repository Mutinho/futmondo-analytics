# Escalation Matrix — F1: Login nativo end-to-end

> Fase: operación (incident-response). Idioma: castellano; tokens técnicos verbatim en inglés.
> Equipo **single-maintainer**: sin rotación on-call ni PagerDuty (de pago / sin equipo). La matriz
> documenta a quién/qué recurrir en cada severidad con los medios gratuitos disponibles.

## Matriz de escalado

| Severidad | Responsable | Canal de notificación | Acción inicial | Si no se resuelve |
|-----------|-------------|-----------------------|----------------|-------------------|
| P1 | Mantenedor (propietario) | Notificación de GitHub Actions (workflow en rojo) + comprobación `/health` | Rollback (RB-4) | `fly machine stop` + diagnóstico; abrir issue |
| P2 | Mantenedor | GitHub Actions / observación `fly logs` | Runbook aplicable (RB-2/RB-3) | Rollback a última release sana |
| P3 | Mantenedor | Observación manual / reporte en el dispositivo | Reinstalar build iOS (RB-5) o fix menor | Programar fix en el siguiente PR |

## Contactos y recursos

- **Mantenedor único**: el propietario del proyecto (no se listan datos personales aquí; PII fuera
  de los artefactos). Notificaciones vía la cuenta de GitHub del repo y el panel de Fly.io.
- **Proveedores (soporte de tier gratuito)**:
  - Fly.io: estado/soporte comunitario (sin SLA de pago).
  - Neon: panel del proyecto (tier free).
  - GitHub Actions: estado del servicio.

## Rutas de escalado "automatizadas" (gratuitas)

- El gate `verify` bloqueante y el `smoke-test` actúan como primera línea: impiden que un cambio
  roto llegue a producción y marcan el workflow en rojo (notificación al mantenedor).
- No hay remediación automática (auto-rollback por métrica): sería de pago/compleja; el rollback es
  una acción manual deliberada (RB-4).

## NO-APLICA (de pago / sin equipo)

| Concepto del stage | Estado |
|---|---|
| Rotación on-call / PagerDuty | NO-APLICA (single-maintainer) |
| AWS Incident Manager | NO-APLICA; plan manual (ver `incident-plan.md`) |
| SNS / paging multi-nivel | NO-APLICA; notificación de GitHub Actions |

## Sources

- [consumes] alarms.md; incident-plan.md, runbooks.md.
- [memory] phases/operation.md (escalation paths + contactos); aidlc-shared/operation-fly-stack.md
  (escalado single-maintainer por notificación GitHub Actions); project.md (coste 0 €).

## Assumptions & Open Questions

None.
