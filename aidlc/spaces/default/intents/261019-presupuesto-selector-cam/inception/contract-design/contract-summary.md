# Contract Design — Summary (F2: Presupuesto nativo + selector de campeonato)

> Fase: inception (contract-design). Idioma: castellano; tokens técnicos verbatim en inglés.
> Contratos entre unidades (U1↔U2), con el backend existente, y con los cimientos de F1. Sin cambios de backend.

## 1. Contratos con el backend (consumo, sin cambios)

### GET /api/v1/analytics/balances?championship_id=<id>
- **Request**: query `championship_id`; `Authorization: Bearer <access token>`.
- **Response** (`BalancesResponse`): `{ success: Bool, championship_id: String, initial_budget: Int, teams: [TeamBudget] }`.
- **`TeamBudget`**: `team_id`, `team_name`, `balance`, `initial_budget`, `total_spent`, `total_income`, `purchases_count`, `sales_count`, `team_value`, `performance`, `max_bid`, `prizes` (enteros salvo nombres/ids). `performance = team_value + balance - initial_budget` (calculado en backend). *Nota de conteo*: el DTO tiene **12 propiedades** (esta lista es la fuente); las referencias anteriores a "9 campos/métricas" cuentan sólo las métricas de negocio mostrables (excluyendo `team_id`, `team_name`, `initial_budget`). De ellas, la fila muestra el `team_name` más **4 métricas** (`balance`, `performance`, `max_bid`, `prizes`); el resto de métricas (`team_value`, `total_spent`, `total_income`, ops) queda disponible para el detalle diferido.
- **Errores**: mapeados a `NetworkError` tipado (F1). 401 → requiere refresh (lo gestiona `AuthService` de F1).

### GET /api/v1/user/championships  (fallback: GET /api/v1/championships)
- **Request**: `Authorization: Bearer`.
- **Response** (`ChampionshipsResponse`): `{ success: Bool, championships: [Championship] }`.
- **`Championship`**: `championship_id`, `name`, `initial_budget`, `has_clauses`, `excluded_teams`, y campos extra opcionales (`money_per_point`, `money_per_ranking`, `dream_team_bonus`, `mvp_bonus`, `ranking_mode`, `users_to_rank`) decodificados como opcionales para tolerar el subconjunto del endpoint legacy.
- **Fallback**: si el primario falla, se intenta `GET /api/v1/championships` (contrato subconjunto); si ambos fallan → error (FR4.2).

## 2. Contrato U1 (library `FutmondoKit`) — superficie pública consumida por U2

```
protocol BudgetService {
  func fetchBalances(championshipId: String) async throws -> BalancesResponse
}
protocol ChampionshipService {
  func fetchChampionships() async throws -> [Championship]   // con fallback interno
}
protocol ActiveChampionshipStore {
  var activeId: String? { get }
  func setActive(_ id: String)                               // persiste en UserDefaults
}
enum MoneyFormatter { static func format(_ amount: Int, signed: Bool) -> String }
enum TeamBudgetSort { static func sorted(_ teams: [TeamBudget], by key: SortKey) -> [TeamBudget] }
```
- **Tipos de dominio** (`TeamBudget`, `Championship`, `BalancesResponse`, `ChampionshipsResponse`, `SortKey`, `NetworkError`) son públicos y `Codable`/`Sendable` donde aplique.
- **Errores**: propagados como `NetworkError` tipado; U2 los traduce a estado `error`.

## 3. Contrato U2 (ui `FutmondoApp`) — consume U1 + DesignSystem F1

- `BudgetViewModel` depende de `BudgetService`, `ChampionshipService`, `ActiveChampionshipStore`, `TeamBudgetSort` (inyección por protocolo → testable/mocking).
- `BudgetRow` consume `MoneyFormatter` + `DSColor`/`DSFont` (F1).
- Estado expuesto por el VM: `enum BudgetState { case loading, loaded([TeamBudget]), empty, error(String) }`.

## 4. Invariantes de contrato

- **Seguridad**: ninguna API de U1 expone ni registra tokens/credenciales; el `Bearer` lo inyecta el `NetworkClient` de F1 (NFR2).
- **Coste**: ningún contrato introduce dependencias nuevas (NFR1).
- **Sin cambios de backend**: los contratos de §1 son los endpoints existentes tal cual.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/domain-design/components.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/units-generation/unit-of-work.md`
- `aidlc/spaces/default/codekb/futmondo-analytics/api-documentation.md`

## Assumptions & Open Questions

None.
