# Code Summary — `ios-network-client` (Bolt 2 de F1)

> Fase: construcción (code-generation). Capa de red Swift. Idioma: castellano;
> identificadores/código/comentarios en inglés. Solo SDK de Apple; cero dependencias externas.

## Qué se creó

Paquete SwiftPM `FutmondoKit` bajo `ios/`, con un target library y un test target:

| Fichero | Rol |
|---------|-----|
| `ios/Package.swift` | Manifiesto SwiftPM (`swift-tools-version:6.0`); library `FutmondoKit` + test target `FutmondoKitTests`; `platforms` iOS 15 / macOS 12 para que `swift test` compile en Linux/WSL sobre Foundation; sin dependencias. |
| `ios/xtool.yml` | Config mínima de `xtool` (version, `bundleID` placeholder `com.futmondo.app`, `product`) para el build en WSL. |
| `ios/Sources/FutmondoKit/Networking/HTTPMethod.swift` | `enum HTTPMethod: String` (`get`/`post`/`put`/`delete`). |
| `ios/Sources/FutmondoKit/Networking/APIRequest.swift` | `struct APIRequest`, `struct AnyEncodable` (wrapper type-erased `Encodable`), `struct EmptyResponse: Decodable, Equatable`. |
| `ios/Sources/FutmondoKit/Networking/NetworkError.swift` | `enum NetworkError: Error, Equatable` con los 8 casos (`unauthorized`, `forbidden`, `clientError(Int)`, `server(Int)`, `cancelled`, `transport(String)`, `decoding(String)`, `unexpectedStatus(Int)`). |
| `ios/Sources/FutmondoKit/Networking/NetworkClient.swift` | `protocol NetworkClient` (`send<T: Decodable>(_:) async -> Result<T, NetworkError>`) + `enum NetworkClientError { case insecureBaseURL }`. |
| `ios/Sources/FutmondoKit/Networking/URLSessionNetworkClient.swift` | `final class` que implementa `NetworkClient`: init lanzable que valida `https` (SEC-N1), inyección de `Bearer` por request sin retención (SEC-N2/NR1), serialización JSON del body (NR2), mapeo completo de estados (NR3) y errores sin material sensible (SEC-N4). |
| `ios/Sources/FutmondoKit/Networking/UserMe.swift` | DTO de humo `/api/v1/user/me` (`userId`/`email`, `CodingKeys` snake_case). |
| `ios/Tests/FutmondoKitTests/NetworkClientTests.swift` | XCTest (14 tests) con `MockURLProtocol` inyectado vía `URLSessionConfiguration.ephemeral`, que aseveran el efecto de cada rama. |

## Enfoque

- **Seguridad del transporte (SEC-N1)**: la base URL se valida con un **init lanzable**
  (`guard baseURL.scheme?.lowercased() == "https" else { throw .insecureBaseURL }`), no una
  `precondition` eliminable con `-Ounchecked`. Sin override de ATS.
- **Token (SEC-N2/N3/NR1)**: `accessTokenProvider` se invoca en cada `send`; el `Bearer` se añade al
  `URLRequest` local solo si el token no está vacío; el cliente no guarda el token en ninguna
  propiedad ni lo loguea. Un token vacío se trata como ausencia de token.
- **Mapeo (NR3)**: 2xx con cuerpo → decode `T`; 2xx vacío (o `T == EmptyResponse`) → `.success(EmptyResponse)`;
  401 → `.unauthorized`; 403 → `.forbidden`; otros 4xx → `.clientError(status)`; 5xx → `.server(status)`;
  1xx/3xx → `.unexpectedStatus(status)`; `CancellationError` / `URLError(.cancelled)` → `.cancelled`;
  otro error de red → `.transport(localizedDescription)`; fallo de decode → `.decoding(message)`.
- **Errores sin material sensible (SEC-N4)**: solo cruzan el borde `Int` (status) o
  `error.localizedDescription`; nunca `userInfo`, el `Error` crudo ni la URL con query.
- **Portabilidad Linux/WSL**: `#if canImport(FoundationNetworking)` para importar la API de
  `URLSession` async en Linux; los tests usan `URLProtocol` stub, sin red real ni dispositivo.

## Verificación — IMPORTANTE

**No se ejecutó `swift test` en este entorno**: el entorno del agente **no tiene toolchain Swift**
(`swift`/`swift test`/`xtool` no están disponibles). Los XCTest están **escritos, son reales y
aseveran el efecto** (no `assert True`, no specs espejo), listos para ejecutarse. La verificación la
realiza **el propietario en WSL** (opción A acordada, Swift 6.4 del spike F0):

```bash
cd ios && swift test
```

Es verificación real y reproducible (lógica pura con `URLProtocol` stub, sin iPhone ni macOS). La
validación end-to-end en el iPhone 13 Pro (`cd ios && xtool dev build`) corresponde sobre todo al
Bolt 3.

## Cobertura de los tests (14 casos, aseveran el efecto)

2xx decodifica `UserMe`; 2xx vacío → `EmptyResponse`; 401 → `.unauthorized`; 403 → `.forbidden`;
404 → `.clientError(404)`; 503 → `.server(503)`; fallo de red → `.transport`; JSON inválido →
`.decoding`; 302 → `.unexpectedStatus(302)`; `Bearer` presente con token; `Bearer` ausente sin token;
token vacío no inyecta `Bearer`; init rechaza `http://` (`XCTAssertThrowsError` → `.insecureBaseURL`);
init acepta `https://`.

## Sources

- [consumes] code-generation-plan.md, unit-test-instructions.md, functional-spec.md, entities.md,
  rules.md (NR1–NR6), security-design.md (SEC-N1..N4), logical-components.md, requirements.md
  (FR-7, NFR-1, NFR-2, NFR-3).

## Assumptions & Open Questions

None.
