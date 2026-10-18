# NFR — Observability Requirements (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés.

## OBS-A1 — Logs sin credenciales
Si se registra el ciclo de sesión (login OK/fallo, refresh, logout), **nunca** se incluye el token
ni la password; solo el evento y, como mucho, el modo de fallo. En F1 la observabilidad real es la
validación manual en el iPhone.

## Sources
- [consumes] security-requirements.md (SEC-A3), functional-spec.md.

## Assumptions & Open Questions
None.
