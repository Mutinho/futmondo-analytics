<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T11:23Z — U2 functional-design (UI-only): revestir LoginView de F1 con componentes/tokens de U1 (TextInputField, PrimaryButton, ErrorState, Card, DSColor.splashGradient) preservando AuthViewModel y todos los flujos. Tabla de equivalencia antes→después; sin entities/rules propias; ACs de US4.1 como N/A (lógica de F1, verificación en functional-spec W1 + dispositivo).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
None.
