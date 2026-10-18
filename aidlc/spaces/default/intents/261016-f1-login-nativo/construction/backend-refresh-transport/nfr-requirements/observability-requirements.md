# NFR — Observability Requirements (`backend-refresh-transport`)

> Bolt 1 de F1. Idioma: castellano; tokens técnicos verbatim en inglés. Adaptado al stack real
> (Fly.io + logging estructurado), coste 0 €.

## OBS-1 — Logs sin credenciales
Los logs existentes de `/auth/*` (`logger.info`/`warning`) se conservan; **no** se añade logging
del refresh token ni de bodies (SEC-2). Un nuevo log puede indicar el **canal** usado
(`cookie`/`header`/`body`) **sin** el valor del token, útil para diagnóstico.

## OBS-2 — Herramientas gratuitas
Diagnóstico vía `fly logs` y el logging estructurado existente; no se introduce tracing/APM de
pago (coherente con coste 0 € y el aprendizaje de operación del proyecto).

## Sources
- [consumes] functional-spec.md; operation-fly-stack (knowledge compartido).

## Assumptions & Open Questions
None.
