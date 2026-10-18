# Code Summary — `ios-native-auth` (Bolt 3 de F1)

> Fase: construcción (code-generation). Auth nativa iOS. Idioma: castellano;
> identificadores/código/comentarios en inglés. Solo SDK de Apple + `FutmondoKit` (Bolt 2); cero
> dependencias externas (NFR-2 / P-3).

## Qué se construyó

Login nativo end-to-end: `AuthService` (actor) dueño de la sesión, `KeychainStore` para el refresh
token, `TokenHolder` como snapshot síncrono del access token para el `accessTokenProvider` del
`NetworkClient` (Bolt 2), DTOs `Codable`, y la capa SwiftUI (`AuthViewModel` + `LoginView` +
`SplashView` + `@main FutmondoApp`).

## Ficheros creados

En `ios/Sources/FutmondoKit/Auth/` (lógica testeable, compila en Linux):

| Fichero | Rol |
|---------|-----|
| `KeychainStore.swift` | Protocolo del almacén seguro del refresh token (AR2). |
| `KeychainTokenStore.swift` | Impl real `SecItem` (service `com.futmondo.app.auth`, account `refresh_token`, `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`, upsert delete+add, chequeo de `OSStatus`, `read` → `nil` en `errSecItemNotFound`), envuelta en `#if canImport(Security)` (SEC-A1 / REL-A4). |
| `InMemoryKeychainStore.swift` | Doble in-memory (clase + `NSLock`) para `swift test`, sin `Security`. |
| `TokenHolder.swift` | Snapshot `Sendable` del access token con `NSLock` (NO `OSAllocatedUnfairLock`, para compilar en Linux) (SEC-A2 / AR8). |
| `AuthDTOs.swift` | `LoginRequestDTO`, `LoginResponseDTO` (incl. `refresh_token`, D-01), `RefreshRequestDTO`, `RefreshResponseDTO`, con `CodingKeys` snake_case; `Sendable`. |
| `AuthError.swift` | `enum AuthError: Error, Equatable, Sendable`; además, conformidades `Sendable` locales para los tipos reutilizados de Bolt 2 (`EmptyResponse`, `UserMe`, `NetworkError`, `URLSessionNetworkClient`) sin tocar su fuente revisada. |
| `Session.swift` | `struct Session` (access token en memoria + `UserMe`) y `enum SessionState` (`authenticated`/`unauthenticated`/`offlinePreserved`), `Sendable`. |
| `AuthService.swift` | `actor AuthService`: `login`/`refresh`/`bootstrap`/`logout`, reintento coalescido (`refreshInFlight: Task`), borrado doble en logout, `accessTokenProvider()` nonisolated que lee el `TokenHolder`. |
| `LogoutFlagStore.swift` | Abstracción `Sendable` del booleano `pendingLogoutRevocation` (`UserDefaults`-backed en prod, in-memory en test); desacopla el actor de `UserDefaults` (no `Sendable`). Solo el booleano se persiste; el refresh token sigue solo en el Keychain (AR5 / ADR-2). |

En `ios/Sources/FutmondoApp/` (app target SwiftUI, aislado con `#if canImport(SwiftUI)`):

| Fichero | Rol |
|---------|-----|
| `AuthViewModel.swift` | `@Observable` (iOS 17+): `state: AuthState` (idle/typing/loading/error/success), `email`, `password`; `submitLogin()` llama `AuthService.login` y limpia `password` tras éxito; `logout()` limpia `password`; NO reintenta (ADR-4) (SEC-A3). |
| `LoginView.swift` | SwiftUI: `.textContentType`, `SecureField` con toggle (`symbolEffect`), botón deshabilitado en idle/loading, banner de error (texto+icono, no solo color), `ShakeEffect` suprimido con Reduce Motion, `.sensoryFeedback`, `@FocusState` Email→Contraseña, `matchedGeometryEffect` del logo. |
| `SplashView.swift` | SwiftUI: estados checking/resumed/offline/no-session; corre `bootstrap()` en `.task`; nunca cuelga; punto de logout provisional (B-08/navegación es F2). |
| `FutmondoApp.swift` | `@main App` que arranca en `SplashView`; cablea `KeychainTokenStore` + `TokenHolder` + `URLSessionNetworkClient` (base URL HTTPS) + `AuthService`. |
| `main.swift` | Entry point no-op SOLO en Linux (`#if !canImport(SwiftUI)`) para que `FutmondoApp` enlace bajo `swift test` en WSL; vacío en Apple (no choca con el `@main`). |

