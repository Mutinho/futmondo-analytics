# NFR Design — Reliability Design (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés.

## REL-A1 diseño — bootstrap exhaustivo
`bootstrap` mapea el resultado del `refresh` a `.authenticated` / `.unauthenticated` /
`.offlinePreserved` según el `NetworkError` (401/revocado → borra Keychain → unauthenticated;
`.transport`/`.server`/`.unexpectedStatus` → offlinePreserved). Nunca cuelga.

## REL-A2 diseño — reintento único + coalescing
`refreshInFlight: Task<String, Error>?` en el actor: la primera petición con 401 crea la Task; las
concurrentes la esperan; al terminar se limpia. Cada petición reintenta una vez.

## REL-A3 diseño — logout resiliente
`logout` limpia Keychain + actor + holder y marca `pendingLogoutRevocation` (UserDefaults) si la
red falla; en `bootstrap` futuro con red se reintenta la revocación.

## REL-A4 diseño — errores de Keychain
`KeychainTokenStore` convierte `OSStatus != errSecSuccess` (salvo `errSecItemNotFound` en read, que
devuelve `nil`) en un error propagado; `save`/`delete` no asumen éxito.

## Sources
- [consumes] reliability-requirements.md, functional-spec.md, security-design.md.

## Assumptions & Open Questions
None.
