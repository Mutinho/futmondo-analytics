# Tech Stack Decisions — U1 `u1-design-system`

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

| Área | Decisión | Rationale | ID |
|------|----------|-----------|----|
| Lenguaje/UI | Swift + SwiftUI | Target nativo iOS ya decidido; coste 0 € (SDK de Apple). | NFR2.1 |
| Empaquetado | SwiftPM (módulo/target dentro del proyecto `ios/`) | Encaja con la estructura de F1 (`ios/Package.swift`, `xtool.yml`); sin despliegue independiente. | — |
| Color | Asset catalog (Color Sets con Any/Dark Appearance) | Resolución automática claro/oscuro (BR1.1); idiomático, sin dependencias. | NFR3 |
| Tipografía | `Font` + Dynamic Type (`@ScaledMetric`/relative) con Roboto opcional y fallback a fuente del sistema | FR2.2/FR2.3; sin empaquetar dependencia obligatoria. | — |
| Build/verificación | `cd ios && swift build && swift test` (xtool/WSL para instalar en dispositivo) | Check reproducible a coste 0 €; ya usado en F1. | — |

Sin bases de datos, colas, caches ni servicios: la librería es cliente puro.

## Assumptions & Open Questions

None.
