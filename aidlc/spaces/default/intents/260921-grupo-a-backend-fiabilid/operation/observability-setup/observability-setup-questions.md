# Preguntas — Observability Setup (Fiabilidad de la sync)

> Conversation language: Spanish. Fase Operation. **Adaptación de stack** (regla
> afirmada en `project.md`): el stage asume AWS (CloudWatch/X-Ray/SNS), pero el
> stack real es **Fly.io + Neon** a coste 0 €. Se genera la observabilidad con
> herramientas gratuitas (`fly logs`, healthcheck `/health`, logging
> estructurado) y se marca **NO-APLICA/diferido** lo que exige servicios de pago
> (SLOs formales con burn-rate, tracing distribuido, anomaly detection ML).
> Respuestas determinadas por el stack real (Operation: preguntas excepcionales).

## Q1 — ¿Señales de oro a monitorizar (latencia, tráfico, errores, saturación)?

A. Errores/fiabilidad de la sync (pasos `degraded`) + disponibilidad (`/health`); latencia/saturación por `fly logs` sin dashboards de pago
B. Suite completa de golden signals con dashboards
X. Other (please specify)

[Answer]: A. El foco de este intent es la **fiabilidad observable de la sync**: los pasos `degraded` emiten un `logger.warning` estructurado (`sync_step`, `reason`) visible en `fly logs`. Disponibilidad vía `/health`. Latencia/tráfico/saturación se observan puntualmente por `fly logs`/`fly status`, sin dashboards de pago.

## Q2 — ¿SLOs/SLIs definidos?

A. Sin SLOs formales con burn-rate (NO-APLICA: requieren servicio de métricas de pago); SLI informal = `/health` 200 y ausencia de pasos `degraded` inesperados
B. SLOs formales con ventanas y burn-rate
X. Other (please specify)

[Answer]: A. NO se definen SLOs formales con burn-rate (exigen un backend de métricas de pago; fuera del mandato coste 0 €). SLI informal observable: `/health` responde 200 y los pasos de sync no quedan `degraded` de forma inesperada (visible en `fly logs`). Se marca diferido.

## Q3 — ¿Layouts de dashboards?

A. Sin dashboards gestionados (NO-APLICA: servicio de pago); se documentan consultas de `fly logs` equivalentes
B. Dashboards en CloudWatch/Grafana Cloud
X. Other (please specify)

[Answer]: A. Sin dashboards de pago. Se documentan consultas/filtros de `fly logs` que dan la misma señal (ver `log-queries.md`).

## Q4 — ¿Retención y agregación de logs?

A. Retención por defecto de `fly logs` (streaming/ventana corta); sin agregación de pago
B. Agregación gestionada (Loki/CloudWatch Logs)
X. Other (please specify)

[Answer]: A. `fly logs` (streaming; retención corta por defecto de la plataforma). Sin agregación gestionada de pago. Coste 0 €. El logging estructurado del intent facilita filtrar por `sync_step`/`reason`.

## Q5 — ¿Instrumentación de tracing distribuido?

A. NO-APLICA (tracing distribuido requiere servicio de pago); se difiere
B. Sí (OpenTelemetry + backend de trazas)
X. Other (please specify)

[Answer]: A. NO-APLICA / diferido. El tracing distribuido exige un backend de trazas de pago; fuera del mandato coste 0 €. La correlación de un fallo de sync se hace por el log estructurado (`sync_step`, `reason`) en `fly logs`.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
