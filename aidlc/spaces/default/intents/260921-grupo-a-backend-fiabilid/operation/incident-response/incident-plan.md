# Plan de respuesta a incidentes — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: Fly.io + Neon,
> single-maintainer, coste 0 €. Sin AWS Incident Manager ni status page de pago.

## Clasificación de severidad

| Sev | Definición | Ejemplo | Respuesta |
|---|---|---|---|
| P1 | Servicio caído / datos en riesgo | `/health` en rojo sostenido; Neon inaccesible | Rollback inmediato (RB-1/RB-4); revisión post-incidente obligatoria |
| P2 | Degradación funcional relevante | sync deja resultados incompletos de forma recurrente | Diagnóstico por `fly logs`; fix por PR; revisión post-incidente obligatoria |
| P3 | Fallo acotado / no crítico | un paso `degraded` puntual y transitorio | Relanzar sync; anotar `reason`; sin revisión formal salvo recurrencia |

## Ciclo de vida del incidente

1. **Detección**: workflow de deploy en rojo (`verify`/`smoke-test`), `/health`
   en rojo, o hallazgo en `fly logs` (`sync step degraded`).
2. **Triage**: clasificar severidad (tabla) y aplicar el runbook correspondiente
   (`runbooks.md`).
3. **Mitigación**: rollback (`rollback-runbook.md`) o relanzar sync según el caso.
4. **Resolución**: PR con el fix real; gate de CI (gitleaks + pytest + ng test)
   verde antes de fusionar. Nunca push directo a `main`.
5. **Post-incidente (P1/P2, obligatorio)**: registrar timeline, causa raíz y
   prevención en una nota/issue del repo.

## Comunicación

- Single-maintainer: la "comunicación" es la nota de incidente en el repo y el PR
  del fix. Sin status page de pago ni comms multi-canal.

## RTO / RPO (informales)

- **RTO** ≈ minutos: `fly releases rollback <vN>` + verificación `/health`.
- **RPO** = último estado persistido en Neon (durable). El estado en memoria
  (`TaskManager`, syncs en curso) NO es durable y se pierde en el redeploy
  (limitación conocida y aceptada; su solución excede este intent).

## NO-APLICA / diferido

- AWS Incident Manager, on-call rotations gestionadas, status page, DR
  automatizada: servicios de pago; diferidos. El plan manual de arriba cubre la
  operación del intent a coste 0 €.

## Sources

- `runbooks.md`, `escalation-matrix.md`,
  `operation/deployment-pipeline/rollback-runbook.md`,
  `operation/observability-setup/alarms.md`, `phases/operation.md`
  (post-incident reviews P1/P2).

## Assumptions & Open Questions

None.
