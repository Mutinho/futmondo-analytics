# Unit Test Instructions — U1 `u1-budget-data`

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.
> Metodología: test-after. Runner: `cd ios && swift build && swift test`. Tests en `ios/Tests/FutmondoKitTests/`.

## Alcance y patrón

- Tests XCTest en el testTarget `FutmondoKitTests` (sólo depende de `FutmondoKit`, compila en WSL sin SwiftUI).
- Sin red real: `NetworkClient` fake en memoria (patrón F1 de `NetworkClientTests`/`AuthServiceTests`). Sin credenciales/tokens reales.
- `UserDefaults` de suite de test dedicada (`UserDefaults(suiteName:)`), limpiada en `setUp`/`tearDown`.
- 5-8 tests por componente: happy-path + ≥2 casos de error/borde. Nada de `assert true` ni specs que no aseveren efecto.

## Ficheros de test y casos

### `MoneyFormatterTests.swift`
- Tabla determinista: `12_400_000,signed:false→"12,4M"`; `8_000_000→"8M"`; `12_000_000→"12M"`; `11_990_000→"12M"`; `-1_200_000→"-1,2M"`; `-1_250_000→"-1,3M"`; `5_500→"5,5K"`; `950→"950"`; `signed:true`: `3_100_000→"+3,1M"`, `-500_000→"-500K"`. Verifica separador `,`, signo ASCII `-`, independencia de locale.

### `TeamBudgetSortTests.swift`
- Orden descendente por cada `SortKey`; estabilidad (empates mantienen orden relativo); input no mutado.

### `BudgetDTOTests.swift`
- Decode de un `BalancesResponse` de ejemplo (JSON fixture) → mapea snake_case; `ops == purchases_count + sales_count`. Decode de `ChampionshipsResponse` con y sin campos extra opcionales.

### `BudgetServiceTests.swift` / `ChampionshipServiceTests.swift`
- `HTTPBudgetService` con fake OK → devuelve `BalancesResponse`.
- `HTTPChampionshipService`: primario OK → lista; primario lanza (red) → usa fallback; primario lanza (decode-error) → usa fallback; ambos lanzan → propaga error del fallback.
- No-fuga: ante error, la descripción del error NO contiene el `championship_id` ni tokens (cubre `NetworkError` y `DecodingError`).

### `ActiveChampionshipStoreTests.swift` / `ActiveChampionshipResolverTests.swift`
- Store: `activeId` nil sin valor; `setActive` persiste y relee.
- Resolver: activeId en lista → ese; activeId nil → primero; activeId no-en-lista → primero; lista vacía → nil.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/functional-design/functional-spec.md`
- `ios/Tests/FutmondoKitTests/` (patrón de fakes de F1)

## Assumptions & Open Questions

None.
