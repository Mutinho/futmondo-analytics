# NFR — Security Requirements (`ios-native-auth`)

> Bolt 3 de F1. Fase: construcción (nfr-requirements). Idioma: castellano; identificadores/código
> en inglés. El eje crítico es el almacenamiento seguro de credenciales.

## SEC-A1 — Refresh token solo en iOS Keychain
El refresh token se guarda **exclusivamente** en el Keychain (Keychain Services), con
accesibilidad `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` (no sincroniza a iCloud, no sale
del dispositivo). Nunca en `UserDefaults`/plist/archivos en claro (FR-3, NFR-1, [memory:M2]).

## SEC-A2 — Access token solo en memoria (actor + snapshot), borrado completo en logout
El access token vive en memoria del `actor AuthService` **y** en un **snapshot** (`TokenHolder`
con lock) que el provider síncrono del `NetworkClient` lee. **Logout debe borrar AMBAS
ubicaciones**: `AuthService.accessToken = nil` **y** `TokenHolder` puesto a `nil`; no basta con
limpiar el actor (si no, el token quedaría legible en el holder tras logout). El snapshot nunca se
persiste; solo existe en memoria mientras hay sesión.

## SEC-A3 — Nada de credenciales en logs, y borrado del password del formulario
Ni el access token, ni el refresh token, ni la password se registran (logs, `print`, mensajes de
error). El password Futmondo del usuario **no se retiene**: `AuthService` lo envía y lo descarta,
**y** `AuthViewModel.password` se **limpia (`= ""`) tras un login exitoso y en logout**, para que
el string del `SecureField` no persista en memoria del ViewModel mientras la vista vive.

## SEC-A7 — Supervivencia del Keychain ante re-firma gratuita (~7 días)
Con firma gratuita el provisioning caduca ~7 días y el bundle ID va prefijado por el team ID
personal; al re-firmar/reinstalar, el item del Keychain puede **no** ser legible (access-group
ligado al provisioning). Comportamiento esperado y seguro: si `readRefreshToken()` falla/devuelve
`nil`, `bootstrap` resuelve `.unauthenticated` y el usuario re-loguea (no es fuga; cae al lado
seguro). Se documenta como expectativa, no como fallo.

## SEC-A4 — Borrado en logout
`logout` borra el refresh token del Keychain y limpia el access token en memoria, aunque la
revocación en backend falle (red caída). `pendingLogoutRevocation` es solo un booleano, no copia
del token.

## SEC-A5 — Transporte seguro reutilizado
Todas las llamadas usan el `NetworkClient` del Bolt 2 (HTTPS/ATS, init que rechaza no-https). El
refresh token viaja por header `X-Refresh-Token`/body solo sobre TLS (D-01).

## SEC-A6 — Solo SDK de Apple
`Security` (Keychain), `SwiftUI`, `Foundation`; cero librerías de terceros (NFR-2/P-3).
`LocalAuthentication`/Face ID queda fuera de F1 (diferido).

## Sources
- [consumes] functional-spec.md, rules.md (AR2/AR5/AR7/AR8), requirements.md (FR-2, FR-3, NFR-1,
  NFR-2), contract-summary.md.
- [memory] credenciales/tokens nunca en claro; refresh token en Keychain.

## Assumptions & Open Questions
None.
