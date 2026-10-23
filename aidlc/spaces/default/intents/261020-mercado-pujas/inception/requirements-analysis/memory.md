<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-20 — 8 FR (FR1 pestaña, FR2 carga/estados, FR3 banner, FR4 cards, FR5 orden, FR6 pujar, FR7 cancelar, FR8 Sofascore Should) + 6 NFR, trazados a Ideación (M1–M7, S1–S2) y a los contratos reales de Reverse Engineering. Tope de importe UI = available_for_bids; el tope absoluto del backend (5e9) queda como barrera de servidor, no se replica en UI (Q1=A).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-20 — Reviewer advisory (product-lead, 1 iter) sobre requirements: READY, 1 Major + 2 Minor aplicados. Major: trazas corregidas de IDs inexistentes (D1–D4/D9) a los reales de Ideación (Q1–Q4, C1–C9). Minor 1: nota explícita de divergencia del tope de puja (available_for_bids vs max_bid del Angular, intencionada por Q1=A). Minor 2: mapeo de códigos HTTP (2xx success true/false, 422/400, 5xx) a los desenlaces aceptada/rechazada/error en FR6.4 y FR7.3.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
