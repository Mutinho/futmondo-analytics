# Functional Design — Frontend Components (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

| Componente SwiftUI | Tipo | Estado/entrada | Tokens F1 | Trazabilidad |
|--------------------|------|----------------|-----------|--------------|
| `RootTabView` | `View` | — | material del sistema | FR5.1 / US4 |
| `BudgetView` | `View` | `@State viewModel: BudgetViewModel` | `LoadingState`, `ErrorState`, `Card`, `DSSpacing` | US1 / FR1, FR4 |
| `BudgetRow` | `View` | `let team: TeamBudget` | `DSFont`, `DSColor.moneyPositive/Negative` | FR1.2, FR1.3 / NFR5 |
| `ChampionshipMenu` | `View` (toolbar) | `championships`, `active`, callback | `DSColor` primary | FR3.1 / US2 |
| `SortMenu` | `View` (toolbar) | `sortKey`, callback | `DSColor` | FR2.1 / US3 |
| `BudgetViewModel` | `@Observable` `@MainActor` | servicios/store de U1 inyectados | — | FR1/FR2/FR3/FR4 |

## Estados de `BudgetView`

- `loading` → `LoadingState` (<100 ms, NFR4).
- `loaded([TeamBudget])` → `List` de `BudgetRow` ordenada por `sortKey`.
- `emptyTeams` → mensaje "Este campeonato no tiene equipos aún." (selector habilitado).
- `noChampionships` → mensaje "No tienes campeonatos." + selector deshabilitado.
- `error(String)` → `ErrorState` + botón Reintentar (foco VoiceOver, NFR5); no corrompe el campeonato activo persistido (FR4.2).

## Accesibilidad (del accessibility-checklist)

Filas como elemento VoiceOver con label compuesto; Dynamic Type vía `DSFont`; color no único portador (signo). Verificación en dispositivo.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/functional-spec.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/refined-mockups/*`

## Assumptions & Open Questions

None.
