# NFR — Reliability Requirements (`ios-network-client`)

> Bolt 2 de F1. Idioma: castellano; identificadores/código en inglés.

## REL-N1 — Mapeo de fallos exhaustivo
Todo resultado se mapea a `.success` o a un caso tipado de `NetworkError` (unauthorized, forbidden,
clientError, server, cancelled, transport, decoding, unexpectedStatus); no hay caminos de error
silenciosos ni `fatalError`.

## REL-N2 — 2xx sin cuerpo no es fallo
Un 204/respuesta vacía se trata como éxito (`EmptyResponse`), no como `.decoding`.

## REL-N3 — Cancelación distinguida
`CancellationError` → `.cancelled`, para que AuthService no la confunda con un fallo de red y no
reintente (ADR-4).

## Sources
- [consumes] functional-spec.md, rules.md (NR3).

## Assumptions & Open Questions
None.
