# NFR — Reliability Requirements (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés.

## REL-A1 — Bootstrap no cuelga
`bootstrap` siempre resuelve a `.authenticated`, `.unauthenticated` o `.offlinePreserved`; ante
red/5xx preserva el Keychain y no deja el Splash colgado (AR3).

## REL-A2 — Reintento único sin bucle + coalescing
El refresh ante 401 es único por petición y coalescido globalmente (AR4); nunca bucle ni tormenta.

## REL-A3 — Logout resiliente
`logout` limpia el estado local aunque la red falle; la revocación pendiente se reintenta o caduca
por TTL (AR5). El `actor` evita estados inconsistentes por concurrencia (AR8).

## REL-A4 — Keychain: manejo de errores
Las operaciones de Keychain (`SecItem*`) comprueban el `OSStatus`; un fallo de guardado se propaga
como error accionable (no se asume éxito silencioso).

## Sources
- [consumes] functional-spec.md, rules.md (AR3, AR4, AR5, AR8).

## Assumptions & Open Questions
None.
