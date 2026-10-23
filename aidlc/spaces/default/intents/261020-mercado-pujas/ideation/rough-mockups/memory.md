<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-20 — Wireframes de baja fidelidad fieles a la vista Angular (banner + cards + orden + puja/cancelar + Sofascore), con tema oscuro/neón y NeonGlassCard de F1/F2. Diálogos y detalle como sheets (HIG, patrón F2). User flow con señal aceptada/rechazada/error + recarga tras escritura; botones deshabilitados durante la operación.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-20 — Reviewer advisory (product-lead, 1 iter) sobre wireframes: READY, 0 Major, 3 Minor aplicados: (1) enumerados los 7 campos de orden junto al selector; (2) añadido estado de validación "vacía/≤0" al sheet de puja; (3) dibujado el glifo ↗/↘ + signo en el grid TENDENCIA (no-sólo-color visible en el artefacto).

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
