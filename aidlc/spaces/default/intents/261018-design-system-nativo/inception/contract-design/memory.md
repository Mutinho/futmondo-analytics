<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T10:03Z — Único boundary U2→U1 como API pública de librería Swift in-process (Q1=A), no API de red. Contrato = superficie pública (colors/typography/spacing/components) con garantía de accesibilidad. Sin versionado formal (Q2=A): mismo repo, el compilador obliga a arreglar consumidores; aditivos no rompen.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-19T10:03Z — El spec no es OpenAPI/AsyncAPI (no aplica a consumo in-process); se usa un shared-schema que describe la superficie pública Swift.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-19T10:03Z — Nombres finales de símbolos públicos de U1 a fijar en functional-design/code-generation.
