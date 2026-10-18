# NFR — Scalability Requirements (`backend-refresh-transport`)

> Bolt 1 de F1. Idioma: castellano; tokens técnicos verbatim en inglés.

## SCAL-1 — Sin impacto en escalabilidad
El ajuste es stateless (como el auth actual); no cambia el modelo de concurrencia ni la carga
sobre Neon PostgreSQL. No requiere escalado adicional.

## Sources
- [consumes] functional-spec.md, technology-stack.md.

## Assumptions & Open Questions
None.
