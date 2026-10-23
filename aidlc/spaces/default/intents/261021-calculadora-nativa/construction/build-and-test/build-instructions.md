# Build Instructions — Calculadora nativa iOS

## Prerequisitos

- Toolchain de **Swift** (el del repo; probado en Linux/WSL). SDK de Apple para
  el target de app; coste 0 €.
- No hay dependencias externas: `ios/Package.swift` mantiene `dependencies: []`.
  No se instala nada.

## Entorno

- No requiere variables de entorno ni servicios locales para compilar ni para
  los tests de `FutmondoKit` (lógica pura con dobles en memoria, sin red).
- Para validación en dispositivo: `xtool` + iPhone con iOS 26 (fuera del build
  de CI/WSL).

## Comandos de build

```bash
# Compilar el paquete (FutmondoKit + FutmondoApp)
swift build --package-path ios
```

## Verificación del build

```bash
# Debe terminar con "Build complete!" y exit 0
swift build --package-path ios 2>&1 | tail -3
```

- En WSL/Linux las vistas SwiftUI quedan excluidas (`#if canImport(SwiftUI)`
  falso), por lo que el build valida `FutmondoKit` y la parte compilable de
  `FutmondoApp`. La UI se valida en dispositivo con `ios/scripts/install-app.sh`.

## Problemas comunes

- **Swift 6 strict concurrency en dispositivo**: evitar `static var` de estado
  (usar `static let`); el build de WSL no lo detecta, el de `xtool` sí.
- **`libxml2 ... no version information`**: aviso benigno del entorno Linux, no
  es un error de build.
- **`actool` no disponible en WSL**: los Color Sets van en código
  (`DSColorValue`), no en asset catalog; no afecta a este build.
