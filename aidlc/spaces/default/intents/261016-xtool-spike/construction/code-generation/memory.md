<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-16T18:03:00Z — Spike de toolchain zero-Unit: el "código" son artefactos listos para ejecución en vivo (app SwiftUI trivial + xtool.yml + scripts setup/smoke + runbook). La ejecución real (build/firma/install en el iPhone) se difiere a una sesión interactiva porque requiere dispositivo físico, Apple ID y USB passthrough.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-16T18:03:00Z — Sin suite automatizada nueva: la cadena xtool no es automatizable como CI a coste 0 €; verificación = smoke manual en dispositivo. Suite existente del repo intacta (confirmado por git: 0 cambios en backend/ y angular-app/).
- 2026-10-16T18:03:00Z — Step 7 del plan sin tick: la ejecución efectiva de la suite es trabajo de Build and Test; aquí sólo se confirma que no se tocó código de app.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
