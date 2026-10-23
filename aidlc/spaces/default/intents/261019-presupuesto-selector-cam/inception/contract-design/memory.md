<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T16:55Z — Contract Design: contratos backend (balances + championships con fallback, sin cambios), superficie pública de U1 (protocolos `BudgetService`/`ChampionshipService`/`ActiveChampionshipStore` + `MoneyFormatter`/`TeamBudgetSort` + tipos `Codable`), y consumo de U2 (VM con inyección por protocolo, estado `BudgetState` loading/loaded/empty/error). Campos extra de championship como opcionales para tolerar el endpoint legacy. Invariantes: sin credenciales en API, cero deps, sin cambios de backend.
- 2026-10-19T16:57Z — Tras review advisory READY (3 Minor): aclarado el conteo de `TeamBudget` en contract-summary (12 propiedades reales; "9 campos" = métricas de negocio mostrables; 4 visibles en fila). Findings 2 (FR3.3 owner VM vs store) y 3 (narrowing de championship_id a obligatorio en cliente) se dejan para construcción/code-generation. Re-pase reviewer iteración 2 por cambio en contract-summary.md.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
