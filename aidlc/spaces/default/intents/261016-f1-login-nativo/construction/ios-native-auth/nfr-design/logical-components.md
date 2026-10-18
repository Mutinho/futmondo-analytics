# NFR Design — Logical Components (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés.

| Componente lógico | Rol | Ubicación objetivo (SwiftPM / app) |
|-------------------|-----|-------------------------------------|
| `KeychainStore` (protocol) | Contrato del almacén seguro | `Sources/FutmondoKit/Auth/KeychainStore.swift` |
| `KeychainTokenStore` | Impl Keychain Services | `Sources/FutmondoKit/Auth/KeychainTokenStore.swift` |
| `TokenHolder` | Snapshot Sendable del access token (lock) | `Sources/FutmondoKit/Auth/TokenHolder.swift` |
| `AuthService` (actor) + protocolo | Sesión: login/refresh/bootstrap/logout, reintento coalescido | `Sources/FutmondoKit/Auth/AuthService.swift` |
| DTOs de auth | Login/Refresh request/response (Codable) | `Sources/FutmondoKit/Auth/AuthDTOs.swift` |
| `AuthViewModel` | Estado de UI (`@Observable`) | app target `Sources/FutmondoApp/AuthViewModel.swift` |
| `LoginView` / `SplashView` | UI SwiftUI | app target `Sources/FutmondoApp/LoginView.swift`, `SplashView.swift` |

> La lógica testeable sin dispositivo (`AuthService` con dobles de `NetworkClient` y `KeychainStore`)
> vive en `FutmondoKit` para que `swift test` la cubra. Las vistas y el `KeychainTokenStore` real
> (SecItem/UI) se validan en el iPhone. El nombre del app target (`FutmondoApp`) se confirma al
> integrar con el proyecto `xtool`.

## Sources
- [consumes] functional-spec.md, components.md (C2-C5), security-design.md.

## Assumptions & Open Questions
None.
