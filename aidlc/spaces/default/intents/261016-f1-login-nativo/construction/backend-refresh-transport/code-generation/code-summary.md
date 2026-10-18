# Code Summary — `backend-refresh-transport` (Bolt 1 de F1)

> Fase: construcción (code-generation). Resumen de la implementación del ajuste aditivo del
> transporte del refresh token. Idioma: castellano; identificadores/tokens técnicos en inglés.

## Qué se construyó

Ajuste **aditivo** del transporte del refresh token en el backend FastAPI para que un cliente
nativo (app iOS, sin cookies de navegador) complete `login → refresh → logout` por **header**
`X-Refresh-Token` o por **body** `{refresh_token}`, **sin romper** el canal cookie `HttpOnly` de la
PWA Angular. El cambio es acotado: sólo `auth/routes.py` + `auth/models.py` (modelos de body
opcionales). No se tocó la cripto, ni el patrón SQL-en-router, ni se ampliaron god-files.

## Ficheros tocados / creados

| Fichero | Acción | Detalle |
|---------|--------|---------|
| `backend/app/auth/models.py` | Modificado (aditivo) | Añadidos `RefreshBodyOptional` y `LogoutBodyOptional` (`refresh_token: Optional[str] = None`). `RefreshRequest` intacto. |
| `backend/app/auth/routes.py` | Modificado (aditivo) | Import de `Header` y de los dos modelos; `resolve_refresh_token(cookie, header, body_token)` a nivel de módulo; `login` añade `refresh_token` al dict (sigue fijando la cookie); `refresh`/`logout` aceptan header + body opcional y resuelven el token por precedencia cookie → header → body. |
| `backend/tests/test_auth_refresh_transport.py` | Creado | 8 tests pytest (TestClient, fakes in-memory, cripto real + `JWT_SECRET` efímero). |
| `.../code-generation/code-generation-plan.md` | Marcado | Checkboxes de pasos a hechos (único cambio a ese fichero). |

## Enfoque

- **Precedencia por presencia** (BR1): `cookie or header or body_token`. Un cliente nativo no envía
  cookie, así que cae al header/body; la PWA sólo envía cookie. El borde cookie-revocada +
  body-válido devuelve 401 (gana la cookie por presencia; el body no se acepta).
- **Body opcional** (`Optional[RefreshBodyOptional/LogoutBodyOptional] = None`): una petición sin
  body (PWA) **no** produce 422 — cierra el Critical del review.
- **No-regresión del canal PWA**: `login` sigue fijando la cookie `HttpOnly` y `logout` sigue
  borrándola; sólo se **añade** `refresh_token` al body de `login`.
- **Seguridad**: no se loguea el token ni los bodies; la revocación es por hash (BR3/BR6); la cripto
  (`jwt_utils`) no cambia. En tests, tokens generados con la cripto real sobre un `JWT_SECRET`
  efímero no productivo (gitleaks escanea los tests).

## Resultado real de tests

Entorno: venv efímero (`backend/.venv-ephemeral`, Python 3.14 del sistema), `requirements.txt`
completo instalado (no había `libsql-experimental` que excluir), `JWT_SECRET` efímero.

- **Nuevos tests del transporte** (`tests/test_auth_refresh_transport.py`): **8 passed** en 0.26 s.
- **Suite completa** (no-regresión, `pytest -q --cov=app`): **422 passed, 3 xfailed** en 8.28 s.
  Cobertura total **58.30 %** — supera el piso heredado bloqueante **27 %** (`--cov-fail-under=27`
  en `pytest.ini`). El piso no se tocó (el ratchet sólo sube).
- **Lint**: `ruff check app/auth/models.py app/auth/routes.py tests/test_auth_refresh_transport.py`
  → *All checks passed!* (sin `ruff format` ni `--fix` masivo; edición quirúrgica).

Los 8 casos cubiertos (aseveran el efecto): (1) `login` → `refresh_token` en body + `Set-Cookie`;
(2) `refresh` por cookie sin body → 200 y **no** 422; (3) por header → 200; (4) por body → 200;
(5) sin token → 401; (6) `logout` por header y por body revocan → `refresh` posterior 401;
(7) precedencia observable (cookie=U_cookie + body=U_body → `access.sub == U_cookie`); (8) cookie
revocada + body válido → 401.

## Bloqueos

Ninguno. Implementación, tests nuevos y suite completa verificados localmente.

## Sources

- [consumes] `../functional-design/functional-spec.md`, `code-generation-plan.md`,
  `unit-test-instructions.md`, `requirements.md` (FR-4, FR-9, NFR-1, NFR-3).
- [code] `backend/app/auth/routes.py`, `backend/app/auth/models.py`, `backend/app/auth/jwt_utils.py`,
  `backend/app/auth/token_store.py`, `backend/conftest.py`,
  `backend/tests/test_auth_characterization.py`, `backend/pytest.ini`,
  `backend/app/core/config.py`, `backend/app/auth/session_store.py`,
  `backend/app/services/session_service.py`.

## Assumptions & Open Questions

None.
