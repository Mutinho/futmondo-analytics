# Code Summary — U1 `u1-budget-data`

> Fase: construcción. Unidad: `u1-budget-data` (library `FutmondoKit`). Idioma: castellano; tokens técnicos verbatim en inglés.
> Metodología: test-after. Runner: `cd ios && swift build && swift test`.

## Ficheros creados

### Código de producción — `ios/Sources/FutmondoKit/Budget/`
1. `TeamBudget.swift` — DTO `Codable`/`Sendable`/`Identifiable`. 12 propiedades wire con `CodingKeys` snake_case (`team_id`→`teamId`, etc.); `id = teamId`; propiedad derivada `ops = purchasesCount + salesCount` (no es campo wire).
2. `BalancesResponse.swift` — DTO del `GET analytics/balances` (`success`, `championship_id`, `initial_budget`, `teams`).
3. `Championship.swift` — DTO `Identifiable` (`id = championshipId`) con los 5 campos core + 6 extras **opcionales** (`money_per_point`, `money_per_ranking`, `dream_team_bonus`, `mvp_bonus`, `ranking_mode`, `users_to_rank`) para tolerar el subconjunto legacy del fallback.
4. `ChampionshipsResponse.swift` — DTO (`success`, `championships`).
5. `SortKey.swift` — enum `Sendable`/`CaseIterable` (`balance`, `performance`, `maxBid`, `teamValue`, `totalSpent`, `totalIncome`).
6. `MoneyFormatter.swift` — formato M/K **determinista** e independiente de locale (ver decisiones).
7. `TeamBudgetSort.swift` — orden **descendente, estable, no mutante** por `SortKey`.
8. `BudgetService.swift` — protocolo `BudgetService` + `HTTPBudgetService` (GET `analytics/balances?championship_id=` vía `NetworkClient` de F1 inyectado).
9. `ChampionshipService.swift` — protocolo `ChampionshipService` + `HTTPChampionshipService` con fallback `user/championships` → `championships`.
10. `ActiveChampionshipStore.swift` — protocolo + `UserDefaultsActiveChampionshipStore` (clave `futmondo_active_championship`, sólo persiste el id como `String`).
11. `ActiveChampionshipResolver.swift` — `resolve(activeId:in:)` **pura, sin efectos**.

### Tests — `ios/Tests/FutmondoKitTests/`
- `MoneyFormatterTests.swift` (7 tests)
- `TeamBudgetSortTests.swift` (6 tests)
- `BudgetDTOTests.swift` (5 tests)
- `BudgetServiceTests.swift` (5 tests; define el fake `FakeBudgetNetworkClient`)
- `ChampionshipServiceTests.swift` (6 tests; fake `ExactPathFake` interno para distinguir primario vs fallback, ya que la ruta del fallback es prefijo de la primaria)
- `ActiveChampionshipStoreTests.swift` (5 tests de store + 5 de resolver = incluye la clase `ActiveChampionshipResolverTests`)

No se modificó `Networking/`, `Auth/` ni `DesignSystem/` de F1 (sólo se consumen). `Package.swift` sin cambios: `dependencies: []`.

## Decisiones clave

- **Puente throw/Result**: el `NetworkClient` de F1 devuelve `Result<T, NetworkError>` y **nunca lanza** desde `send`. Los servicios de U1 exponen `async throws`, así que mapean `.failure(error)` a `throw error`, propagando el `NetworkError` tipado tal cual (sin envolverlo ni añadir contexto que pudiera filtrar la query).
- **`MoneyFormatter` determinista con aritmética entera** (R1): se trabaja sobre `amount.magnitude` (`UInt`, evita el overflow de `abs(Int.min)`); el redondeo a 1 decimal es half-away-from-zero vía enteros (`tenths = (mag*10)/divisor`, y `+1` cuando `remainder*2 >= divisor`); un decimal sólo si la décima redondeada ≠ 0 (`12,4M`), sin decimal si es 0 (`8M`, `12M`, y `11.990.000`→`12,0`→`12M`). Separador `,` fijo, signo ASCII `-` (U+002D), `+` sólo con `signed:true`. **Sin** `NumberFormatter`/locale, para que `swift test` en WSL sea estable.
- **Orden estable** (R2): `Array.sort` de Swift no garantiza estabilidad, así que se ordena sobre `enumerated()` con desempate por índice original, garantizando estabilidad en empates sin mutar el input.
- **Fallback de campeonatos** (R4): `HTTPChampionshipService` intenta el primario y, ante **cualquier** error (red, status o decode), intenta el fallback; si ambos lanzan, propaga el error **del fallback** (no el del primario). Verificado explícitamente en los tests.
- **Resolución pura** (R5): `ActiveChampionshipResolver.resolve` no toca `UserDefaults`; persistir el id resuelto es responsabilidad del `BudgetViewModel` de U2 (frontera U1/U2, finding de contract-design).
- **No-fuga en errores** (SR1/SR4): tests dedicados comprueban que la descripción del error **no contiene** el `championship_id` ni material de token, cubriendo tanto `NetworkError` (red/status) como `DecodingError` (response malformado).
- **Swift 6 async-safety en los fakes**: `NSLock.lock()/unlock()` no está disponible en contexto `async`; los fakes usan un helper `withLock` síncrono (el lock nunca se mantiene a través de un `await`), idéntico al patrón del `SpyNetworkClient` de F1.

## Resultado de `swift build && swift test`

- `swift build`: **Build complete** (0 errores; los avisos `libxml2.so.2 no version information` son ruido del entorno WSL, no del paquete).
- `swift test`: **82 tests ejecutados, 0 fallos** (43 de F1 + 39 nuevos de U1).
  - Desglose U1: MoneyFormatter 7, TeamBudgetSort 6, BudgetDTO 5, BudgetService 5, ChampionshipService 6, ActiveChampionshipStore 5, ActiveChampionshipResolver 5.
  - Cada componente: happy-path + ≥2 casos de borde/error; todas las aserciones verifican efectos reales (valores decodificados, orden, persistencia, no-fuga), nunca `assert true`.

## Cobertura (regla durable del proyecto)

El piso de 80% line-coverage del Testing Contract **no se verifica numéricamente** para código iOS en WSL (llvm-cov no fiable, aprendizaje durable). La lógica pura de U1 vive en `FutmondoKit` y se cubre con XCTest ejecutable; la suite existente (backend `pytest` / frontend `ng test`) no la toca este cambio.

## Desviaciones

- Ninguna respecto al plan aprobado ni a las unit-test-instructions. El contrato enumera `testable_layers` genéricos (DB/repo/endpoint/frontend); en U1 la única capa testeable es **lógica pura Swift** en `FutmondoKit`, tal como anota el propio plan. Validación en dispositivo: NO-APLICA a U1 (sin UI SwiftUI).
