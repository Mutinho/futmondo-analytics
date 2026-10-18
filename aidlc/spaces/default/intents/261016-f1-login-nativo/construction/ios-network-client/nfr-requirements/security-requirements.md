# NFR — Security Requirements (`ios-network-client`)

> Bolt 2 de F1. Fase: construcción (nfr-requirements). Idioma: castellano; identificadores/código
> en inglés. Capa de red Swift.

## SEC-N1 — TLS obligatorio
Todas las peticiones van sobre **HTTPS**; `URLSession` con ATS (App Transport Security) por
defecto (sin excepciones de dominio en claro). La base URL de producción es `https://`.
- **Prohibido** un override de ATS en `Info.plist` (`NSAllowsArbitraryLoads` u
  `NSExceptionAllowsInsecureHTTPLoads`), riesgo agravado por la base URL inyectable (NR4): la base
  URL siempre debe ser `https://` y ATS queda en su valor por defecto estricto.

## SEC-N2 — El cliente no persiste credenciales
El `NetworkClient` **no** guarda el access token ni el refresh token; recibe el access token por
`accessTokenProvider` (inyectado por el Bolt 3) y lo adjunta como `Authorization: Bearer` solo en
memoria durante la petición. El refresh token nunca pasa por este cliente.
- El closure `accessTokenProvider` es de **pull** (`() -> String?`): **no retiene** una copia del
  token; lo lee en el momento de cada petición. No se captura el token en una variable del cliente.

## SEC-N3 — No registrar tokens ni headers de credencial
El cliente no hace logging del header `Authorization`, ni del body, ni de los tokens. Si se añade
logging de diagnóstico, se omite/enmascara `Authorization`.
- **Nota (debug)**: un proxy de depuración MITM (p. ej. Charles) podría interceptar el tráfico TLS
  si se instala un certificado de confianza en el dispositivo; riesgo inherente y acotado a
  entornos de desarrollo. No se habilita en builds de distribución.

## SEC-N4 — Errores sin filtrar material sensible
Los `NetworkError` (`.transport(String)`, `.decoding(String)`) usan mensajes de modo de fallo
(status, descripción de red), **nunca** el token ni cuerpos con credenciales.

## SEC-N5 — Solo SDK de Apple
`URLSession`/`Codable` del SDK; cero librerías de terceros que pudieran interceptar/enviar datos
(NFR-2).

## Sources

- [consumes] functional-spec.md, rules.md, requirements.md (FR-7, NFR-1, NFR-2),
  contract-summary.md, technology-stack.md.
- [memory] credenciales/tokens nunca en claro.

## Assumptions & Open Questions

None.
