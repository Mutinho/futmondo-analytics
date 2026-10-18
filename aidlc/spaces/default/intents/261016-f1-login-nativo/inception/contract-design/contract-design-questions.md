# Contract Design — Preguntas (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés.

## Q1 — ¿El contrato de auth (tras D-01) y los contratos internos del cliente son correctos?

- A. **Correctos** — proceder a delivery planning (recomendado).
- B. Correctos con un ajuste (especifícalo: p. ej. nombre del header, precedencia).
- C. Replantear (especifícalo).
- X. Other (please specify)

[Answer]: A

## Assumptions & Open Questions

None.

## Consolidated Summary Confirmation

Antes de cerrar contract-design, confirma:

- **Precedencia del refresh token**: cookie → header `X-Refresh-Token` → body `refresh_token`
  (cookie-first = compat PWA; body/header = fallback nativo).
- **`/auth/login`**: añade `refresh_token` al body de la respuesta (la cookie sigue fijándose).
- **`/auth/refresh` y `/auth/logout`**: aceptan el refresh token por cookie o header o body.
- **`GET /api/v1/user/me`**: `Authorization: Bearer` (llamada de humo).
- **Contratos Swift**: `NetworkClient.send` (Result + errores tipados), `KeychainStore`
  (save/read/delete), `AuthService` (login/refresh/bootstrap/logout, dueño del reintento único),
  `AuthViewModel` (estado, no reintenta).
- **No-regresión**: la PWA usa el canal cookie sin cambios; tests `pytest` de ambos canales.

¿Está todo correcto?

[Answer]: Looks correct
