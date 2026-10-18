# Functional Design — Rules (`ios-network-client`)

> Bolt 2 de F1. Idioma: castellano; identificadores/código en inglés.

## NR1 — Inyección de Bearer
Si `accessTokenProvider()` devuelve un token no vacío, `send` añade el header
`Authorization: Bearer <token>`. Si no hay token, no se añade el header (el backend responderá 401,
mapeado a `.unauthorized`).

## NR2 — Serialización JSON
El `body` (si existe) se codifica como JSON (`Content-Type: application/json`); la respuesta se
decodifica a `T` con `JSONDecoder`. Un fallo de decodificación → `.decoding`.

## NR3 — Mapeo de estados a errores tipados (completo)
- 2xx con cuerpo → `.success(T)`; 2xx sin cuerpo (204/body vacío) → `.success(EmptyResponse)`.
- 401 → `.unauthorized`; 403 → `.forbidden`; otros 4xx (400/404/422…) → `.clientError(status)`.
- 5xx → `.server(status)`; 1xx/3xx u otros no contemplados → `.unexpectedStatus(status)`.
- `CancellationError` → `.cancelled` (no reintentar); otro error de transporte (sin respuesta,
  offline, timeout) → `.transport(message)`. Fallo de decodificación → `.decoding(message)`.

## NR4 — Base URL configurable
La base URL se inyecta (p. ej. producción vs. local); el cliente no la hardcodea. Las rutas se
construyen uniendo `baseURL` + `path`.

## NR5 — Sin estado de sesión ni Keychain
Este cliente **no** lee ni escribe el Keychain ni mantiene el access token; solo lo adjunta vía el
provider inyectado. La gestión de sesión es del Bolt 3.

## NR6 — Solo SDK de Apple
`URLSession`, `Codable`, `JSONEncoder/Decoder`. Cero librerías de terceros (NFR-2).

## Sources

- [consumes] contract-summary.md (NetworkClient), components.md (C1), requirements.md (FR-7, NFR-2).

## Assumptions & Open Questions

None.
