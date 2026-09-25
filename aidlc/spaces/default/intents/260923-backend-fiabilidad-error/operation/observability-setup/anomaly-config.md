# Anomaly Detection Configuration — Observabilidad (FR3.2 + FR4)

## Sustitución determinista (gratuita)

En lugar de detección de anomalías por ML, este intent usa **barreras
deterministas** y **estados explícitos**:

- Validación/tipado de fallo en el borde de integración (excepción tipada por
  modo de fallo).
- Estado explícito `DEGRADED` (`sync_step_status.py`) para lo recuperable; fatal
  propagado para lo que aborta. Una anomalía se ve como un `failure_mode=` o un
  `DEGRADED` inesperado en `fly logs`, no como una desviación estadística.

## NO-APLICA (coste 0 €)

- CloudWatch Anomaly Detection / detección de anomalías por ML → **NO-APLICA**
  (de pago). Documentado con su alternativa (barreras deterministas + estados
  explícitos observables en `fly logs`), no inventado.

## Assumptions & Open Questions

None.
