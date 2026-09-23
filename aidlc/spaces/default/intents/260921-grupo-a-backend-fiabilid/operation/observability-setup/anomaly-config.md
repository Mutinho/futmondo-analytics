# Configuración de detección de anomalías — Fiabilidad de la sync

> Conversation language: Spanish. **Adaptación de stack**: anomaly detection ML
> **NO-APLICA/diferido** (requiere servicio de métricas/ML de pago). Coste 0 €.

## Estado: NO-APLICA / diferido

- La detección de anomalías basada en ML (CloudWatch Anomaly Detection o
  equivalente) requiere series temporales de métricas historizadas y un servicio
  de análisis de pago. Queda **diferida** conforme al mandato de coste 0 € y a la
  regla de adaptación de stack de `project.md`.

## Sustituto determinista y gratuito

- **Umbral fijo en vez de ML**: el propio intent introduce una barrera
  determinista (el techo `PRICE_SANITY_CAP`, FR6) que rechaza con 422 un `price`
  fuera de rango — una "detección de anomalía" de entrada, sin ML, aseverada por
  test.
- **Señal de degradación explícita**: un paso de sync anómalo (que falla) queda
  marcado `degraded` con `reason` en `fly logs`, en vez de detectarse por
  desviación estadística. La anomalía se hace observable por construcción
  (FR3.1/NFR1), no por inferencia ML.

## Sources

- `construction/sync-reliability/functional-design/functional-spec.md` (FS2/FS3),
  `inception/requirements-analysis/requirements.md` (FR6, NFR1),
  `project.md` (adaptación de stack Operation + coste 0 €).

## Assumptions & Open Questions

None.
