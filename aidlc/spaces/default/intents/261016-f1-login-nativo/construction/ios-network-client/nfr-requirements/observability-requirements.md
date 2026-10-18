# NFR — Observability Requirements (`ios-network-client`)

> Bolt 2 de F1. Idioma: castellano; identificadores/código en inglés.

## OBS-N1 — Logging de diagnóstico sin credenciales
Si el cliente registra algo (opcional), registra método + ruta + status, **nunca** el header
`Authorization` ni los bodies (SEC-N3). En F1 el logging del cliente es mínimo; la observabilidad
del dispositivo es la validación manual.

## Sources
- [consumes] security-requirements.md (SEC-N3), functional-spec.md.

## Assumptions & Open Questions
None.
