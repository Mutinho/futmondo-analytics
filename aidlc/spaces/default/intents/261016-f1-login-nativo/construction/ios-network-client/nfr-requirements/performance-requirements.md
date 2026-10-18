# NFR — Performance Requirements (`ios-network-client`)

> Bolt 2 de F1. Idioma: castellano; identificadores/código en inglés.

## PERF-N1 — async/await no bloqueante
`send` es `async`; no bloquea el hilo principal. La UI (Bolt 3) llama en contextos async. Timeouts
razonables de `URLSession` (default); sin reintentos en el cliente (la política de reintento vive
en AuthService, ADR-4).

## Sources
- [consumes] functional-spec.md.

## Assumptions & Open Questions
None.
