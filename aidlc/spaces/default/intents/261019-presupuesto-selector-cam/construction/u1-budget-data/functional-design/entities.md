# Functional Design — Entities (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data` (library `FutmondoKit`). Idioma: castellano; tokens técnicos verbatim en inglés.
> Lógica pura testeable con `swift test`. Sin SwiftUI, sin dependencias nuevas.

## Modelos (`Codable`, `Sendable`)

### `TeamBudget`
Decodifica cada elemento de `teams[]` de balances. 12 propiedades:
`teamId: String`, `teamName: String`, `balance: Int`, `initialBudget: Int`, `totalSpent: Int`, `totalIncome: Int`, `purchasesCount: Int`, `salesCount: Int`, `teamValue: Int`, `performance: Int`, `maxBid: Int`, `prizes: Int`.
- `CodingKeys` mapean snake_case del backend (`team_id`→`teamId`, etc.).
- Propiedad derivada `ops: Int { purchasesCount + salesCount }`.

### `BalancesResponse`
`success: Bool`, `championshipId: String`, `initialBudget: Int`, `teams: [TeamBudget]`.

### `Championship`
`championshipId: String`, `name: String`, `initialBudget: Int`, `hasClauses: Bool`, `excludedTeams: [String]`, y opcionales (tolerar legacy): `moneyPerPoint: Int?`, `moneyPerRanking: Int?`, `dreamTeamBonus: Int?`, `mvpBonus: Int?`, `rankingMode: String?`, `usersToRank: Int?`.

### `ChampionshipsResponse`
`success: Bool`, `championships: [Championship]`.

### `SortKey` (enum)
`.balance, .performance, .maxBid, .teamValue, .totalSpent, .totalIncome`.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/domain-design/components.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/contract-design/contract-summary.md`

## Assumptions & Open Questions

None.
