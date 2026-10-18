# NFR Design — Performance Design (`backend-refresh-transport`)

> Bolt 1 de F1. Idioma: castellano; tokens técnicos verbatim en inglés.

La resolución del token es una expresión en memoria (`cookie or header or body`); no añade I/O ni
queries. El coste por request es despreciable y equivalente al actual. Sin diseño de caché ni
optimización necesarios.

## Sources
- [consumes] performance-requirements.md, security-design.md.

## Assumptions & Open Questions
None.
