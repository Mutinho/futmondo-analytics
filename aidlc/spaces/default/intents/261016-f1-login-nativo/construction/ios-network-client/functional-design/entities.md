# Functional Design — Entities (`ios-network-client`)

> Bolt 2 de F1. Fase: construcción (functional-design). Idioma: castellano; identificadores/código
> en inglés. Capa de red Swift (C1 `NetworkClient`) sobre `URLSession`.

## Tipos (Swift)

### `APIRequest`
Valor que describe una petición: `method: HTTPMethod` (enum `.get/.post/...`), `path: String`
(relativo a la base URL), `headers: [String: String]`, `body: AnyEncodable?` (wrapper que envuelve
cualquier `Encodable` para `JSONEncoder`; `nil` = sin body).

### `NetworkError` (enum, errores tipados, **Equatable** — forma autoritativa)
`.unauthorized` (401), `.forbidden` (403), `.clientError(Int)` (otros 4xx: 400/404/422…),
`.server(Int)` (5xx), `.cancelled` (CancellationError, no reintentar), `.transport(String)`
(red/offline/timeout; `String`, no `Error`, para que el enum sea `Equatable`),
`.decoding(String)`, `.unexpectedStatus(Int)` (1xx/3xx u otros). Accionables por el llamador.

### `EmptyResponse`
`struct EmptyResponse: Decodable, Equatable {}` — tipa un 2xx sin cuerpo (p. ej. 204).

### `NetworkClient` (protocolo + impl `URLSessionNetworkClient`)
- `baseURL: URL` configurable (inyectado).
- `accessTokenProvider: () -> String?` para inyectar `Authorization: Bearer` cuando hay token.
- `func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError>`.

### `UserMe` (DTO de humo)
Modelo `Decodable` mínimo para `GET /api/v1/user/me` (p. ej. `user_id`, `email`): solo para la
llamada de humo que valida el token end-to-end. No es el modelo final de usuario (eso es F2).

## No hay entidades de dominio ni persistencia en este bolt

El Keychain y el estado de sesión viven en el Bolt 3 (`ios-native-auth`). Este bolt es transporte
puro.

## Sources

- [consumes] components.md (C1), contract-summary.md (NetworkClient, /api/v1/user/me),
  requirements.md (FR-7), unit-of-work.md.

## Assumptions & Open Questions

None.
