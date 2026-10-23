# NFR Design — Questions (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de NFR Design de U2:

- **Performance**: `List`/`LazyVStack` (render perezoso, 60 fps); `state = .loading` síncrono `@MainActor` antes del `await` → spinner <100 ms. Verificación en dispositivo.
- **Seguridad**: el `BudgetViewModel` depende sólo de los protocolos públicos de U1 (nunca `NetworkClient`/`AuthService`); error mostrado = `localizedDescription` de U1 verbatim, sin interpolar id/tokens; `UserDefaults` vía store de U1 (sólo id); sin red nueva. Sin cambios en el modelo de amenazas.
- **Componentes**: `FutmondoApp/Budget/` (RootTabView, BudgetView, BudgetViewModel, BudgetRow, ChampionshipMenu, SortMenu) bajo `#if canImport(SwiftUI)`; integración con `FutmondoApp.swift` (raíz → RootTabView tras login; `AuthViewModel`/`SplashView` de F1 intactos); impls de U1 inyectadas en el punto de entrada.

¿Does this all look correct?

[Answer]: Looks correct
