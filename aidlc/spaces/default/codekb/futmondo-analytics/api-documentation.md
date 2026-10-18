# API Documentation — Futmondo Analytics

Backend FastAPI (`title="Futmondo API"`, `version="2.0.0"`). Dos espacios de
rutas: `/auth/*` (sin prefijo `/api/v1`) y `/api/v1/*`. La protección se aplica
en `AuthMiddleware` (`main.py`): toda ruta bajo `/api/v1` exige
`Authorization: Bearer <access_token>` salvo las de `AUTH_EXCLUDED_PATHS`.

## Autenticación — contrato real (clave para F1)

### `POST /auth/login`

- **Body** (`LoginRequest`, pydantic): `{ "email": str, "password": str }` — son
  las credenciales de **Futmondo** del usuario.
- **Comportamiento**: valida contra la API de Futmondo (`FutmondoClient.login()`).
  Si falla → `401` con `detail` en castellano
  (`"Credenciales incorrectas..."`). Si acierta: upsert de `app_users`, emite
  access + refresh token, cachea la sesión Futmondo, persiste sesión durable
  (best-effort) y auto-detecta campeonatos.
- **Respuesta (200, JSON)**:
  ```json
  {
    "access_token": "<JWT access>",
    "token_type": "bearer",
    "expires_in": 3600,
    "user_id": "<hex>",
    "email": "<email>",
    "display_name": "<local-part del email>"
  }
  ```
- **Side-effect de transporte**: además fija la cookie `HttpOnly`
  `futmondo_refresh_token` (`_set_refresh_cookie`): `httponly=True`,
  `secure=COOKIE_SECURE` (default `true`), `samesite="lax"`,
  `max_age=2592000` (30 días), `path="/auth"`. El refresh token **NO** aparece en
  el body JSON: hoy viaja **solo** por esta cookie.

### `POST /auth/refresh`

- **Entrada**: cookie `futmondo_refresh_token` (parámetro `Cookie(...)`). **No**
  acepta hoy el refresh token por body ni por header.
- **Comportamiento**: sin cookie → `401` (`"No refresh token"`). Verifica firma
  (`verify_token(expected_type="refresh")`), comprueba no-revocado/no-expirado
  por hash en `refresh_tokens` (`is_refresh_token_valid`), relee email/uid del
  usuario y emite un nuevo access token. Dispara rehidratación de sesión durable
  best-effort.
- **Respuesta (200, JSON)**:
  `{ "access_token": "<JWT>", "token_type": "bearer", "expires_in": 3600 }`.

### `POST /auth/logout`

- **Entrada**: cookie `futmondo_refresh_token` (opcional).
- **Comportamiento**: revoca el refresh token (`revoke_refresh_token` por hash),
  elimina la sesión Futmondo en memoria, purga la sesión durable y el handle
  cifrado, y limpia la cookie (`_clear_refresh_cookie`).
- **Respuesta (200)**: `{ "success": true, "message": "Sesión cerrada" }`.

### Implicación D-01 para F1

Un cliente nativo iOS no tiene almacén de cookies de navegador ni participa del
mismo origen CORS. El contrato actual entrega el refresh token **solo** por
cookie `HttpOnly`, por lo que F1 requiere un **ajuste aditivo del backend** para
transportar el refresh token también fuera de la cookie (p. ej. en el body de
`/auth/login` y aceptarlo en el body/header de `/auth/refresh`), preservando el
camino cookie existente para el navegador. El refresh token en iOS debe guardarse
en **Keychain** (nunca en claro). La verificación/firma/revocación
(`jwt_utils.py`, `refresh_tokens`) se reutiliza sin cambios.

## Protección de `/api/v1/*`

`AuthMiddleware.dispatch` (`main.py`):
- Rutas que no empiezan por `/api/v1` ni `/auth` → pasan sin auth.
- `AUTH_EXCLUDED_PATHS` = `/auth/login`, `/auth/refresh`, `/auth/logout`,
  `/health`, `/`, `/docs`, `/openapi.json`, `/redoc` → sin auth.
- Resto de `/api/v1/*`: exige `Authorization: Bearer`; sin header → `401`
  `{"detail": "Not authenticated"}`; token inválido/expirado → `401`
  `{"detail": "Token expired or invalid"}`. Al validar, adjunta
  `request.state.user = { user_id, email, futmondo_uid }`.

La dependencia `get_current_user` (`dependencies.py`) implementa la misma
validación para endpoints que la declaran explícitamente.

### `GET /api/v1/user/me`

- Requiere Bearer. Lee `request.state.user` (puesto por el middleware); si falta
  → `401`. Devuelve el usuario desde `app_users`:
  ```json
  {
    "success": true,
    "user": { "id", "email", "futmondo_user_id", "display_name",
              "created_at", "last_login" }
  }
  ```
- Si el usuario no existe en DB → `404`.

### Otros endpoints `/api/v1/*` (resumen, todos protegidos por Bearer)

| Prefijo (router) | Ejemplos | Propósito |
|---|---|---|
| `/api/v1/user` | `/me`, `/championships` | Usuario y config de campeonatos |
| `/api/v1/analytics` | `/balances` (balances router) | Presupuestos y analítica |
| `/api/v1/market` | `/today`, `/bid` | Mercado y puja |
| `/api/v1/sync` | `/trigger`, `/task/{id}`, phantoms, sofascore | Sync async durable |
| `/api/v1/player-finances` | `/` | Finanzas por usuario |
| `/api/v1/roster`, `/transactions`, `/favorites` | — | Plantilla, movimientos, favoritos |
| `/api/v1/clausulable-players`, `/statistics`, `/user-stats` | — | Clausulables y estadísticas |
| `/api/v1/matchdays`, `/initialize`, `/database` (reset_db) | — | Jornadas, init, admin DB |
| `/api/v1/assistant` | — | Asistente AI (Gemini/Groq) |
| `/api/v1/photos/{player_id}` | — | Foto de jugador (protegida; redirige 302 al mount público `/static/photos/*`) |

### Rutas públicas de servicio

- `GET /` → metadata del servicio. `GET /health` → `{"status":"healthy"}` (usado
  por el smoke test de `fly-deploy.yml`). `/static/photos/*` → mount estático
  **público intencional** de imágenes no sensibles (fuera de `/api/v1` y `/auth`).

## Sources

- `backend/app/main.py` (AuthMiddleware, routers, `/health`, `/`, fotos)
- `backend/app/auth/routes.py` (login/refresh/logout, cookie)
- `backend/app/auth/jwt_utils.py` (ACCESS_TOKEN_EXPIRE_MINUTES=60)
- `backend/app/auth/dependencies.py`
- `backend/app/api/v1/endpoints/user.py`

## Assumptions & Open Questions

- Los contratos de request/response detallados de cada endpoint de datos (más
  allá de auth y `/user/me`) no se transcriben campo a campo; se enumeran por
  prefijo/propósito a partir de `main.py` y los nombres de fichero. F1 solo
  necesita el contrato de auth y `/user/me`, que sí están verificados leyendo el
  código.
