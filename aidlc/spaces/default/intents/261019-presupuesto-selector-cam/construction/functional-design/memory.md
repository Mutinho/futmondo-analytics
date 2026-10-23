<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-19T17:16Z — Functional Design U1 `u1-budget-data`: superficie pública (DTOs Codable/Sendable con CodingKeys snake_case; `SortKey`; `MoneyFormatter`; `TeamBudgetSort`; protocolos `BudgetService`/`ChampionshipService`/`ActiveChampionshipStore` + impls HTTP/UserDefaults). Reglas R1-R6 (formato dinero, orden descendente estable, fallback de endpoints, resolución de activo, seguridad). Casos a testear con `NetworkClient` fake (patrón F1) + `UserDefaults` de suite de test. Walking skeleton OFF reportado. Autonomía de construcción se propone en este punto (offer_autonomy true).
- 2026-10-19T17:37Z — Review adversarial iteración 1 = NOT-READY (2 Major + 4 Minor). Resueltos: (M1) `MoneyFormatter` determinista e independiente de locale (separador `,` fijo, signo ASCII `-`, half-away-from-zero por aritmética entera, sin `NumberFormatter`); (M2) añadida función pura `ActiveChampionshipResolver.resolve(activeId:in:)` a la superficie de U1 (owner de persistencia = `BudgetViewModel` de U2); (m3) borde del redondeo definido; (m4) glifo de signo fijado ASCII; (m5) `SortKey`+`ActiveChampionshipResolver` en traceability; (m6) fallback dispara con cualquier throw (incl. decode). Re-pase iteración 2.
- 2026-10-20T09:16Z — Functional Design U2 `u2-budget-ui` (SwiftUI, bajo `#if canImport(SwiftUI)`): `RootTabView` (TabView 1-pestaña Liquid Glass), `BudgetViewModel` (@Observable @MainActor, estado loading/loaded/empty/error, inyecta servicios/store/resolver de U1, owner de persistir el id resuelto), `BudgetView` (toolbar con `ChampionshipMenu` + `SortMenu`, cuerpo por estado), `BudgetRow` (4 métricas + tokens de dinero, label VoiceOver), `ChampionshipMenu`/`SortMenu`. Verificación `swift build` + dispositivo (sin XCTest de vistas en WSL). Consume U1 ya testeada.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
