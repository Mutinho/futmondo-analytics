# NFR Design — Logical Components (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Componentes lógicos y su ubicación (en `FutmondoKit`)

```
FutmondoKit/
  Budget/
    TeamBudget.swift              // DTO (12 props, CodingKeys, ops derivado)
    BalancesResponse.swift        // DTO
    Championship.swift            // DTO (extras opcionales)
    ChampionshipsResponse.swift   // DTO
    SortKey.swift                 // enum
    MoneyFormatter.swift          // lógica pura determinista
    TeamBudgetSort.swift          // lógica pura
    BudgetService.swift           // protocolo + HTTPBudgetService
    ChampionshipService.swift     // protocolo + HTTPChampionshipService (fallback)
    ActiveChampionshipStore.swift // protocolo + UserDefaultsActiveChampionshipStore
    ActiveChampionshipResolver.swift // función pura de resolución
```

Todos en el target library existente `FutmondoKit` (subcarpeta nueva `Budget/`), sin tocar `Networking/`/`Auth/`/`DesignSystem/` de F1 salvo para consumir `NetworkClient`. Tests en `Tests/FutmondoKitTests/Budget*Tests.swift`.

**Frontera U1/U2 en la persistencia del campeonato activo**: U1 **expone** el almacén (`UserDefaultsActiveChampionshipStore`: `activeId` get / `setActive`) y la función pura `ActiveChampionshipResolver.resolve`. U1 **no decide por sí mismo cuándo** persistir; es el `BudgetViewModel` de U2 quien, tras resolver el activo contra la lista cargada, invoca `setActive` si el id resuelto difiere del persistido (owner de FR3.3). Así la lógica es testeable en U1 y la orquestación de efectos queda en U2.

## Rendimiento / escalabilidad

NO-APLICA carga: el número de equipos por campeonato es pequeño (decenas); orden y formato son O(n) sobre listas cortas. La fluidez de render es asunto de U2 (NFR4), no de U1.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/functional-design/functional-spec.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/code-structure.md`

## Assumptions & Open Questions

None.
