# NFR Design — Observability Design (`backend-refresh-transport`)

> Bolt 1 de F1. Idioma: castellano; tokens técnicos verbatim en inglés.

Logging existente conservado; opcionalmente un log de diagnóstico con el **canal** usado
(`cookie`/`header`/`body`), nunca el token (SEC-2). Diagnóstico vía `fly logs`. Sin tracing/APM de
pago (coste 0 €).

## Sources
- [consumes] observability-requirements.md, security-design.md.

## Assumptions & Open Questions
None.
