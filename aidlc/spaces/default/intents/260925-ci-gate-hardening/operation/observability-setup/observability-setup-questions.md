# Observability Setup — Preguntas (Intent 4: gate CI/CD hardening)

> Etapa final del scope infra, fase Operation. El conocimiento asume
> CloudWatch/X-Ray/SLO con burn-rate; se adapta al stack real (Fly.io + Neon +
> GitHub Actions, coste 0 €) y al carácter config-only del intent. La
> observabilidad relevante es la **de la señal del gate endurecido** más los
> healthchecks de runtime existentes; se marca NO-APLICA lo de pago (SLO formal
> con burn-rate, tracing distribuido, anomaly detection ML), documentando la
> alternativa gratuita (regla afirmada, learned 2026-09-16).

---

## Q1 — Golden signals a observar

¿Qué señales se observan, dado que el intent no cambia el runtime?

- A. **Señales del gate + healthchecks existentes**: para el gate — pass/fail por
  paso con nombre (log de Actions), cobertura en ambos gates, findings de
  audit/lint, caducidad de la allowlist, minutos de Actions (coste); para el
  runtime (sin cambios) — `/health` 200 (disponibilidad), no-200/fallo de smoke
  test (error). Traffic/saturation de la app quedan como observación existente
  (`fly status`), sin instrumentación nueva.
- B. Instrumentar los 4 golden signals completos con un servicio de métricas.
- X. Other (please specify)

[Answer]: A

---

## Q2 — SLO/SLI (`slo-config.md`)

¿Cómo se configura el SLO/SLI a coste 0 €?

- A. **SLI informal, SLO formal NO-APLICA**: sin motor de SLO con burn-rate
  alerting (de pago). SLI informal: `/health` 200 por release (disponibilidad),
  reproducibilidad y no-flapping del gate, cobertura de rutas hacia `main` (PR +
  push). Documentar como SLI observable con log de Actions/`fly logs`, marcando
  el SLO formal con ventana y burn-rate como NO-APLICA/diferido.
- B. Definir SLOs formales con burn-rate y error budget.
- X. Other (please specify)

[Answer]: A

---

## Q3 — Dashboards (`dashboards.md`)

¿Qué "dashboards" a coste 0 €?

- A. **Vistas gratuitas existentes**: la vista de checks del PR/commit en GitHub
  (estado del gate por paso), el panel de billing de Actions (minutos), y
  `fly status`/`fly logs` para runtime. Sin dashboards dedicados de pago
  (CloudWatch/Grafana). Documentar qué mirar y dónde.
- B. Crear dashboards dedicados en un servicio de observabilidad.
- X. Other (please specify)

[Answer]: A

---

## Q4 — Alarmas y tracing/anomaly (`alarms.md`, `tracing-config.md`, `anomaly-config.md`)

¿Cómo se resuelven alarmas, tracing y anomaly a coste 0 €?

- A. **Alarmas = fallos bloqueantes del gate + smoke test, vía notificación de
  Actions** (single-maintainer, sin PagerDuty/SNS); **tracing distribuido =
  NO-APLICA** (de pago), sustituido por correlación de log estructurado +
  `task_id` en `fly logs`; **anomaly detection ML = NO-APLICA** (de pago),
  sustituido por barreras deterministas (allowlist con caducidad, piso de
  cobertura, pins). Documentar el equivalente gratuito y marcar NO-APLICA lo de
  pago.
- B. Configurar alarmas SNS/PagerDuty, X-Ray y CloudWatch Anomaly Detection.
- X. Other (please specify)

[Answer]: A

---

## Q5 — Log queries (`log-queries.md`)

Las CloudWatch Logs Insights queries del conocimiento no aplican. ¿Qué se
documenta?

- A. **Consultas equivalentes con las herramientas gratuitas**: patrones de
  `grep`/filtro sobre `fly logs` (por `sync_step`, `reason`, `task_id`, nivel de
  log) para el runtime, y filtros sobre el log de GitHub Actions para el estado
  del gate (paso fallido, finding de audit, entrada de allowlist caducada).
  Marcar NO-APLICA las Logs Insights de pago, documentando la alternativa.
- B. Escribir CloudWatch Logs Insights queries.
- X. Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de las decisiones de Observability Setup (config-only; adaptado a
Fly.io + GitHub Actions coste 0 EUR; NO-APLICA lo de pago):

- **Q1 — Golden signals (A)**: señales del gate (pass/fail por paso, cobertura,
  audits/lint, caducidad allowlist, minutos de Actions) + healthchecks existentes
  (`/health`, no-200); sin instrumentacion nueva.
- **Q2 — SLO/SLI (A)**: SLI informal (`/health` 200 por release, reproducibilidad
  y no-flapping del gate, cobertura de rutas PR+push); SLO formal con burn-rate
  NO-APLICA/diferido (de pago).
- **Q3 — Dashboards (A)**: vistas gratuitas existentes (checks de GitHub, billing
  de Actions, `fly status`/`fly logs`); sin dashboards dedicados de pago.
- **Q4 — Alarmas/tracing/anomaly (A)**: alarmas = fallos bloqueantes del gate +
  smoke test via notificacion de Actions (single-maintainer); tracing distribuido
  y anomaly ML NO-APLICA, sustituidos por log estructurado + `task_id` y barreras
  deterministas (allowlist con caducidad, piso, pins).
- **Q5 — Log queries (A)**: `grep`/filtros sobre `fly logs` (runtime) y el log de
  Actions (estado del gate); CloudWatch Logs Insights NO-APLICA.

Se generaran 6 artefactos: `dashboards.md`, `alarms.md`, `slo-config.md`,
`log-queries.md`, `tracing-config.md`, `anomaly-config.md`, respetando el mandato
coste 0 EUR, la adaptacion Fly.io/GitHub Actions y todas las reglas afirmadas.

[Answer]: Looks correct
