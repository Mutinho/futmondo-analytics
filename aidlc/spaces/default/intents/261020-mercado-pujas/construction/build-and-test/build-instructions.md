# Build Instructions — F3 Mercado (u1-market)

> Instrucciones de build para la capa nativa iOS (`ios/`, SwiftPM). F3 añade la
> pantalla de Mercado; no toca backend ni frontend Angular (esas suites siguen
> igual y las corre el gate de CI). Coste 0 €: sólo SDK de Apple / toolchain Swift.

## Dependencias

- Toolchain Swift (`swift` ≥ 6.0) con soporte SwiftPM. `Package.swift` declara
  `dependencies: []` — **no hay dependencias externas que instalar**.
- No se requiere `npm`/`pip` para esta Unit (no toca frontend/backend).

## Setup de entorno

- Ninguna variable de entorno nueva. La app usa la base URL
  `https://futmondo-api.fly.dev` (cableada en `FutmondoApp`, reutilizada de F1).
- Los tests de `FutmondoKit` no necesitan red ni credenciales (dobles in-memory).

## Comandos de build

```
swift build --package-path ios
```

Compila los targets `FutmondoKit` (library) y `FutmondoApp` (app product, vistas
SwiftUI bajo `#if canImport(SwiftUI)`).

## Verificación del build

- `swift build --package-path ios` → **Build complete** (exit 0).
- Validación de UI en dispositivo (iPhone 13 Pro): `xtool dev build` — **difiere**
  al dispositivo; en Linux/WSL falla por desajuste compilador/SDK (Swift 6.0.3 vs
  SDK Swift 6.4). Documentado como limitación de toolchain WSL, no un fallo del
  código.

## Troubleshooting

- `libxml2.so.2: no version information available`: aviso benigno de
  `FoundationXML` en Linux; no afecta a build ni tests.
- `xtool dev build` "this SDK is not supported by the compiler": limitación de
  entorno WSL; la validación de vistas se hace en dispositivo.

## Assumptions & Open Questions

None.
