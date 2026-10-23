# Build Instructions — Sistema de diseño nativo iOS

> Fase: construcción. Idioma: identificadores/comandos en INGLÉS; prosa en castellano.

## Prerrequisitos

- Toolchain de Swift (6.x) en Linux/WSL o macOS. Sin dependencias externas (sólo SDK de Apple / Foundation).
- No requiere red, BD ni servicios locales.

## Setup de entorno

Ninguno especial: el paquete SwiftPM `ios/` no necesita variables de entorno ni secretos para compilar/testear.

## Build

```
cd ios && swift build
```

Compila `FutmondoKit` (lógica, incluida la del sistema de diseño), `FutmondoApp` (vistas SwiftUI guardadas con `#if canImport(SwiftUI)`, incluidos los componentes del sistema de diseño y el login revestido) y el target de tests.

## Verificación de build

- Salida esperada: `Build complete!`, sin errores.
- Aviso conocido inofensivo en WSL: `libxml2.so.2: no version information available` (ruido del toolchain, no error).

## Troubleshooting

- Si `actool` fallara al empaquetar un asset catalog en WSL: los Color Sets del sistema de diseño están definidos EN CÓDIGO (DSColorToken), no en `Assets.xcassets` (aprendizaje durable); no debería aparecer.
- `ios/.build/` son artefactos de compilación; no deben versionarse (ver nota de `.gitignore` en el summary).

## Assumptions & Open Questions

None.
