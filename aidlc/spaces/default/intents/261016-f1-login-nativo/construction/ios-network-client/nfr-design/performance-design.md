# NFR Design — Performance Design (`ios-network-client`)

> Bolt 2 de F1. Idioma: castellano; identificadores/código en inglés.

`send` es `async` sobre `URLSession.data(for:)`; no bloquea el hilo principal. Sin reintentos en el
cliente (la política vive en AuthService, ADR-4). Timeouts por defecto de `URLSession`.

## Sources
- [consumes] performance-requirements.md, functional-spec.md.

## Assumptions & Open Questions
None.
