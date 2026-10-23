# Observability Setup — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés. Adaptado al stack real (no AWS/CloudWatch), coste 0 €.

## Contexto

La capa de diseño es **cliente iOS** embebido en la app; no es un servicio desplegado que emita métricas/logs de servidor. La observabilidad formal (dashboards, SLO con burn-rate, tracing distribuido, anomaly detection) NO-APLICA a esta capa y, para el proyecto, se sostiene con herramientas gratuitas del stack real (Fly.io) sin inventar infraestructura.

## Dashboards

NO-APLICA: sin servicio nuevo que dashboard-ear. Los dashboards/observabilidad del backend/frontend en Fly.io son estado heredado y no cambian.

Ver también: `alarms.md`, `slo-config.md`, `log-queries.md`, `tracing-config.md`, `anomaly-config.md`.

## Assumptions & Open Questions

None.
