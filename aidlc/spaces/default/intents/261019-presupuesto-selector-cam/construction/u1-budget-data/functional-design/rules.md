# Functional Design — Rules (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## R1 — Formato de dinero (`MoneyFormatter`, FR1.3)
- `format(_ amount: Int, signed: Bool) -> String`.
- `abs(amount) >= 1_000_000` → dividir entre 1.000.000, sufijo `M`; `>= 1_000` → entre 1.000, sufijo `K`; `< 1_000` → número tal cual (sin sufijo).
- Un decimal si, tras redondear a 1 decimal, la parte fraccionaria ≠ 0 (p. ej. `12,4M`); sin decimal si es 0 (`8M`, y también `12,0M`→`12M`). El borde se resuelve POR redondeo a 1 decimal primero y luego decidir: `11.990.000` → `abs/1e6 = 11,99` → redondeo a 1 decimal `12,0` → se emite `12M`.
- **Redondeo determinista**: half-away-from-zero a 1 decimal (p. ej. `−1.250.000`→`−1,3M`; `1.250.000`→`1,3M`), implementado con aritmética entera sobre el valor, **sin** depender de `NumberFormatter`/locale.
- **Separador y glifos deterministas (independientes de locale)**: separador decimal **coma** `,` fijo (no de locale, para que `swift test` en WSL sea estable); signo negativo con el carácter ASCII `-` (U+002D); signo positivo `+` sólo si `signed == true`. (La prosa de specs usa `−` por estética, pero la función emite `-`.)
- `signed == true` → anteponer `+` a positivos y `-` a negativos; `signed == false` → sólo `-` en negativos, sin `+`.

## R2 — Ordenación (`TeamBudgetSort`, FR2.1)
- `sorted(_ teams: [TeamBudget], by key: SortKey) -> [TeamBudget]`: orden **descendente** por el campo de la clave. Estable. Sin mutación del input.

## R3 — Servicio de balances (`BudgetService`, FR1.1, FR4.2)
- `fetchBalances(championshipId:) async throws -> BalancesResponse` vía `NetworkClient` (GET `analytics/balances?championship_id=`). Propaga `NetworkError` tipado; no traga errores.

## R4 — Servicio de campeonatos (`ChampionshipService`, FR3.1, FR4.2)
- `fetchChampionships() async throws -> [Championship]`: intenta GET `user/championships`; si lanza **cualquier** error (red, status no-2xx o fallo de decodificación), intenta GET `championships` (fallback); si ambos lanzan, propaga el error del fallback. Nunca devuelve lista parcial silenciosa.

## R5 — Estado del campeonato activo (`ActiveChampionshipStore` + resolución)
- `activeId: String?` leído de `UserDefaults` (clave `futmondo_active_championship`, paridad con la web); `setActive(_ id: String)` persiste en `UserDefaults`.
- **Resolución del activo como función pura testeable de U1** (no delegada a U2): `ActiveChampionshipResolver.resolve(activeId: String?, in championships: [Championship]) -> Championship?`:
  - si `activeId` existe y hay un campeonato con ese `championshipId` → ese (FR3.2);
  - si `activeId` es `nil` **o** no coincide con ninguno de la lista → el primero de la lista (FR3.3);
  - si la lista está vacía → `nil` (estado vacío).
  - La resolución **no auto-sanea** `UserDefaults` por sí sola; es responsabilidad del llamador (el `BudgetViewModel` de U2) persistir el id resuelto vía `setActive` si cambió (owner de FR3.3, finding de contract-design). `resolve` es pura (sin efectos).

## R6 — Seguridad (NFR2)
- Ninguna función registra ni incluye tokens/credenciales en mensajes de error. El `Bearer` lo inyecta el `NetworkClient` de F1.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/requirements-analysis/requirements.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/contract-design/contract-summary.md`

## Assumptions & Open Questions

None.
