# Reverse Engineering — Confirmación (F1: Login nativo end-to-end)

> Idioma: castellano; tokens técnicos verbatim en inglés. Esta etapa produjo la base de
> conocimiento del código (codekb) del repositorio, enfocada en servir a F1.

## Consolidated Summary Confirmation

El reverse-engineering generó 9 documentos de codekb en
`aidlc/spaces/default/codekb/futmondo-analytics/` (business-overview, architecture,
code-structure, api-documentation, component-inventory, technology-stack, dependencies,
code-quality-assessment, reverse-engineering-timestamp). Hallazgos clave para F1:

- **Auth**: JWT `HS256` (PyJWT). Access token (1h) en el body de `/auth/login` y en memoria en el
  cliente; refresh token (30d) con hash persistido para revocación.
- **Contrato actual (D-01)**: el refresh token viaja **sólo por cookie `HttpOnly`**
  (`futmondo_refresh_token`); `/auth/refresh` lo lee sólo por cookie. F1 añade transporte por
  body/header (aditivo), reutilizando firma/validación/revocación sin cambios de cripto.
- **Protección de `/api/v1/*`**: `AuthMiddleware` (Starlette) + `get_current_user` exigen
  `Authorization: Bearer`; exentos login/refresh/logout, `/health`, `/`, docs.
- **Referencias frontend**: `auth.service.ts`, `auth.interceptor.ts` (Bearer + refresh ante 401,
  logout ante 403), `login.component.ts`.
- **Seguridad/calidad**: password Futmondo nunca en memoria; `JWT_SECRET` no-default en arranque;
  gate de CI bloqueante; god-files (`data_manager_v2.py`, `data_sync_service.py`) como deuda
  conocida (no ampliar).

¿Está todo correcto?

[Answer]: Looks correct
