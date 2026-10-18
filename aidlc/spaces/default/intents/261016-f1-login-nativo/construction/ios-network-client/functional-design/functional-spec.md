# Functional Spec — `ios-network-client` (Bolt 2 de F1)

> Fase: construcción (functional-design). Capa de red Swift sobre `URLSession`. Idioma: castellano;
> identificadores/código en inglés.

## Objetivo

Proveer una capa HTTP tipada y testeable que todas las pantallas posteriores (F2/F3) y la auth
nativa (Bolt 3) usen para hablar con el backend FastAPI. En F1 se ejercita con una llamada de humo
a `GET /api/v1/user/me` que valida el access token end-to-end.

## Interfaz

```swift
enum HTTPMethod: String { case get = "GET", post = "POST", put = "PUT", delete = "DELETE" }

struct AnyEncodable: Encodable {   // wrapper para codificar cualquier Encodable con JSONEncoder
    private let encodeFunc: (Encoder) throws -> Void
    init<T: Encodable>(_ wrapped: T) { encodeFunc = wrapped.encode }
    func encode(to encoder: Encoder) throws { try encodeFunc(encoder) }
}

struct APIRequest {
    let method: HTTPMethod
    let path: String                 // relative to baseURL
    var headers: [String: String] = [:]
    var body: AnyEncodable? = nil     // envuelve cualquier Encodable; nil = sin body
}

// EmptyResponse permite tipar un 2xx sin cuerpo (p. ej. 204) como T = EmptyResponse.
struct EmptyResponse: Decodable, Equatable {}

enum NetworkError: Error, Equatable {   // payloads String para que sea Equatable y testeable
    case unauthorized                   // 401
    case forbidden                      // 403
    case clientError(Int)               // otros 4xx (400, 404, 422, ...)
    case server(Int)                    // 5xx
    case cancelled                      // CancellationError (no reintentar)
    case transport(String)              // red/offline/timeout (mensaje, no el Error crudo)
    case decoding(String)
    case unexpectedStatus(Int)          // 1xx/3xx u otros no contemplados
}

protocol NetworkClient {
    func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError>
}

final class URLSessionNetworkClient: NetworkClient {
    // init lanzable: rechaza una baseURL no-https con NetworkClientError.insecureBaseURL
    // (no una precondition eliminable con -Ounchecked). ATS por defecto, sin override en Info.plist.
    init(baseURL: URL, session: URLSession = .shared, accessTokenProvider: @escaping () -> String?) throws
    func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError>
}
```

> **Decisión (resuelve la tensión Equatable vs payload)**: `NetworkError` es **la forma
> autoritativa** y `Equatable`; sus payloads son `String`/`Int`, **no** `Error` (porque `Error` no
> es `Equatable` y rompería la síntesis). `entities.md` se alinea a esta forma. El `Error` crudo de
> transporte se convierte a `String` (`error.localizedDescription`) en el borde.

## Comportamiento (reglas NR1–NR6)

1. Construye `URLRequest` con `baseURL + path`, método, headers; añade `Authorization: Bearer` si
   hay token (NR1); serializa el body a JSON si existe (NR2).
2. Ejecuta con `URLSession`; mapea el status/el error a `Result` (NR3):
   - 2xx **con cuerpo** → decodifica a `T`; 2xx **sin cuerpo** (204 o body vacío) → `.success` con
     `T == EmptyResponse` (si el llamador tipa otra `T` no vacía para un 204, es `.decoding`).
   - 401 → `.unauthorized`; 403 → `.forbidden`; otros 4xx (400/404/422…) → `.clientError(status)`;
     5xx → `.server(status)`; 1xx/3xx u otros → `.unexpectedStatus(status)`.
   - `CancellationError` → `.cancelled` (no debe disparar reintentos en AuthService, ADR-4);
     cualquier otro error de red/timeout → `.transport(message)`.
3. Decodifica el body 2xx no vacío a `T` (NR2); fallo → `.decoding(message)` (NR3).

## Llamada de humo (F1)

`GET /api/v1/user/me` con un access token válido → `.success(UserMe)`; sin token válido →
`.failure(.unauthorized)`. Esto valida que el Bearer y el pipeline funcionan contra el backend real.

## Tests (XCTest — nota de posture)

Según P-1 (practices), en F1 **no hay arné XCTest aún**: la verificación del cliente nativo es
**manual** en el iPhone 13 Pro, y el arnés XCTest unitario queda como **deuda registrada**. No
obstante, el diseño es unit-testable: `NetworkClient` es un protocolo con `URLSession` inyectable
(se puede doblar con `URLProtocol` stub cuando se cree el arnés). Los casos a cubrir cuando exista
el arnés: éxito 2xx con decodificación; 401→unauthorized; 403→forbidden; 5xx→server; transporte;
decoding inválido; inyección de Bearer presente/ausente.

## Alcance y límites

- Solo transporte HTTP + mapeo de errores + llamada de humo. Sin Keychain, sin estado de sesión
  (Bolt 3), sin pantallas de datos (F2). Solo SDK de Apple.

## Sources

- [consumes] contract-summary.md, components.md (C1), requirements.md (FR-7, NFR-2, NFR-3),
  rules.md, entities.md.

## Assumptions & Open Questions

None.
