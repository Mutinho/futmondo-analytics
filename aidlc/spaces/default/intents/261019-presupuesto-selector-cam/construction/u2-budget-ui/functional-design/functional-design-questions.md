# Functional Design — Questions (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Functional Design de U2 `u2-budget-ui` (capa SwiftUI en `FutmondoApp`, bajo `#if canImport(SwiftUI)`):

- `RootTabView`: `TabView` con una pestaña "Presupuesto" (Liquid Glass iOS 26) + `NavigationStack`.
- `BudgetViewModel` (`@Observable @MainActor`): inyecta servicios/store/resolver de U1; estado `loading/loaded/empty/error`; `load()` resuelve el activo con `ActiveChampionshipResolver` y persiste si cambió (owner FR3.3); `selectChampionship`, `setSort`.
- `BudgetView`: `.toolbar` con `ChampionshipMenu` (título) + `SortMenu`; cuerpo por estado (`LoadingState`/`ErrorState`/vacío/`List` de `BudgetRow`).
- `BudgetRow`: 4 métricas (`balance`/`performance` con tokens de dinero vía `MoneyFormatter`, `max_bid`, `prizes`), label VoiceOver.
- Verificación: `swift build` (guardado por `#if canImport(SwiftUI)`) + validación en iPhone 13 Pro (render/accesibilidad/fidelidad); sin XCTest de vistas en WSL. Consume U1 (ya testeada).

¿Does this all look correct?

[Answer]: Looks correct
