<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T13:12Z — F2 intent capturado leyendo la fuente de verdad real (`budget-overview` + `championship.service.ts`). Decisiones (Guíame, A en todo): selector = menú en navigation bar (Q1 A); Presupuesto lista solo-lectura con todas las métricas de `TeamBudget`, detalle/premios como follow-up (Q2 A); solo cards/list nativa sin toggle (Q3 A); con ordenación por las mismas claves vía menú toolbar (Q4 A); cambio de campeonato recarga + persiste en `UserDefaults` (Q5 A). Asunciones aceptadas: endpoints existentes sin cambios de backend, formato de dinero como la web, sesión F1 intacta, coste 0 €.
- 2026-10-19T13:20Z — Tras review advisory READY del product-lead, aplicados findings 1–3 al intent-statement (criterio verificable del selector: `UserDefaults` + recarga; ordenación Q4 y formato M/K al bloque "Qué entra"; validación en iPhone 13 Pro marcada como supuesto/riesgo arrastrado de F1). Finding 4 (precisar mínimo de navegación) dejado explícito en "Qué NO entra" para scope-definition. Re-pase de reviewer iteración 2 por cambio en artefacto `produces`.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
