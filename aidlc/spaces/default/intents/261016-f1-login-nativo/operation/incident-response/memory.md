<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
2026-10-18 — Incident-response adaptado a single-maintainer + Fly.io: SSM Automation / AWS Incident Manager / AWS Backup → procedimientos manuales con flyctl reutilizando docs/ROLLBACK.md. Runbooks centrados en los modos de fallo de F1 (backend/health, login, refresh/transporte D-01, app iOS).

## Deviations
2026-10-18 — Sin rotación on-call ni remediación automática por métrica (de pago/sin equipo): escalado al mantenedor único por notificación de GitHub Actions; rollback manual deliberado (RB-4).
2026-10-18 — reliability/security-design e infrastructure-specification `skipped`: no existen; todo derivado de alarms/dashboards + docs/ROLLBACK.md + app desplegada.

## Tradeoffs
2026-10-18 — RPO = datos en Neon; el estado en memoria (TaskManager/syncs) se pierde en redeploy/rollback — limitación aceptada del entorno único. DR multi-región diferido/NO-APLICA (de pago).

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
