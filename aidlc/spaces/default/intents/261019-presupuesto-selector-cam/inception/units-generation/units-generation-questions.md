# Units Generation — Questions (F2)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Units Generation:

- **2 unidades** (mismo patrón limpio que F1):
  - **U1 `u1-budget-data`** (library, sin deps): DTOs (`TeamBudget`/`Championship` + responses), `MoneyFormatter`, `TeamBudgetSort`, `BudgetService`/`ChampionshipService` (fallback) sobre `NetworkClient` de F1, `ActiveChampionshipStore` (`UserDefaults`). Checkpoint `swift build && swift test`.
  - **U2 `u2-budget-ui`** (ui, depende de U1): `RootTabView` (TabView 1-pestaña), `BudgetView` + `BudgetViewModel`, `BudgetRow`, `ChampionshipMenu`. Checkpoint `swift build` + validación en dispositivo.
- **Dependencias**: U2 → U1 → cimientos F1; sin ciclos; U1 se construye primero.
- `traceability.json` cubre unidad → US/FR; todos los FR Must asignados.

¿Does this all look correct?

[Answer]: Looks correct
