# Functional Design — Confirmación (`backend-refresh-transport`, Bolt 1 de F1)

> Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Functional design del Bolt 1 (ajuste aditivo del transporte del refresh token). Resumen:

- **Login**: añade la clave `refresh_token` al dict crudo que ya devuelve `login()`; la cookie
  `HttpOnly` se sigue fijando (sin regresión PWA).
- **Refresh/Logout**: aceptan el refresh token por cookie → header `X-Refresh-Token` → body
  (precedencia cookie-first); body **opcional** (`Optional[...] = None`) para que una petición sin
  body **no dé 422**. Cripto y revocación reutilizadas sin cambios.
- **Tests pytest** (8): devolución en body + cookie; refresh por cookie-sin-body (no 422); por
  header; por body; sin token → 401; logout por header y por body revoca; precedencia observable
  (sub del access token == usuario de la cookie); borde cookie-revocada+body-válido → 401.
- **Revisión adversarial**: iteración 1 NOT-READY (1 Critical del 422 + 3 Major), iteración 2
  READY tras incorporar todos los findings.
- Sin ampliar god-files; solo `auth/routes.py` + modelos de body opcionales en `auth/models.py`.

¿Está todo correcto?

[Answer]: 
