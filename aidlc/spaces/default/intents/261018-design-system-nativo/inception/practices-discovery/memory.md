<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-18T17:19Z — Re-run de proyecto maduro: reafirmación pura del baseline afirmado (trunk-based + squash, CI gate bloqueante, walking skeleton OFF, test-after, deploy Fly.io on-merge, coste 0 €, idioma código inglés/usuario castellano). Matiz nativo añadido: tema de Angular como fuente de verdad del diseño SwiftUI, Stitch descartado, Apple HIG de relleno.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-18T17:19Z — Q1=A: el testing de UI nativa (XCTest/snapshot) se documenta como riesgo/deuda, NO se compromete arnés nuevo en este intent de capa de diseño; backend pytest y gates de CI del repo no cambian. Se decide cuando haya pantallas de datos (F2).

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-18T17:19Z — Arnés de test de UI nativo y su umbral: diferido a F2 / intent de tooling.