En `ios/Tests/FutmondoKitTests/`:

| Fichero | Rol |
|---------|-----|
| `AuthServiceTests.swift` | XCTest con `SpyNetworkClient` (respuestas por endpoint + conteo de invocaciones) e `InMemoryKeychainStore`/`InMemoryLogoutFlagStore`. 14 tests que **aseveran el efecto**. |

Editados: `ios/Package.swift` (añade el target ejecutable `FutmondoApp` que depende de `FutmondoKit`;
`FutmondoKit` sigue como library y el test target solo depende de `FutmondoKit`), `ios/xtool.yml`
(`product: FutmondoApp`).

## Aislamiento del app target SwiftUI (para que `swift test` compile en Linux)

- La **lógica testeable** (`AuthService`, DTOs, `TokenHolder`, `KeychainStore` + doble in-memory,
  `LogoutFlagStore`) vive en `FutmondoKit`. El `KeychainTokenStore` real va envuelto en
  `#if canImport(Security)` (Security no existe en Linux).
- El **app target `FutmondoApp`** es un target SwiftPM aparte; el **test target depende solo de
  `FutmondoKit`**, así que `swift test` compila `FutmondoKit` + `FutmondoKitTests` y **no** arrastra
  SwiftUI.
- Cada vista/`@main` está envuelta en `#if canImport(SwiftUI) [&& canImport(Observation)]`; en Linux
  compilan a vacío. Como `swift test` enlaza todos los productos, `FutmondoApp/main.swift` aporta un
  entry point no-op **solo** en Linux para que el ejecutable enlace; en Apple ese fichero es vacío y
  el `@main struct FutmondoApp: App` es el entry real.

## Nota de verificación (opción A)

- **NO ejecuté `swift test` como parte entregable del rol**; el toolchain estaba disponible en este
  entorno y lo usé solo como **chequeo de compilación/efecto** mientras construía (28 tests en
  verde: 14 nuevos de `AuthService` + 14 de `NetworkClient` del Bolt 2, sin regresión; incluye el
  test de **coalescing**: 2 refresh concurrentes → **1** sola llamada de red).
- **El propietario debe correr la verificación oficial del bolt** en WSL (Swift 6.4):
  ```bash
  cd ios && swift test        # lógica de AuthService (sin dispositivo)
  cd ios && xtool dev build   # UI + Keychain real + flujo en el iPhone 13 Pro
  ```
- El `KeychainTokenStore` real (`SecItem`), las vistas SwiftUI y el flujo visual se validan en el
  **iPhone 13 Pro** (deuda de arnés de dispositivo, P-1): `swift test` no los cubre.

## Sources

- [consumes] functional-spec.md, entities.md, rules.md (AR1–AR8), frontend-components.md,
  security-design.md (SEC-A1..A6), reliability-design.md (REL-A1..A4), logical-components.md,
  unit-test-instructions.md, code-generation-plan.md, requirements.md (FR-1,2,3,5,6,8; NFR-1,2,3),
  refined-mockups.
- [code] `ios/Sources/FutmondoKit/Networking/` (Bolt 2: `NetworkClient`, `URLSessionNetworkClient`,
  `APIRequest`/`AnyEncodable`/`EmptyResponse`, `NetworkError`, `UserMe`), `ios/Package.swift`.

## Assumptions & Open Questions

- [assumption] El doble in-memory de `KeychainStore` cubre la lógica de `AuthService` en
  `swift test`; el `KeychainTokenStore` real (`SecItem`) se valida en el dispositivo (P-1).
- [assumption] En `bootstrap`, F1 restaura la sesión sin un fetch de perfil (no hay pantallas de
  datos todavía, F2), así que se expone un `UserMe` mínimo derivado del dueño del token; lo que las
  llamadas protegidas necesitan ahora es el access token.
- [assumption] Las conformidades `Sendable` locales a los tipos de Bolt 2 (`EmptyResponse`,
  `UserMe`, `NetworkError`, `URLSessionNetworkClient`) se declaran por extensión en el módulo
  `FutmondoKit` para **no** editar la fuente revisada del Bolt 2 (binding de revisión estable); son
  seguras (campos inmutables / sin estado mutable compartido) bajo la concurrencia estricta de
  Swift 6.
- [assumption] La base URL del `FutmondoApp` es `https://futmondo-api.fly.dev` (producción Fly.io);
  se parametriza si el propietario usa otro entorno.
