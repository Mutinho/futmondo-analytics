# NFR — Scalability Requirements (`ios-network-client`)

> Bolt 2 de F1. Idioma: castellano; identificadores/código en inglés.

## SCAL-N1 — Cliente stateless y reutilizable
Una instancia de `NetworkClient` (con base URL + provider) se reutiliza para todas las llamadas de
la app; no mantiene estado por petición. No hay preocupación de escalado del lado cliente.

## Sources
- [consumes] functional-spec.md.

## Assumptions & Open Questions
None.
