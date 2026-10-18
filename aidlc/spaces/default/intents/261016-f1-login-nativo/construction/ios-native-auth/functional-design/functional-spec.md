# Functional Spec — `ios-native-auth` (Bolt 3 de F1)

> Fase: construcción (functional-design). Auth nativa completa. Idioma: castellano;
> identificadores/código en inglés.

## Objetivo

Completar el login nativo end-to-end: pantalla de Login + Splash de auto-login, con el access
token en memoria y el refresh token en iOS Keychain, usando el `NetworkClient` del Bolt 2 y el
transporte aditivo del backend (Bolt 1). Cierra F1.

## Componentes

### `KeychainStore` (C2)
```swift
protocol KeychainStore {
    func saveRefreshToken(_ token: String) throws
    func readRefreshToken() -> String?
    func deleteRefreshToken() throws
}
final class KeychainTokenStore: KeychainStore { /* SecItemAdd/Copy/Delete, service+account */ }
```
Testeable: `AuthService` depende del protocolo; en tests se usa un doble in-memory.

### `AuthService` (C3) — dueño de la sesión y del reintento único
`AuthService` es un **`actor`** (aislamiento de concurrencia): protege el estado mutable
(`accessToken` en memoria y la orquestación del refresh) frente a las múltiples peticiones async
que lo leen/mutan, eliminando la carrera de datos.
```swift
actor AuthService {
    private var accessToken: String?
    private var refreshInFlight: Task<String, Error>?   // coalescing del refresh (AR4)
    func login(email: String, password: String) async -> Result<Session, AuthError>
    func refresh() async -> Result<String, AuthError>        // nuevo access token (coalescido)
    func bootstrap() async -> SessionState
    func logout() async
    func currentAccessToken() -> String?                      // lectura aislada para el snapshot del provider
    var pendingLogoutRevocation: Bool { get }
}
```
- **Provider del NetworkClient sin romper el aislamiento**: el `NetworkClient` recibe un
  `accessTokenProvider: () -> String?` **síncrono**, así que no puede entrar al actor en línea. Se
  resuelve con un **snapshot Sendable**: un pequeño `TokenHolder` (clase con lock / `OSAllocatedUnfairLock`
  o `nonisolated(unsafe)` atómico) que `AuthService` **actualiza** cada vez que cambia el access
  token (login/refresh/logout), y que el provider lee sin tocar el actor. El token nunca se retiene
  en el closure; el provider lee el holder.
- **`login`**: AR1. **`bootstrap`**: AR3. **`refresh`**: envía el refresh token (Keychain) por
  header `X-Refresh-Token`/body (D-01). **`logout`**: AR5.
- **Reintento único + coalescing (AR4)**: ante un 401, se solicita el refresh a través de
  `refreshInFlight`: si ya hay una `Task` de refresh en vuelo, **todas las peticiones esperan la
  misma** (una sola rotación del refresh token); si no, se crea. Tras resolverse (éxito o fallo) se
  limpia `refreshInFlight`. Cada petición reintenta **una vez** con el nuevo access token; si el
  refresh falló por 401/revocación, re-login. Nunca N refresh en paralelo.

### `AuthViewModel` (C4) y vistas (C5)
`AuthViewModel` expone `state`, `email`, `password`, `submitLogin()`, `logout()`; refleja el
resultado de `AuthService` sin reintentar. `LoginView`/`SplashView` en SwiftUI según
refined-mockups (estados, animaciones con Reduce Motion, autorrelleno, haptics).

## Flujos (resumen; detalle en rules AR1–AR6)

- Login manual → 200 → access en memoria + refresh en Keychain → autenticado.
- Arranque → refresh token en Keychain → `bootstrap` → auto-login / offline-preserved / login.
- 401 en llamada protegida → refresh → reintento único → re-login si falla.
- Logout → revoca + borra Keychain + limpia memoria (pendiente si red caída).

## Verificación (opción A: swift test real + validación manual en iPhone)

- **`swift test`** (ejecutable por el propietario en WSL, como el Bolt 2) cubre la **lógica
  testeable sin dispositivo**: `AuthService` con dobles de `NetworkClient` y `KeychainStore`
  in-memory — login OK/401, bootstrap (3 ramas), refresh+reintento único, logout +
  pendingLogoutRevocation. Son los casos que aseveran el efecto.
- **Validación manual en el iPhone 13 Pro** (xtool): el **Keychain real**, la **UI** y el flujo
  visual (login → auto-login → logout). Es la parte que `swift test` no cubre (necesita
  dispositivo). Documentada en unit-test-instructions; `KeychainTokenStore` real se ejercita ahí.

## Alcance y límites

- Sin pantallas de datos (F2). Sin navegación/tab bar (B-08, F2). Sin Face ID (diferido). Solo SDK
  de Apple. Reutiliza `FutmondoKit` (Bolt 2) y el backend (Bolt 1).

## Sources
- [consumes] contract-summary.md, components.md (C2-C5), requirements.md (FR-1,2,3,5,6,8; NFR-1,2,3),
  rules.md, entities.md, refined-mockups.

## Assumptions & Open Questions
- [assumption] El doble in-memory de `KeychainStore` en tests cubre la lógica de `AuthService`; el
  `KeychainTokenStore` real (SecItem) se valida en el dispositivo (no en `swift test`), por ser
  API de plataforma. Es coherente con P-1 (deuda de arnés de dispositivo).
