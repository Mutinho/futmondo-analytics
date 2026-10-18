# Functional Design — Entities (`ios-native-auth`)

> Bolt 3 de F1. Fase: construcción (functional-design). Idioma: castellano; identificadores/código
> en inglés. Auth nativa: Keychain + AuthService + ViewModel + Login/SplashView.

## Tipos y componentes (Swift)

### `KeychainStore` (protocolo + impl `KeychainTokenStore`)
Fachada sobre **Keychain Services** (`Security`). Métodos:
`saveRefreshToken(_:) throws`, `readRefreshToken() -> String?`, `deleteRefreshToken() throws`.
Protocolo para poder doblarlo en tests (impl real usa `SecItem*`).

### `Session` / `AuthState`
- `struct Session { let accessToken: String; let user: UserMe }` (access token en memoria).
- `enum AuthState: Equatable { case idle, typing, loading, error(String), success }` (UI).
- `enum SessionState { case authenticated(Session), unauthenticated, offlinePreserved }`
  (resultado de `bootstrap`).

### `AuthError` (enum, Equatable)
`.invalidCredentials` (401 login), `.network(NetworkError)`, `.refreshFailed`, `.unknown(String)`.

### `AuthService` (protocolo + impl)
`login(email,password) async -> Result<Session, AuthError>`, `refresh() async -> Result<String,
AuthError>`, `bootstrap() async -> SessionState`, `logout() async`,
`var pendingLogoutRevocation: Bool`. Mantiene el access token en memoria; refresh token vía
`KeychainStore`. Dueño del reintento único ante 401 (ADR-4).

### `AuthViewModel` (`@Observable` / `ObservableObject`)
Expone `state: AuthState`, `email`, `password`; acciones `submitLogin()`, `logout()`. No reintenta
(delega en `AuthService`).

### DTOs de auth (Codable)
- `LoginRequestDTO { email, password }`.
- `LoginResponseDTO { access_token, refresh_token, token_type, expires_in, user_id, email, display_name? }`
  (incluye `refresh_token`, por el ajuste D-01 del backend).
- `RefreshRequestDTO { refresh_token }`, `RefreshResponseDTO { access_token, expires_in }`.

## Sources
- [consumes] components.md (C2-C5), contract-summary.md (contratos Swift y HTTP), requirements.md
  (FR-1,2,3,5,6,8), unit-of-work.md.

## Assumptions & Open Questions
None.
