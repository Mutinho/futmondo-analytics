# Domain Design — Questions (F2)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Domain Design:

- **Lógica pura en `FutmondoKit`** (testeable con `swift test`): DTOs `TeamBudget` (9 campos), `Championship` + responses; `MoneyFormatter` (FR1.3); `TeamBudgetSort` (FR2.1); `BudgetService` y `ChampionshipService` (con fallback) sobre el `NetworkClient` de F1; `ActiveChampionshipStore` (`UserDefaults`).
- **Vistas en `FutmondoApp`** (`#if canImport(SwiftUI)`): `RootTabView` (TabView 1-pestaña), `BudgetView` + `BudgetViewModel` orquestador (estados loading/loaded/error/empty), `BudgetRow` (4 métricas + tokens de dinero), `ChampionshipMenu`.
- **4 ADRs**: (1) separación kit/app por testabilidad en WSL; (2) `UserDefaults` para el campeonato activo (replica el patrón de la web); (3) ViewModel orquestador con estado explícito; (4) DTO completo de 9 campos aunque la lista muestre 4 (sin rehacer el modelo al llegar el detalle).
- Reutiliza red/auth de F1; **sin cambios de backend**. `traceability.json` cubre cada componente → FR/US.

¿Does this all look correct?

[Answer]: Looks correct
