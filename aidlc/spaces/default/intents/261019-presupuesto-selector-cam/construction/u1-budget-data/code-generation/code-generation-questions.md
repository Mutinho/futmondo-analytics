# Code Generation — Questions (U1 `u1-budget-data`)

> Fase: construcción. Unidad: `u1-budget-data`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Plan Approval

[Approval Fingerprint]: sha256:v3:4029a0674d180fdd6136f5fc403d422ae6bf24f42d1282d96afbc53a36bd88f9
[Planned Source]: 8c1c68d524263196187f8e9f5b2ce0285c4d17f76e55b7bbe79e15a18a5cc296

Plan resumido (detalle en `code-generation-plan.md`): generar en `ios/Sources/FutmondoKit/Budget/` los DTOs (`TeamBudget`/`Championship` + responses, `SortKey`), la lógica pura (`MoneyFormatter` determinista, `TeamBudgetSort`), los servicios (`BudgetService`/`ChampionshipService` con fallback sobre el `NetworkClient` de F1) y el estado (`ActiveChampionshipStore` `UserDefaults` + `ActiveChampionshipResolver`). Tests test-after (5-8 por componente) con fakes patrón F1. Checkpoint `cd ios && swift build && swift test`. Sin cambios de dependencias ni de `Networking/Auth/DesignSystem` salvo consumo.

- Approve Plan
- Request Changes

[Answer]: Approve Plan

## Consolidated Summary Confirmation

Checkpoint de U1 `u1-budget-data` (capa de datos/lógica en `FutmondoKit/Budget/`):

- **Código generado**: 11 ficheros (DTOs `TeamBudget`/`Championship` + responses, `SortKey`, `MoneyFormatter` determinista, `TeamBudgetSort` estable, `BudgetService`/`ChampionshipService` con fallback sobre el `NetworkClient` de F1, `ActiveChampionshipStore` `UserDefaults` + `ActiveChampionshipResolver` puro).
- **Tests**: 6 ficheros XCTest nuevos (MoneyFormatter, TeamBudgetSort, DTOs, BudgetService, ChampionshipService, ActiveChampionshipStore+Resolver), 5-8 por componente, happy-path + bordes, no-fuga de credenciales (NetworkError y DecodingError).
- **Checkpoint verificado de primera mano**: `cd ios && swift build && swift test` → Build complete, **82 tests, 0 fallos** (43 F1 + 39 U1).
- **Reviewer de código adversarial**: READY (1 Minor advisory no bloqueante: `999_999`→"1000K" en el borde del millón, spec-correcto; decisión UX opcional diferida).
- Sin dependencias nuevas; `Networking/`/`Auth/`/`DesignSystem/` intactos salvo consumo. Validación en dispositivo NO-APLICA a U1 (sin UI).

¿Does this all look correct?

[Answer]: Looks correct
