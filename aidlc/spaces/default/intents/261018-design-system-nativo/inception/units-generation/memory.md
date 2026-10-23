<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T09:58Z — Dos Units (Q1=A): U1 `u1-design-system` (library: tokens+componentes+catálogo) y U2 `u2-login-theming` (ui: revestir F1), con U2→U1. Embebido en la app iOS SwiftPM (Q2=A); sin paralelismo (Q3=A). Edge block YAML cycle-free. Story map: U1 cubre US1.1–US3.1, U2 cubre US4.1.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-19T09:58Z — Walking skeleton OFF (sistema en producción): no se da forma de "slice integrado" a la primera Unit; U1 es la librería base por dependencia natural.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
None.
