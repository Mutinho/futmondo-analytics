# Configuración de tracing — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: tracing distribuido
> **NO-APLICA/diferido** (requiere un backend de trazas de pago). Coste 0 €.

## Estado: NO-APLICA / diferido

- El tracing distribuido (X-Ray, OpenTelemetry + backend de trazas como Jaeger
  gestionado/Tempo/Honeycomb) exige un servicio de recolección/almacenamiento de
  trazas de pago. Queda **diferido** conforme al mandato de coste 0 € y a la
  regla de adaptación de stack de `project.md`.
- Además, el intent es una intervención backend acotada dentro de un único
  servicio (`futmondo-api`); no introduce un flujo cross-servicio nuevo que
  justifique trazas distribuidas.

## Alternativa gratuita vigente

- **Correlación por log estructurado**: para diagnosticar un fallo de sync se
  usa el `logger.warning` estructurado (`sync_step`, `reason`) en `fly logs`
  (ver `log-queries.md`), que localiza el paso y el motivo sin necesidad de
  trazas distribuidas.
- El identificador de tarea (`task_id`) presente en `progress` permite seguir
  una ejecución de sync concreta a través de sus pasos en los logs.

## Sources

- `construction/sync-reliability/functional-design/functional-spec.md`,
  `project.md` (adaptación de stack Operation + coste 0 €).

## Assumptions & Open Questions

None.
