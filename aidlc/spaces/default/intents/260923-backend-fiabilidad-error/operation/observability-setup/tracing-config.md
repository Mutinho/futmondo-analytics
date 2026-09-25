# Tracing Configuration — Observabilidad (FR3.2 + FR4)

## Correlación (gratuita) en lugar de tracing distribuido

- **`task_id`** es el correlador: todos los logs de un sync comparten `task_id`,
  de modo que `fly logs | grep task_id=<ID>` reconstruye el hilo del sync entre
  pasos. Es la sustitución a coste 0 € del tracing distribuido.

## NO-APLICA (coste 0 €)

- Tracing distribuido gestionado (AWS X-Ray, Jaeger, Zipkin, OpenTelemetry
  backend) → **NO-APLICA** (de pago / infraestructura adicional). Documentado con
  su alternativa gratuita (correlación por `task_id` en `fly logs`), no inventado.
- No se instrumenta W3C Trace Context ni sampling: fuera de alcance y de
  presupuesto.

## Assumptions & Open Questions

None.
