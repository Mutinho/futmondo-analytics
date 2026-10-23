# Observability Setup — Preguntas

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés. Sin decisiones nuevas.

## Consolidated Summary Confirmation

Resumen de Observability Setup:

- **Capa de diseño cliente iOS sin servicio que observar**: dashboards, alarms, SLO, log-queries, tracing y anomaly detection **NO-APLICAN** (adaptado al stack real, sin AWS/CloudWatch; coste 0 €).
- **Salud de la UI**: observación manual en el iPhone 13 Pro; sin telemetría de cliente de pago.
- **Producción Fly.io/Neon**: observabilidad heredada (`fly logs`, `/health`) no modificada.

¿Does this all look correct?

[Answer]: Looks correct
