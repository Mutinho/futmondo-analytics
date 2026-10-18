# Tracing Config — F1: Login nativo end-to-end

> Fase: operación (observability-setup). Idioma: castellano; tokens técnicos verbatim en inglés.
> **Tracing distribuido (X-Ray o equivalente) NO-APLICA**: es de pago y el stack es coste 0 €,
> single-maintainer, con una topología simple (una app pública + Neon). Se sustituye por
> correlación ligera vía logs estructurados. Coherente con `aidlc-shared/operation-fly-stack.md`.

## Decisión

- **No se instrumenta tracing distribuido** en F1. Rationale: (1) coste 0 € (X-Ray/APM gestionado
  es de pago); (2) la topología es plana (app → Neon), sin malla de microservicios que justifique
  spans distribuidos; (3) D-01 es un ajuste aditivo de transporte, no introduce saltos de servicio
  nuevos.

## Sustituto gratuito: correlación por log

- Para seguir una petición de auth, se usa la correlación por **campos de log estructurado**
  (p. ej. `endpoint`, `status` y, donde exista, `task_id`) filtrando con `fly logs | grep`
  (ver `log-queries.md`).
- Si en el futuro se necesitara trazar un flujo multi-paso (p. ej. sync), la vía gratuita es añadir
  un identificador de correlación a los logs de ese flujo, no un tracer gestionado.

## NO-APLICA (de pago)

| X-Ray / stage | Estado |
|---|---|
| Tracing distribuido (spans, service map) | NO-APLICA (de pago; topología plana) |
| APM gestionado | NO-APLICA (coste 0 €) |

## Sources

- [consumes] performance-design.md, infrastructure-specification.md — NO existen (`skipped`);
  derivado de la topología real.
- [memory] aidlc-shared/operation-fly-stack.md (X-Ray → correlación por log, diferido/NO-APLICA);
  project.md (coste 0 €).

## Assumptions & Open Questions

None.
