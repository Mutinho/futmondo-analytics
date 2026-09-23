# Informe de SLO — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: Fly.io + Neon, coste
> 0 €. SLO formal con burn-rate NO-APLICA/diferido; se informa el SLI informal.

## Cumplimiento del SLI informal

| SLI | Estado | Evidencia |
|---|---|---|
| Disponibilidad backend (`/health` 200) | Cumplido | `smoke-test` de release + `curl` puntual |
| Fiabilidad de la sync (sin `degraded` inesperado) | Observable y sano | `fly logs` (`sync step degraded`) — antes del intent, invisible |

## Error budget / burn-rate

- **NO-APLICA**: no hay SLO cuantificado con ventana temporal ni backend de
  métricas de pago para computar burn-rate (diferido, ver
  `observability-setup/slo-config.md`). No hay error budget que quemar.

## Efecto del intent sobre la fiabilidad

- **Mejora directa de la señal (NFR1)**: antes, un paso non-critical que fallaba
  se registraba como `done` (éxito falso), corrompiendo cualquier medida de
  fiabilidad. Ahora queda `degraded` con `reason` y log estructurado, de modo
  que la fiabilidad de la sync es por fin **medible** (aunque sea de forma
  informal por `fly logs`). Este intent es un prerrequisito para cualquier SLO
  de sync futuro.

## Sources

- `operation/observability-setup/slo-config.md`,
  `operation/deployment-execution/health-check-report.md`,
  `operation/performance-validation/nfr-validation-matrix.md` (NFR1).

## Assumptions & Open Questions

None.
