<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T16:27Z — Units Generation: 2 unidades (mismo patrón limpio que F1). U1 `u1-budget-data` (library, sin deps nuevas): DTOs + MoneyFormatter + TeamBudgetSort + BudgetService/ChampionshipService + ActiveChampionshipStore, checkpoint `swift test`. U2 `u2-budget-ui` (ui, depende de U1): RootTabView + BudgetView/BudgetViewModel + BudgetRow + ChampionshipMenu, checkpoint `swift build` + validación en dispositivo. Sin ciclos; U1 primero. traceability.json cubre unidad→US/FR.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
