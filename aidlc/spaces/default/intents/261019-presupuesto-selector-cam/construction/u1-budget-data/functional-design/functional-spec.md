# Functional Design — Spec (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data` (library `FutmondoKit`). Idioma: castellano; tokens técnicos verbatim en inglés.

## Superficie pública (protocolos + tipos)

```swift
public struct TeamBudget: Codable, Sendable, Identifiable { /* 12 props; id = teamId; ops derivado */ }
public struct BalancesResponse: Codable, Sendable { /* success, championshipId, initialBudget, teams */ }
public struct Championship: Codable, Sendable, Identifiable { /* id = championshipId; extras opcionales */ }
public struct ChampionshipsResponse: Codable, Sendable { /* success, championships */ }
public enum SortKey: Sendable { case balance, performance, maxBid, teamValue, totalSpent, totalIncome }

public enum MoneyFormatter { public static func format(_ amount: Int, signed: Bool) -> String }
public enum TeamBudgetSort { public static func sorted(_ teams: [TeamBudget], by key: SortKey) -> [TeamBudget] }

public protocol BudgetService: Sendable {
  func fetchBalances(championshipId: String) async throws -> BalancesResponse
}
public protocol ChampionshipService: Sendable {
  func fetchChampionships() async throws -> [Championship]     // fallback interno
}
public protocol ActiveChampionshipStore: Sendable {
  var activeId: String? { get }
  func setActive(_ id: String)
}

public enum ActiveChampionshipResolver {
  // Pura, sin efectos. Owner de la persistencia del id resuelto: el BudgetViewModel (U2).
  public static func resolve(activeId: String?, in championships: [Championship]) -> Championship?
}
```

Implementaciones concretas: `HTTPBudgetService`, `HTTPChampionshipService` (sobre el `NetworkClient` de F1), `UserDefaultsActiveChampionshipStore`.

## Comportamientos a testear (`swift test`)

- `MoneyFormatter`: tabla de casos **determinista** (locale-independiente, separador `,` fijo, signo ASCII `-`): `12.400.000, signed:false → "12,4M"`; `8.000.000 → "8M"`; `12.000.000 → "12M"`; `11.990.000 → "12M"`; `-1.200.000 → "-1,2M"`; `-1.250.000 → "-1,3M"` (half-away-from-zero); `5.500 → "5,5K"`; `950 → "950"`; con `signed:true`: `3.100.000 → "+3,1M"`, `-500.000 → "-500K"`.
- `TeamBudgetSort`: orden descendente por cada `SortKey`; estabilidad; input inmutable.
- `ActiveChampionshipResolver.resolve`: activeId en lista → ese; activeId nil → primero; activeId presente-pero-no-en-lista → primero; lista vacía → nil.
- `HTTPBudgetService`/`HTTPChampionshipService`: con un `NetworkClient` fake (patrón F1), decodifican el response; `ChampionshipService` cae al fallback cuando el primario lanza (incluido fallo de decode) y propaga el error del fallback cuando ambos lanzan.
- `UserDefaultsActiveChampionshipStore`: lee/escribe con un `UserDefaults` de suite de test; `activeId` nil cuando no hay valor.

## Casos límite / error

- Response vacío (`teams: []`) decodifica a lista vacía (el VM lo traduce a estado vacío).
- Error de red → `NetworkError` tipado propagado (sin credenciales en el mensaje).
- Campos opcionales de `Championship` ausentes (endpoint legacy) → decodifican a `nil` sin fallar.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/functional-design/{entities.md,rules.md}`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/contract-design/contract-summary.md`

## Assumptions & Open Questions

None.
