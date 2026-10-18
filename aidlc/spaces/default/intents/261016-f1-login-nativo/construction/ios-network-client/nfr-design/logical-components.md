# NFR Design — Logical Components (`ios-network-client`)

> Bolt 2 de F1. Idioma: castellano; identificadores/código en inglés.

| Componente lógico | Rol | Ubicación objetivo (SwiftPM target) |
|-------------------|-----|-------------------------------------|
| `NetworkClient` (protocol) | Contrato de red | `Sources/FutmondoKit/Networking/NetworkClient.swift` |
| `URLSessionNetworkClient` | Impl sobre URLSession | `Sources/FutmondoKit/Networking/URLSessionNetworkClient.swift` |
| `APIRequest`, `HTTPMethod`, `AnyEncodable`, `EmptyResponse` | Tipos de petición | `Sources/FutmondoKit/Networking/APIRequest.swift` |
| `NetworkError` | Errores tipados | `Sources/FutmondoKit/Networking/NetworkError.swift` |
| `UserMe` | DTO de humo (/api/v1/user/me) | `Sources/FutmondoKit/Networking/UserMe.swift` |

> Rutas tentativas dentro del paquete SwiftPM del proyecto `xtool`; el nombre del módulo
> (`FutmondoKit`) se confirma en code-generation. Sin clases nuevas de estado ni Keychain (Bolt 3).

## Sources
- [consumes] functional-spec.md, components.md (C1), security-design.md.

## Assumptions & Open Questions
None.
