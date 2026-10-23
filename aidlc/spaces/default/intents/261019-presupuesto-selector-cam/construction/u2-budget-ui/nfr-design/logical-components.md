# NFR Design — Logical Components (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Ubicación (en `FutmondoApp`)

```
FutmondoApp/
  Budget/
    RootTabView.swift          // TabView 1-pestaña (Liquid Glass), #if canImport(SwiftUI)
    BudgetView.swift           // pantalla + toolbar (ChampionshipMenu + SortMenu) + estados
    BudgetViewModel.swift      // @MainActor @Observable; orquesta servicios/store/resolver de U1
    BudgetRow.swift            // fila de equipo (DSFont/DSColor + MoneyFormatter), label VoiceOver
    ChampionshipMenu.swift     // Menu en el título; activo con ✓; deshabilitado si vacío
    SortMenu.swift             // Menu de orden (6 claves)
```

- Todo bajo `#if canImport(SwiftUI)`; integrado con `SplashView.swift` de F1.
- **Seam de integración (exacto, leído del código F1)**: la raíz es `SplashView` (no `FutmondoApp.swift`, que sólo cablea el `AuthService` y presenta `SplashView`). La superficie autenticada se decide en `SplashView.content` → `case .resumed`, que **hoy** renderiza `authenticatedPlaceholder`. F2 **sustituye el cuerpo de `case .resumed`** por `RootTabView`, dejando intactos `runBootstrap()`, el `.onChange(of: viewModel.state)` que enruta `.success → .resumed`, y el resto de fases (`.checking`, `.offline`, `.expired`, `.noSession` con `LoginView`). No se toca `FutmondoApp.swift` ni `AuthViewModel`.
- **Re-homing del logout (preservar la lógica de sesión de F1)**: el único punto de logout vive hoy en `authenticatedPlaceholder` (`await viewModel.logout(); phase = .noSession`). Al reemplazar esa vista por `RootTabView`, el logout se **re-aloja dentro de `RootTabView`** (p. ej. un botón "Cerrar sesión" accesible) que invoca **exactamente el mismo** `AuthViewModel.logout()` y fija `phase = .noSession` mediante un callback/binding pasado desde `SplashView`. Así el flujo de sesión F1 (bootstrap, auto-login, logout) queda igual; sólo cambia dónde se aloja el botón.
- Composición del punto de entrada: `SplashView` crea el `BudgetViewModel` inyectando las impls concretas de U1 (`HTTPBudgetService`, `HTTPChampionshipService` sobre el `NetworkClient` de F1 ya cableado en `FutmondoApp.swift`, `UserDefaultsActiveChampionshipStore`) y se lo pasa a `RootTabView`.

## Rendimiento/escalabilidad

Listas cortas; render perezoso (ver performance-design). Sin backend ni escalado.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/{functional-spec.md,frontend-components.md}`
- `ios/Sources/FutmondoApp/*` (F1), `ios/Sources/FutmondoKit/Budget/*` (U1)

## Assumptions & Open Questions

None.
