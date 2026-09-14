<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-14T12:56:00Z — Los unit tests pasan (6/6 con Vitest, no regresión), pero `ng build` de producción falla por el presupuesto de bundle inicial (1.03 MB > maximumError 1 MB en angular.json). Ese presupuesto y el tamaño del bundle son PREEXISTENTES (git diff confirma que solo cambié runner karma->vitest y quité browsers; no toqué budgets). El fallo es deuda anterior, ajena a las 5 mejoras de CI/tooling; debilitar el presupuesto está prohibido. Escalado a halt-and-ask (gated).
## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
