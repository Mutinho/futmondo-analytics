<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
2026-10-18 — Observability-setup se adapta al stack Fly.io + Neon (coste 0 €): dashboards/alarms/slo/log-queries/tracing/anomaly se mapean a equivalentes gratuitos (fly logs/status, curl /health, gate verify + smoke, notificación GitHub Actions). Superficie observable = endpoints de auth de F1.

## Deviations
2026-10-18 — SLO formal con error budget/burn-rate, tracing distribuido (X-Ray) y anomaly detection ML marcados NO-APLICA (de pago), sustituidos por SLI informal, correlación por log y barreras deterministas + estados explícitos.
2026-10-18 — nfr-design e infrastructure-design `skipped` en los 3 bolts: sus artefactos consumidos no existen; la superficie observable se deriva de la app desplegada y deployment-execution, sin inventar diseño.

## Tradeoffs
2026-10-18 — Observación pull (sin dashboards/alertas gestionadas push): aceptable para single-maintainer a coste 0 €; el smoke /health + picos de 4xx/5xx en logs son la detección práctica de anomalía.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
