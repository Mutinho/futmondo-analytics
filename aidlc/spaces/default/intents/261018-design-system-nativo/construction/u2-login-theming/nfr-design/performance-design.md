# Performance Design — U2 `u2-login-theming`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

- **NFR4.1 (render fluido)**: el revestimiento usa vistas SwiftUI ligeras de U1 (sin listas pesadas ni trabajo en el hilo principal). Los Color Assets/tokens se resuelven en O(1); `DSFont` usa estilos relativos (Dynamic Type) sin recomputación costosa. Sin cambios en el ciclo de red (lo gestiona `AuthService` de F1). Objetivo 60 fps, verificación manual en iPhone 13 Pro.
- **NFR4.2 (feedback de loading)**: el estado `loading` se deriva directamente de `viewModel.state == .loading` y el `PrimaryButton` lo refleja en el mismo ciclo de render (feedback < 100 ms desde la pulsación, sin latencia añadida por U2).

## Assumptions & Open Questions

None.
