# Tracing Config — Intent 4 (gate CI/CD hardening)

> Fase Operation. El tracing distribuido (X-Ray) **NO-APLICA** en este stack a
> coste 0 € (Q4=A). Se documenta el sustituto gratuito por correlación de log
> estructurado.

## Tracing distribuido — NO-APLICA (documentado)

- **AWS X-Ray / OpenTelemetry con backend gestionado**: **NO-APLICA** (coste +
  infraestructura de collector/backend inexistente). El sistema son dos apps
  Fly.io; no hay malla de servicios que justifique tracing distribuido, y el
  intent es config-only (no cambia el runtime).

## Sustituto gratuito: correlación por log estructurado

- **Correlación por `task_id`**: los flujos de sync ya propagan un `task_id` en
  los logs estructurados; `fly logs | grep 'task_id=<id>'` reconstruye la
  secuencia de un flujo end-to-end sin un backend de tracing.
- **Campos estructurados** (`sync_step`, `reason`, nivel): permiten seguir el
  progreso paso a paso de una operación en `fly logs`.
- Es la "traza" viable a coste 0 €: correlación por campo, no spans gestionados.

## Relación con el intent

Este intent no introduce servicios nuevos ni cambia el runtime, así que no añade
ninguna necesidad de tracing nueva. La "traza" del propio gate es la secuencia de
pasos con nombre en el log de GitHub Actions (cada step es un tramo identificable
del pipeline).

## Sources

- `../../construction/nfr-design/observability-design.md` (correlación por log estructurado).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (tracing de pago NO-APLICA).

## Assumptions & Open Questions

- Tracing distribuido queda como deuda documentada; fuera de alcance por coste 0 € y por no aportar valor en una topología de dos apps sin cambios de runtime.
