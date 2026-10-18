# Functional Design — Rules (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés.

## AR1 — Login
`login`: `POST /auth/login` con email/password → si 200, guarda access token en memoria y refresh
token en Keychain (vía `KeychainStore`); devuelve `Session`. Si 401 → `.invalidCredentials`; otro
error de red → `.network(e)`.

## AR2 — Access token en memoria, refresh en Keychain
El access token **nunca** se persiste (solo memoria del `AuthService`); el refresh token **solo**
en Keychain, nunca en `UserDefaults`/plist (FR-2, FR-3, NFR-1).

## AR3 — Bootstrap (auto-login)
`bootstrap`: si hay refresh token en Keychain, intenta `refresh`:
- 200 → access token en memoria → `.authenticated`.
- 401/revocado → borra Keychain → `.unauthenticated`.
- red/5xx → **preserva** Keychain → `.offlinePreserved` (no cuelga; reintenta luego).
Sin token en Keychain → `.unauthenticated`.

## AR4 — Refresh ante 401 (reintento único + coalescing, ADR-4)
Ante un 401 en una llamada protegida, `AuthService` refresca (refresh token del Keychain por
header/body, D-01) y reintenta la petición **exactamente una vez**. Si el reintento vuelve a 401 o
el refresh falla por 401/revocación → fuerza re-login (sin bucle). `.cancelled` del cliente no
cuenta como fallo de red.
- **Coalescing**: si varias peticiones reciben 401 a la vez (access token caducado), **todas
  comparten una única operación de refresh en vuelo** (`refreshInFlight: Task`), para no disparar
  N refresh en paralelo ni rotar el refresh token varias veces. Las que esperaban usan el mismo
  resultado; si el refresh falla, todas resuelven a re-login.

## AR5 — Logout
`logout`: `POST /auth/logout` (revoca; refresh token por header/body) → borra Keychain + limpia el
access token en memoria **en AMBAS ubicaciones**: `AuthService.accessToken` **y** el `TokenHolder`
snapshot que lee el provider (SEC-A2). Red caída → limpia estado local y marca
`pendingLogoutRevocation = true`.
- **El flag NO duplica el refresh token en claro**: `pendingLogoutRevocation` es un **booleano**
  persistido (p. ej. `UserDefaults`, solo el flag). El refresh token sigue **solo en el Keychain**
  hasta que se revoque; en el siguiente arranque con red se reintenta `logout` leyéndolo del
  Keychain; si no se completa, caduca por TTL (30 días) en backend. Nunca se copia el token fuera
  del Keychain (AR2/ADR-2).

## AR8 — Concurrencia (aislamiento del estado de sesión)
`AuthService` es un **`actor`**: el access token en memoria y la orquestación del refresh están
aislados, sin carrera de datos. El `accessTokenProvider` síncrono del `NetworkClient` lee un
**snapshot Sendable** (holder con lock) que el actor actualiza al cambiar el token; el provider no
entra al actor en línea. Invariante del `[weak self]`: si `self == nil`, el provider devuelve
`nil` y el cliente no inyecta `Bearer` (no se usa `[unowned self]`).

## AR6 — UI y accesibilidad
`LoginView`/`SplashView` según refined-mockups: estados idle/typing/loading/error/success;
animaciones nativas que respetan Reduce Motion; autorrelleno de contraseña (`.textContentType`);
feedback háptico; `@FocusState` Email→Contraseña. `AuthViewModel` refleja estado, no reintenta.
- **Borrado del password del formulario**: tras un login exitoso y en logout, `AuthViewModel`
  limpia `password = ""`, para que el string del `SecureField` no persista en memoria del
  ViewModel mientras la vista vive (SEC-A3).

## AR7 — Solo SDK de Apple
`Security` (Keychain), `SwiftUI`, `Foundation`, el `FutmondoKit.NetworkClient` del Bolt 2. Cero
librerías de terceros (NFR-2/P-3). `LocalAuthentication`/Face ID queda **fuera de F1** (diferido).

## Sources
- [consumes] contract-summary.md, components.md (C2-C5), requirements.md, refined-mockups
  (mockups/interaction-spec/accessibility-checklist).

## Assumptions & Open Questions
None.
