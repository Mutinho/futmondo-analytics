# NFR Requirements — Questions (U2 `u2-budget-ui`)

> Fase: construcción. Unidad: `u2-budget-ui`. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de NFR Requirements de U2:

- **Performance (NFR4)**: PR1 `List`/`LazyVStack` para scroll fluido (60 fps); PR2 estado `loading` síncrono antes del `await` → indicador <100 ms. Verificación en dispositivo (no medible en WSL).
- **Seguridad (NFR2)**: SR1 la UI no maneja tokens/credenciales (consume servicios de U1); errores sin fuga heredados de U1; SR2 `UserDefaults` sólo el id activo; SR3 sin red nueva.
- **Tech stack**: TS1 cero dependencias nuevas; TS2 target `FutmondoApp` bajo `#if canImport(SwiftUI)`, sin XCTest de vistas en WSL (lógica ya testeada en U1); TS3 Liquid Glass automático del SDK.

¿Does this all look correct?

[Answer]: Looks correct
