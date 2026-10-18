# Functional Design — Rules (`backend-refresh-transport`)

> Bolt 1 de F1. Reglas de resolución y comportamiento del transporte del refresh token. Idioma:
> castellano; tokens técnicos verbatim en inglés.

## BR1 — Resolución del refresh token (precedencia)
En `/auth/refresh` y `/auth/logout`, el refresh token se resuelve en este orden y se usa el
**primero presente**:
1. Cookie `futmondo_refresh_token` (canal PWA, sin cambios).
2. Header `X-Refresh-Token`.
3. Body `{ "refresh_token": ... }`.
Si ninguno está presente → `401` (refresh) / comportamiento actual de "sin token" (logout).

## BR2 — Login devuelve el refresh token en el body (aditivo)
`POST /auth/login` sigue fijando la cookie `HttpOnly` **y** además incluye `refresh_token` en el
body de la respuesta. Es el **mismo** token (no se emiten dos).

## BR3 — Reutilización de cripto y revocación
La verificación (`verify_token(expected_type="refresh")`), el hash (`hash_token`), la validez
(`is_refresh_token_valid`) y la revocación (`revoke_refresh_token`) se aplican **igual** sea cual
sea el canal de entrada. No cambia la criptografía ni el formato del token.

## BR4 — No-regresión de la PWA
El comportamiento por cookie de los tres endpoints es idéntico al actual; los tests existentes de
auth deben seguir verdes (characterization-first).

## BR5 — Seguridad del transporte
El refresh token en body/header viaja **solo sobre TLS**; nunca se registra en logs (ni en el
cuerpo de request/response). El `JWT_SECRET` no-default fail-fast se mantiene.

## BR6 — Idempotencia del logout
`logout` revoca el token (por hash) sea cual sea el canal; si no hay token, responde igual que
hoy sin error 500.

## Sources

- [consumes] contract-summary.md (precedencia, guardarraíles), requirements.md (FR-4, FR-9, NFR-1).
- [code] `auth/routes.py`, `jwt_utils.py`, `token_store.py`.

## Assumptions & Open Questions

None.
