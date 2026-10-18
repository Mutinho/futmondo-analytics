# NFR Design — Reliability Design (`backend-refresh-transport`)

> Bolt 1 de F1. Idioma: castellano; tokens técnicos verbatim en inglés.

## REL-1 diseño — body opcional
El parámetro de body se declara `Optional[RefreshBodyOptional] = None`, garantizando que una
petición sin body (PWA por cookie) no produce 422. Es el punto de fiabilidad clave del bolt.

## REL-2 diseño — logout idempotente
`logout` resuelve el token por `resolve_refresh_token`; si es `None`, responde el mismo
`{success, message}` que hoy sin error. La revocación por hash es idempotente.

## REL-3 diseño — rehidratación sin cambios
El bloque best-effort de `ensure_session` en refresh se conserva íntegro.

## Sources
- [consumes] reliability-requirements.md, functional-spec.md.

## Assumptions & Open Questions
None.
