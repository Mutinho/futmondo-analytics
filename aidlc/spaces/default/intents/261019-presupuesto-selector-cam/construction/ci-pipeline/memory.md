<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-20T10:04Z — CI Pipeline: NO-APLICA cambios de CI. El gate bloqueante existente aplica al PR tal cual y queda en verde (F2 no toca backend/frontend Angular); gitleaks escanea el Swift nuevo. Verificación del código iOS (`swift build && swift test` 87 verde + dispositivo) es local/manual; sin runner Swift en CI (deuda aceptada, follow-up). Ningún umbral modificado.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-20T12:43Z — CI Pipeline re-confirmado tras el re-trabajo de U2: sin cambios respecto al estado previo. NO-APLICA cambios de CI; el gate bloqueante existente aplica al PR de F2 (que ahora incluye FR6 detalle) y sigue en verde (F2 no toca backend/frontend Angular). Verificación del código iOS (`swift build && swift test` = 105 verde + dispositivo) local/manual; sin runner Swift en CI (deuda aceptada). Ningún umbral modificado.