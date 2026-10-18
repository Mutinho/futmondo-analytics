# NFR Design — Security Design (`ios-native-auth`)

> Bolt 3 de F1. Fase: construcción (nfr-design). Idioma: castellano; identificadores/código en
> inglés.

## Keychain (SEC-A1) — diseño
`KeychainTokenStore` usa `SecItemAdd`/`SecItemCopyMatching`/`SecItemDelete` con:
- `kSecClass = kSecClassGenericPassword`, `kSecAttrService = "com.futmondo.app.auth"`,
  `kSecAttrAccount = "refresh_token"`.
- `kSecAttrAccessible = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` (sin iCloud sync, no sale
  del dispositivo, legible en background para el refresh de arranque).
- `save` hace delete+add (upsert) y comprueba `OSStatus`; un fallo se propaga (REL-A4).

## Access token en memoria (SEC-A2) — diseño
- `actor AuthService` guarda `accessToken: String?`.
- Un `TokenHolder` (clase `final`, Sendable) espeja el access token para el `accessTokenProvider`
  síncrono del `NetworkClient`. **Lock portable**: usa `NSLock` (disponible en Foundation de Linux
  y Darwin) para que `TokenHolder` **compile bajo `swift test` en WSL/Linux** — **no**
  `OSAllocatedUnfairLock` (iOS 16+/macOS 13, inexistente en swift-corelibs-foundation, rompería el
  build de tests). API: `get() -> String?`, `set(_:)`, ambos bajo `lock.lock()/unlock()`.
- **Logout borra ambas, en orden seguro**: primero `tokenHolder.set(nil)` (corta de inmediato la
  inyección de `Bearer` para cualquier petición en vuelo que lea el holder), **luego**
  `self.accessToken = nil` dentro del actor. Así ninguna petición posterior al logout puede
  adjuntar el token.

## Password del formulario (SEC-A3) — diseño
Tras `login` OK y en `logout`, `AuthViewModel` ejecuta `password = ""`. `AuthService` no almacena
el password en ningún campo; lo pasa como argumento a `login` y no lo retiene.

## Transporte (SEC-A5) — diseño
`AuthService` construye `APIRequest` para `/auth/*` y los envía por el `NetworkClient` (Bolt 2); el
refresh token va en el header `X-Refresh-Token` (o body) solo sobre HTTPS.

## Face ID (SEC-A6) — diseño
No se importa `LocalAuthentication` en F1; el gancho para Face ID queda como extensión futura
(diferido).

## Sources
- [consumes] security-requirements.md (SEC-A1..A7), functional-spec.md, rules.md (AR2/AR5/AR8).

## Assumptions & Open Questions
None.
