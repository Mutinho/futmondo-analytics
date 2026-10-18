# NFR Design — Reliability Design (`ios-network-client`)

> Bolt 2 de F1. Idioma: castellano; identificadores/código en inglés.

## REL-N1 diseño — mapeo exhaustivo
`send` cubre todas las ramas en un único switch sobre el status + manejo de `URLError`/
`CancellationError`; cada camino devuelve `.success` o un caso de `NetworkError` (sin
`fatalError`, sin camino silencioso).

## REL-N2 diseño — 2xx vacío
Si `T == EmptyResponse` o el body está vacío con 2xx, devuelve `.success(EmptyResponse())` sin
intentar decodificar.

## REL-N3 diseño — cancelación
`catch is CancellationError → .cancelled`, evaluado antes del `catch` genérico de transporte.

## Sources
- [consumes] reliability-requirements.md, functional-spec.md (NR3).

## Assumptions & Open Questions
None.
