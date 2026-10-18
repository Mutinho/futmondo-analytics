# NFR — Performance Requirements (`backend-refresh-transport`)

> Bolt 1 de F1. Idioma: castellano; tokens técnicos verbatim en inglés.

## PERF-1 — Sin coste de latencia añadido
El ajuste solo cambia **de dónde se lee** el refresh token (cookie/header/body) y **añade una
clave** al body de login; no añade I/O, consultas ni llamadas de red nuevas. La latencia de
`/auth/*` es equivalente a la actual.
- **Verificación**: la resolución del token es una expresión en memoria (`cookie or header or
  body`); no hay nuevas queries.

## Sources
- [consumes] functional-spec.md, requirements.md.

## Assumptions & Open Questions
None.
