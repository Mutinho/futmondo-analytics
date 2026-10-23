<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T13:24Z — Feasibility: viable, sin bloqueantes. Cimientos de F1 (red/auth en `FutmondoKit`, tokens de diseño) + endpoints existentes sin cambios de backend cubren casi todo. Riesgo dominante = patrón de navegación del selector sin sidebar (Q1-A menú en navigation bar), validable en dispositivo. Riesgo secundario = formateo de dinero M/K (lógica pura testeable). Coste 0 €. 8 restricciones duras registradas (C-01..C-08).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
