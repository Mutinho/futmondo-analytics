# NFR Design — Security Design (`ios-network-client`)

> Bolt 2 de F1. Fase: construcción (nfr-design). Idioma: castellano; identificadores/código en
> inglés.

## Diseño de la inyección segura del token (SEC-N2)
`URLSessionNetworkClient` recibe `accessTokenProvider: () -> String?` y lo llama **en cada
petición** justo antes de construir el `URLRequest`:
```
if let token = accessTokenProvider(), !token.isEmpty {
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
}
```
El cliente **no** guarda el token en ninguna propiedad; vive solo en el `URLRequest` local.

## TLS/ATS (SEC-N1) — mecanismo de enforcement
La base URL `https://` se valida con un **init lanzable** (no una `precondition`, que es eliminable
con `-Ounchecked` y dejaría pasar `http://` en release):
```
enum NetworkClientError: Error { case insecureBaseURL }

init(baseURL: URL, session: URLSession = .shared, accessTokenProvider: @escaping () -> String?) throws {
    guard baseURL.scheme?.lowercased() == "https" else { throw NetworkClientError.insecureBaseURL }
    ...
}
```
El rechazo de un esquema no-`https` es un **error tipado propagado** en construcción, no una
aserción eliminable. ATS queda en su valor por defecto estricto; **prohibido** cualquier override
en `Info.plist` (SEC-N1 requirement).

## No logging de credenciales (SEC-N3)
El cliente no instala logging de `Authorization`/body. Si se añade un log de diagnóstico, enmascara
el header `Authorization` (`Bearer ***`).

## Errores tipados sin material sensible (SEC-N4)
El mapeo a `NetworkError` usa **solo** el status (`Int`) y, para transporte/decoding, un mensaje
derivado **únicamente** de `error.localizedDescription` — **nunca** `userInfo`,
`String(describing: error)` ni la URL con query (que podría llevar material sensible). Esto cubre
los ocho casos de `NetworkError` del functional-spec: cada caso carga solo un `Int` (status) o un
`String` de modo de fallo, jamás el token ni el cuerpo de credenciales.

## Sources
- [consumes] security-requirements.md (SEC-N1..N5), functional-spec.md, contract-summary.md.

## Assumptions & Open Questions
None.
