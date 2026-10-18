<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
2026-10-16 — F1 tiene dos canales de despliegue (backend D-01 por CD on-merge a Fly.io; app iOS por firma gratuita con xtool, manual). Se documentan ambos en vez de asumir un único pipeline.
2026-10-16 — D-01 es aditivo y retrocompatible por precedencia (cookie→header→body): NO necesita feature flag ni ventana de migración; cliente viejo (PWA) y nuevo (iOS) conviven en la misma release.

## Deviations
2026-10-16 — Los artefactos consumidos infrastructure-specification.md y cicd-pipeline.md NO existen (infrastructure-design se reportó `skipped` en los 3 bolts): se documenta la ausencia y se toma la topología real de fly-deploy.yml + team.md, sin inventar infra (regla: diseñar solo contra evidencia).
2026-10-16 — No hay review adversarial en esta etapa (support_agents vacío, collaborators off); sensores aplicables solo required-sections + upstream-coverage.

## Tradeoffs
2026-10-16 — Sin blue/green ni canary: entorno único Fly.io tier gratuito (coste 0 €). El smoke /health sustituye al staging; se acepta el tradeoff documentado en team.md.
2026-10-16 — Publicación App Store diferida (B-09): requiere Apple Developer Program de pago (excepción acotada). F1 se queda en firma gratuita ~7 días (reinstalación periódica).

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
