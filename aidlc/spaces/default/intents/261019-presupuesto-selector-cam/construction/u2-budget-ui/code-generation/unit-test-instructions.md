# Unit Test Instructions — U2 `u2-budget-ui`

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.
> Metodología: test-after. Runner: `cd ios && swift build && swift test`.

## Capa testeable vs validación en dispositivo

- Las **vistas SwiftUI** y el `BudgetViewModel` (dependiente de SwiftUI/`@Observable`) **no se testean con XCTest en WSL** (cobertura de UI no fiable, regla durable): se validan en el iPhone 13 Pro.
- La **lógica pura** de orquestación ya reside en U1 (`MoneyFormatter`, `TeamBudgetSort`, `ActiveChampionshipResolver`, servicios) y está cubierta por los 39 tests de U1.
- Si al implementar U2 surge lógica pura nueva y extraíble del VM (p. ej. una función que derive el `BudgetState` a partir de `(championships, balances, error)` o decida si hay que persistir el id resuelto), **colocarla en `FutmondoKit`** (o en un tipo neutro sin SwiftUI) y añadir XCTest con happy-path + bordes. Si toda la lógica del VM es trivialmente orquestación de llamadas `async` de U1, no se fuerzan tests artificiales.

## Checkpoint ejecutable

- `cd ios && swift build` → compila U2 (guardado con `#if canImport(SwiftUI)`).
- `cd ios && swift test` → los 82 tests existentes (F1 + U1) siguen en verde (no regresión); más los nuevos XCTest si se extrajo lógica pura.

## Validación en dispositivo (iPhone 13 Pro, manual)

- Flujo: login → Presupuesto del campeonato activo → cambiar campeonato (persiste) → ordenar → estados vacío/error → logout (re-alojado, mismo `AuthViewModel.logout()`).
- Accesibilidad: VoiceOver (filas, selector, Reintentar), Dynamic Type.
- Fidelidad: tokens de dinero, verde Material 3, claro/oscuro; Liquid Glass de la tab bar.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/functional-spec.md`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/refined-mockups/accessibility-checklist.md`

## Assumptions & Open Questions

None.
