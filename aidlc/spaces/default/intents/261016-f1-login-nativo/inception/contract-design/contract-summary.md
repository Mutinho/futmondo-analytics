# Contract Summary — F1: Login nativo end-to-end

> Fase: inception (contract-design). Contratos de interfaz. Idioma: castellano; tokens técnicos
> (rutas, claves JSON, firmas) verbatim en inglés. Ratifica el contrato de `/auth/*` tras el
> ajuste aditivo D-01 y define los contratos internos del cliente Swift.

## 1. Contrato HTTP de autenticación (backend, tras D-01)

### Precedencia del refresh token (ratificada)
Cuando una petición trae el refresh token por **varios** canales, el backend lo resuelve en este
orden: **(1) cookie `futmondo_refresh_token`** (compat PWA) → **(2) header** → **(3) body**. El
canal cookie de la PWA no cambia; body/header son el fallback para el cliente nativo (ADR-1).

### `POST /auth/login`
- **Request** (sin cambios): `{ "email": string, "password": string }`.
- **Response 200** (aditivo): se añade `refresh_token` al body existente.
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_id": "string",
  "email": "string",
  "display_name": "string",
  "refresh_token": "string"
}
```
- La cookie `HttpOnly` `futmondo_refresh_token` se **sigue** fijando (PWA sin cambios).
- **401**: `{ "detail": "Credenciales incorrectas…" }`.

### `POST /auth/refresh`
- **Request** (aditivo): el refresh token se acepta por **cookie** (actual) **o** por
  **header** `X-Refresh-Token: <token>` **o** por **body** `{ "refresh_token": string }`.
- **Response 200** (sin cambios): `{ "access_token", "token_type", "expires_in" }`.
- **401**: sin token / token inválido / revocado.

### `POST /auth/logout`
- **Request** (aditivo): refresh token por cookie **o** `X-Refresh-Token` **o** body
  `{ "refresh_token": string }`.
- **Response 200**: `{ "success": true, "message": "Sesión cerrada" }`; revoca el token (hash).

### `GET /api/v1/user/me` (sin cambios; llamada de humo)
- **Request**: header `Authorization: Bearer <access_token>`.
- **Response 200**: info del usuario; **401** sin token válido.

## 2. Contratos internos del cliente Swift

### `NetworkClient` (C1)
```
func send<T: Decodable>(_ request: APIRequest) async -> Result<T, NetworkError>
enum NetworkError { case unauthorized, forbidden, server(Int), transport(Error), decoding(Error) }
```
- Inyecta `Authorization: Bearer` cuando hay access token; base URL configurable.
- `APIRequest`: valor con `method`, `path`, `headers`, `body` (Encodable opcional). (Tipo a
  concretar en construcción, pero su forma queda fijada aquí.)

### `KeychainStore` (C2)
```
func saveRefreshToken(_ token: String) throws
func readRefreshToken() -> String?
func deleteRefreshToken() throws
```
- Backed por Keychain Services; nunca escribe en `UserDefaults`/plist.

### `AuthService` (C3)
```
struct Session { let accessToken: AccessToken; let user: UserInfo }
typealias AccessToken = String
enum SessionState { case authenticated(Session); case unauthenticated; case offlinePreserved }
func login(email: String, password: String) async -> Result<Session, AuthError>
func refresh() async -> Result<AccessToken, AuthError>
func bootstrap() async -> SessionState          // auto-login al arrancar
func logout() async                              // revoca + limpia; red caída → pendiente
var pendingLogoutRevocation: Bool { get }        // revocación pendiente observable (red caída)
```
- Dueño del **reintento único** ante 401 (ADR-4). Access token en memoria; refresh token vía C2.
- `pendingLogoutRevocation` se persiste y se reintenta en el siguiente arranque con red; si no se
  completa, el token caduca por TTL (30 días) en backend.

### `AuthViewModel` (C4)
```
enum AuthState { case idle; case typing; case loading; case error(String); case success }
@Observable var state: AuthState
```
- Refleja estado; no reintenta.

## 3. Compatibilidad y no-regresión

- La PWA sigue usando el canal cookie en los tres endpoints (precedencia (1)); su comportamiento
  no cambia (FR-9). Tests `pytest` cubren cookie **y** header/body.

## 4. Guardarraíles de seguridad del contrato

- El `refresh_token` ahora viaja también en el **body JSON** de la respuesta de login y en el
  request de refresh/logout del cliente nativo: **solo sobre TLS/HTTPS**; el refresh token **nunca**
  se registra en logs (ni request/response bodies de login/refresh/logout), coherente con la regla
  durable de credenciales nunca en claro (NFR-1).
- El backend reutiliza `verify_token`/`hash_token`/`revoke_refresh_token` sin cambios de cripto.

## Sources

- [consumes] unit-of-work.md, unit-of-work-dependency.md, components.md, requirements.md.
- [code] `auth/routes.py` (contrato actual), `dependencies.py`, `jwt_utils.py`, `auth.service.ts`.

## Assumptions & Open Questions

- [assumption] El header `X-Refresh-Token` y el orden **header-antes-de-body** son propuestas de
  contrato; **rationale**: el header mantiene el token fuera del cuerpo serializable (menos riesgo
  de quedar en logs de body) y es idiomático para credenciales de transporte, por eso precede al
  body. Ajustable en construcción si surge conflicto, preservando la precedencia **cookie-first** y
  la no-regresión de la PWA.
