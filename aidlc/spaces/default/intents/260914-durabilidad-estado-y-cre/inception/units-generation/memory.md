<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-15T15:12:00Z — CredentialProtection queda DENTRO de U1 (no unidad propia): se consume en la sesión y no se despliega por separado. Su interfaz es un límite intra-unidad formalizado en Contract Design (2.8), no una arista del DAG. Por eso el DAG queda sin aristas (U1 y U2 independientes).
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-15T15:17:00Z — Tras la revisión advisory se corrigieron dos hallazgos Minor: R-02 (alinear cita de preguntas a Q2-A/Q3-B en unit-of-work.md) y R-03 (añadir NFR5 transversal U1+U2 a traceability.json). R-01 (nota de orden intra-unidad en el story-map) se mantiene deliberadamente: el stage file permite "story implementation order within each unit".
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
