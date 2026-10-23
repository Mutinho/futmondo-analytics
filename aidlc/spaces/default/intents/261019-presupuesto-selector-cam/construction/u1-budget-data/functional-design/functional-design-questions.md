# Functional Design — Questions (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Functional Design de U1 `u1-budget-data` (library `FutmondoKit`, lógica pura testeable):

- **Modelos** `Codable`/`Sendable`: `TeamBudget` (12 props, CodingKeys snake_case, `ops` derivado), `BalancesResponse`, `Championship` (extras opcionales para el legacy), `ChampionshipsResponse`, `SortKey`.
- **Lógica**: `MoneyFormatter` (R1: umbral M/K, 1 decimal si aplica, half-up, signo), `TeamBudgetSort` (R2: descendente estable), `BudgetService`/`ChampionshipService` (R3/R4: sobre `NetworkClient` de F1, fallback de endpoints, errores tipados), `ActiveChampionshipStore` (R5: `UserDefaults`, resolución de activo / primer campeonato / nil).
- **Seguridad** (R6/NFR2): sin credenciales en errores.
- **Tests** (`swift test`): tabla de casos de formato, orden, fallback, persistencia; `NetworkClient` fake (patrón F1) y `UserDefaults` de suite de test; casos vacío/error/opcionales ausentes.

**Autonomía de construcción propuesta**: autónomo hasta el checkpoint de cada unidad (`swift build && swift test` para U1), con un "ok" por summary en cada etapa.

¿Does this all look correct?

[Answer]: Looks correct
