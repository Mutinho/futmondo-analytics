# Build Instructions — Favoritos nativa iOS

## Prerequisitos
- Toolchain de Swift (probado en WSL). SDK de Apple; coste 0 €.
  `ios/Package.swift` sin dependencias (`dependencies: []`).

## Comandos
```bash
swift build --package-path ios          # compilar FutmondoKit + FutmondoApp
swift test --package-path ios           # suite completa (232 tests)
```

## Verificación
- `swift build` debe terminar con "Build complete!" (exit 0).
- En WSL las vistas SwiftUI quedan excluidas (`#if canImport(SwiftUI)`); la UI
  se valida en dispositivo con `ios/scripts/install-app.sh`.

## Problemas comunes
- Swift 6 device-strict: usar `static let`, no `static var` de estado.
- `actool` no disponible en WSL (Color Sets en código); no afecta al build.
