# Tech Stack Decisions — U2 `u2-login-theming`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

| Área | Decisión | Rationale |
|------|----------|-----------|
| UI | SwiftUI (SDK de Apple), consumiendo la librería `DesignSystem` (U1) | coste 0 €; revestir con componentes/tokens ya construidos |
| Ubicación | modificar `ios/Sources/FutmondoApp/LoginView.swift` in-place | brownfield: sin duplicados; preserva API y comportamiento de F1 |
| Dependencias | ninguna nueva | sólo SDK de Apple + FutmondoKit/DesignSystem internos |
| Verificación | `cd ios && swift build && swift test` + validación visual en iPhone 13 Pro | sin arnés de UI nativo (diferido) |

## Assumptions & Open Questions

None.
