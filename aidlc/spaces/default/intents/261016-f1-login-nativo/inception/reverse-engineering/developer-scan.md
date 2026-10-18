# Developer Scan — Reverse Engineering (F1: Login nativo end-to-end)

**Collaborator:** aidlc-developer-agent

> Handoff del link del pipeline de reverse-engineering. Resume el escaneo del repositorio y los
> hallazgos relevantes para F1. Idioma: castellano; tokens técnicos verbatim en inglés.

## Qué se produjo

9 documentos de codekb en `aidlc/spaces/default/codekb/futmondo-analytics/`:
`business-overview.md`, `architecture.md` (mermaid + fallback), `code-structure.md`,
`api-documentation.md`, `component-inventory.md`, `technology-stack.md`, `dependencies.md`,
`code-quality-assessment.md`, `reverse-engineering-timestamp.md`. Cada uno con `## Sources` y
`## Assumptions & Open Questions`, sin credenciales/tokens reales.

## Hallazgos clave para F1

1. **Auth**: JWT `HS256` (PyJWT). Access token (1h) en el body de `/auth/login`, guardado en
   memoria en el cliente. Refresh token (30d) con hash persistido para revocación.
2. **Contrato actual (D-01)**: el refresh token viaja **sólo por cookie `HttpOnly`**
   (`futmondo_refresh_token`, secure, samesite=lax, path=/auth); `/auth/refresh` lo lee sólo por
   cookie. F1 añade transporte por body/header (aditivo), reutilizando firma/validación/
   revocación sin cambios de cripto.
3. **Protección de `/api/v1/*`**: `AuthMiddleware` (Starlette) + `get_current_user`
   (`dependencies.py`) exigen `Authorization: Bearer` con `verify_token(expected_type="access")`;
   exentos `/auth/login|refresh|logout`, `/health`, `/`, `/docs`, `/openapi.json`, `/redoc`.
4. **Referencias frontend**: `auth.service.ts` (login/refresh/logout/tryRecoverSession, access en
   memoria), `auth.interceptor.ts` (Bearer + reintento con refresh en 401, logout en 403),
   `login.component.ts`.
5. **Seguridad**: password Futmondo nunca en memoria; handle de re-auth cifrado
   (`FUTMONDO_CRED_KEY`); `JWT_SECRET` no-default fail-fast en arranque; gate de CI bloqueante
   (gitleaks + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit`); pisos de
   cobertura heredados que el ratchet sólo sube.
6. **God-files como deuda conocida (no ampliar)**: `data_manager_v2.py`, `data_sync_service.py`.

## Sources

- Repositorio `/home/javi/futmondo-analytics` (backend/ y angular-app/), ficheros citados en
  cada documento de codekb.

## Assumptions & Open Questions

None.
