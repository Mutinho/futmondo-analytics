# NFR — Scalability Requirements (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés.

## SCAL-A1 — App de un usuario por dispositivo
F1 gestiona la sesión de un único usuario en el dispositivo; no hay preocupación de escalado
cliente. Una instancia de `AuthService` (actor) por app.

## Sources
- [consumes] functional-spec.md.

## Assumptions & Open Questions
None.
