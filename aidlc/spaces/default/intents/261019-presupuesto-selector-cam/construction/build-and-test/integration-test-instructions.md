# Integration Test Instructions — F2

> Fase: construcción (build-and-test). Idioma: castellano; tokens técnicos verbatim en inglés.

## Integración U1 ↔ U2 (ejecutable donde sea lógica pura)

- `ActiveChampionshipPersistence.shouldPersist` (frontera U2→U1 para FR3.3) cubierto por `ActiveChampionshipPersistenceTests` (`swift test`).
- El `BudgetViewModel` orquesta los protocolos de U1 (`BudgetService`/`ChampionshipService`/`ActiveChampionshipStore`); la integración completa VM↔U1↔red se valida de extremo a extremo **en dispositivo** (requiere red real y SwiftUI), no en WSL.

## Integración con F1 (en dispositivo)

- Flujo: login (F1) → `SplashView.case .resumed` → `RootTabView` → Presupuesto; logout re-alojado invoca el mismo `AuthViewModel.logout()`. Se valida que la sesión de F1 sigue intacta (auto-login, expiración, offline).

## Comando

`cd ios && swift build && swift test` para la parte ejecutable; el resto, checklist en iPhone 13 Pro.

## Assumptions & Open Questions

None.
