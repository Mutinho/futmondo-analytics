# Build Instructions — F2 (Construcción integrada)

> Fase: construcción (build-and-test). Idioma: castellano; tokens técnicos verbatim en inglés.

## Build

- Comando: `cd ios && swift build` (compila `FutmondoKit` + `FutmondoApp`; la UI de U2 bajo `#if canImport(SwiftUI)`).
- Sin dependencias nuevas (`Package.swift` `dependencies: []`). Toolchain Swift 6; en WSL el build de app usa el SDK disponible, la validación de UI se hace en dispositivo con `xtool`.

## Test (unit, ejecutable en WSL)

- Comando: `cd ios && swift test` → **87 tests, 0 fallos** (43 F1 + 39 U1 + 5 de U2 `ActiveChampionshipPersistence`).
- `FutmondoKitTests` sólo depende de `FutmondoKit`; las vistas SwiftUI no entran en el cómputo (validación en dispositivo).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/code-generation/*`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/code-generation/*`

## Assumptions & Open Questions

None.
