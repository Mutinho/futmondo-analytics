# NFR — Security Requirements (`backend-refresh-transport`)

> Bolt 1 de F1. Fase: construcción (nfr-requirements). Idioma: castellano; tokens técnicos
> verbatim en inglés. El eje crítico de este bolt es la seguridad del transporte del refresh token.

## SEC-1 — Transporte solo sobre TLS
El refresh token que ahora viaja en body/header de `/auth/login|refresh|logout` **solo** se
transmite sobre HTTPS/TLS (producción Fly.io ya fuerza HTTPS). No se habilita ningún canal en
claro.
- **Verificación**: no hay cambios que degraden el esquema; el endpoint se sirve tras TLS en
  producción (configuración existente).

## SEC-2 — Nunca registrar el refresh token
Ni el valor del refresh token ni los bodies de login/refresh/logout se escriben en logs
(`logger.*`), ni en mensajes de excepción, ni en `exc_info`.
- **Access logs de infra**: el refresh token **no** viaja en query string ni en la URL (va en
  cookie, header `X-Refresh-Token` o body), de modo que **no** aparece en los access logs de
  uvicorn/nginx (que registran método+ruta, no headers de credencial ni bodies). Prohibido añadir
  logging de headers/bodies de `/auth/*`.
- **Verificación**: revisión de los puntos de log del handler; test que comprueba que un error de
  refresh no incluye el token en el mensaje.

## SEC-3 — Cripto y revocación sin cambios
Se reutiliza `verify_token` (HS256), `hash_token` (sha256) y la revocación por hash; no se altera
el `JWT_SECRET` ni el formato del token. El `JWT_SECRET` no-default fail-fast se mantiene.
- **Verificación**: los tests de cripto/arranque existentes (`test_jwt_startup.py`) siguen verdes.

## SEC-4 — Precedencia determinista, sin ampliar superficie de ataque
La resolución cookie → header → body es por **presencia**; no se aceptan múltiples tokens
combinados ni se amplía CORS para orígenes nuevos. El canal cookie `HttpOnly`/`samesite=lax`
permanece igual.
- **Verificación**: test de precedencia (test 7) y de borde (test 8).

## SEC-5 — No-regresión del modelo de sesión de la PWA
El refresh por cookie no cambia; la PWA no gana ni pierde superficie.
- **Invariante verificable (XSS)**: la PWA **ignora** el `refresh_token` del body de login —
  `auth.service.ts` solo lee `access_token` (en memoria) y el objeto `user`; nunca lee ni
  almacena `refresh_token` del body. Por tanto exponer el refresh en el body **no** amplía la
  superficie XSS de la PWA (su refresh sigue en cookie `HttpOnly`, inaccesible a JS).
- **Verificación**: tests de no-regresión (cookie-only) verdes; inspección de `auth.service.ts`
  confirma que no consume `refresh_token` del body.

## Sources

- [consumes] functional-spec.md, rules.md (BR5), requirements.md (NFR-1), contract-summary.md,
  technology-stack.md.
- [memory] credenciales/tokens nunca en claro; `JWT_SECRET` no-default.

## Assumptions & Open Questions

None.
