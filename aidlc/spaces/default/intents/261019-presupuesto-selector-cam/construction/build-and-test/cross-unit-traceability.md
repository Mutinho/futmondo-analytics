# Cross-Unit Traceability — F2

> Fase: construcción (build-and-test). Idioma: castellano; tokens técnicos verbatim en inglés.

| Requisito | U1 (datos/lógica) | U2 (UI) | Verificación |
|-----------|-------------------|---------|--------------|
| FR1.1 cargar balances | `BudgetService`/`BalancesResponse` | `BudgetView`/`BudgetViewModel` | `swift test` (U1) + dispositivo |
| FR1.2 9 campos DTO / 4 en fila | `TeamBudget` | `BudgetRow` | `swift test` (decode) + dispositivo |
| FR1.3 formato M/K + tokens dinero | `MoneyFormatter` | `BudgetRow` | `MoneyFormatterTests` + dispositivo |
| FR2.1 orden descendente | `TeamBudgetSort` | `SortMenu`/VM | `TeamBudgetSortTests` + dispositivo |
| FR3.1 selector + fallback | `ChampionshipService` | `ChampionshipMenu` | `ChampionshipServiceTests` + dispositivo |
| FR3.2/FR3.3 persistencia/activo | `ActiveChampionshipStore`/`...Resolver`/`...Persistence` | `BudgetViewModel.load/select` | `ActiveChampionship*Tests` + dispositivo |
| FR4.1/FR4.2 carga/error | (errores tipados) | `BudgetState`/`LoadingState`/`ErrorState` | `swift test` (error paths) + dispositivo |
| FR5.1 TabView 1-pestaña | — | `RootTabView` | dispositivo |
| FR6 detalle de equipo | `fetchTeamDetail`/`Transaction`/`TeamDetailResponse`/`TransactionDatePresenter` | `TeamDetailView`/`TeamDetailViewModel` (zoom, summary numeric, menú Compras/Ventas, entrada escalonada) | `swift test` (U1) + dispositivo |
| NFR2 seguridad | no-fuga (tests U1) | error verbatim | `swift test` |
| NFR3/NFR4/NFR5 UI | — | vistas U2 | dispositivo |
| NFR1/NFR6 coste/verificación | `Package.swift` sin deps | idem | `swift build` |

Cobertura completa de FR Must; nada huérfano.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/code-generation/traceability.json`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/code-generation/traceability.json`

## Assumptions & Open Questions

None.
