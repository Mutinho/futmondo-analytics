<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T12:16Z — Build and Test: `swift build` OK, `swift test` 43/0 sin regresión (14 U1 + 29 F1). Cross-unit gate PASS: FR1–FR6 + NFR1–NFR4 cubiertos (U1 tokens/componentes/catálogo, U2 login revestido). Targets de UI/dispositivo (render 60fps, VoiceOver/Dynamic Type, fidelidad visual, cadena de foco) Unverified-local → validación manual en iPhone 13 Pro (no medible en WSL). `ios/.build/` ya gitignored (línea 41), el aviso era ruido del escaneo.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
