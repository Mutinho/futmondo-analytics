<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T19:05Z — Infrastructure Design U1: NO-APLICA infra/CI-CD nuevo. Código de librería cliente iOS; no despliega, no toca workflows; el gate de CI existente aplica al PR. Verificación `swift build && swift test` local en WSL. No se añade runner Swift (coste 0 €, fuera de alcance).
- 2026-10-20T09:36Z — Infrastructure Design U2: NO-APLICA infra/CI-CD/monitorización nuevos. UI SwiftUI cliente; no despliega ni provisiona; gate de CI existente aplica al PR. Verificación `swift build` + dispositivo (xtool). Deuda aceptada (sin runner Swift en CI) ya registrada en U1.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
