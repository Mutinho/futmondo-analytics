# NFR Design — Performance Design (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés.

`bootstrap` y las acciones de auth son `async` (no bloquean el main actor); el Splash muestra
`ProgressView`. El refresh coalescido (`refreshInFlight` en el actor) evita trabajo duplicado. El
acceso al Keychain es local.

## Sources
- [consumes] performance-requirements.md, security-design.md.

## Assumptions & Open Questions
None.
