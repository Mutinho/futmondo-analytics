# Functional Design — Entities (`backend-refresh-transport`)

> Bolt 1 de F1. Fase: construcción (functional-design). Idioma: castellano; tokens técnicos
> verbatim en inglés. Ajuste aditivo del transporte del refresh token en el backend FastAPI.

## Entidades y estructuras (sin cambios de esquema de BD)

Este bolt **no añade entidades de dominio ni tablas**: reutiliza las existentes. Se documentan
las estructuras de request/response afectadas.

> **Estado real del código (verificado)**: hoy `login()` **devuelve un `dict` crudo** (no usa
> `TokenResponse`), aunque `auth/models.py` ya define `TokenResponse` (con `refresh_token`),
> `RefreshRequest` (con `refresh_token` **obligatorio**) y `RefreshResponse`. El ajuste **no**
> introduce `LoginResponse`.

### Respuesta de `POST /auth/login` (modificada — aditiva, sigue siendo dict crudo)
Se **añade** la clave `refresh_token` al `dict` que ya devuelve `login()` (mismo token que la
cookie). No se migra a un modelo Pydantic para no cambiar el contrato de las demás claves ni
arriesgar regresión; el añadido es una sola clave.

### Body de `POST /auth/refresh` — **nuevo modelo opcional** `RefreshBodyOptional`
`class RefreshBodyOptional(BaseModel): refresh_token: Optional[str] = None`. El **parámetro de
body se declara opcional** (`body: RefreshBodyOptional | None = None`) para que una petición
**sin body** (la de la PWA, que usa cookie) **no produzca 422**. NO se reutiliza el
`RefreshRequest` existente porque su `refresh_token` es **obligatorio** y rompería el canal cookie.

### Body de `POST /auth/logout` — **nuevo modelo opcional** `LogoutBodyOptional`
Igual que arriba: `refresh_token: Optional[str] = None`, parámetro de body opcional.

### Header `X-Refresh-Token`
Parámetro `Header(default=None, alias="X-Refresh-Token")` en refresh y logout.

### Reutilizadas sin cambios
- Tabla `refresh_tokens` (hash + user_id + expires_at) para revocación.
- `app_users` (lookup de email/futmondo_user_id en refresh).
- Funciones de cripto `create_refresh_token`, `verify_token`, `hash_token`,
  `is_refresh_token_valid`, `revoke_refresh_token` — **sin cambios**.

## Sources

- [consumes] contract-summary.md, components.md (C6), requirements.md (FR-4, FR-9).
- [code] `auth/routes.py`, `auth/models.py`, `auth/token_store.py`, `jwt_utils.py`.

## Assumptions & Open Questions

None.
