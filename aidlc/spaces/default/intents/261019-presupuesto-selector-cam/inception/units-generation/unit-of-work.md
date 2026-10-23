# Units of Work — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (units-generation). Idioma: castellano; tokens técnicos verbatim en inglés.
> Scope: `feature`. Dos unidades, con U2 dependiente de U1 (mismo patrón limpio de F1).

```yaml
units:
  - name: u1-budget-data
    kind: library
    summary: >
      Capa de datos y lógica pura en FutmondoKit: DTOs (TeamBudget, Championship
      y sus responses), MoneyFormatter, TeamBudgetSort, BudgetService y
      ChampionshipService (con fallback de endpoints) sobre el NetworkClient de
      F1, y ActiveChampionshipStore (UserDefaults). Cubierta con swift test.
    depends_on: []
  - name: u2-budget-ui
    kind: ui
    summary: >
      Capa de presentación en FutmondoApp (SwiftUI, #if canImport(SwiftUI)):
      RootTabView (TabView 1-pestaña, Liquid Glass), BudgetView + BudgetViewModel
      (estados loading/loaded/error/empty), BudgetRow (4 métricas + tokens de
      dinero), ChampionshipMenu. Consume U1 y el DesignSystem de F1. Validada en
      dispositivo.
    depends_on: [u1-budget-data]
```

## U1 — `u1-budget-data` (library)

- **Contenido**: `TeamBudget`, `BalancesResponse`, `Championship`, `ChampionshipsResponse` (Codable); `MoneyFormatter`; `TeamBudgetSort`; `BudgetService` + `ChampionshipService` (protocolos + impl sobre `NetworkClient`); `ActiveChampionshipStore`.
- **Requisitos**: FR1.1, FR1.2, FR1.3, FR2.1, FR3.1, FR3.2, FR3.3, FR4.2, NFR1, NFR2, NFR6.
- **Verificación**: `swift test` (XCTest) sobre la lógica pura; tabla de casos de `MoneyFormatter`, orden, fallback de endpoints, persistencia del store.

## U2 — `u2-budget-ui` (ui)

- **Contenido**: `RootTabView`, `BudgetView`, `BudgetViewModel`, `BudgetRow`, `ChampionshipMenu`; estados de carga/error/vacío; toolbar con selector + orden.
- **Requisitos**: FR1 (render), FR4.1, FR5.1, NFR3, NFR4, NFR5.
- **Verificación**: `swift build` (compila guardado con `#if canImport(SwiftUI)`); validación visual/accesibilidad/rendimiento en iPhone 13 Pro.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/domain-design/{components.md,decisions.md}`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/{requirements-analysis/requirements.md,user-stories/stories.md}`

## Assumptions & Open Questions

None.
