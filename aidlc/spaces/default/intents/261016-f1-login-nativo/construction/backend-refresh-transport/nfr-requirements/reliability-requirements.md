# NFR — Reliability Requirements (`backend-refresh-transport`)

> Bolt 1 de F1. Idioma: castellano; tokens técnicos verbatim en inglés.

## REL-1 — No-regresión como invariante de fiabilidad
El canal cookie de la PWA sigue funcionando idéntico; una petición de refresh **sin body** no
produce 422 (fiabilidad del canal existente). Cubierto por tests de no-regresión.

## REL-2 — Logout idempotente
`logout` responde sin error aunque no haya token por ningún canal (BR6); revoca por hash de forma
idempotente.

## REL-3 — Degradación de rehidratación de sesión sin cambios
La rehidratación best-effort en refresh (`get_session_service().ensure_session`) se mantiene tal
cual; un fallo transitorio no rompe el refresh (comportamiento actual preservado).

## Sources
- [consumes] functional-spec.md, rules.md, requirements.md (FR-9).

## Assumptions & Open Questions
None.
