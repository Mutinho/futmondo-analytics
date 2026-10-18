## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T14:22:08Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | functional-spec.md > /auth/refresh | Un body opcional mal cableado en FastAPI devuelve 422 ante una petición sin body (la de la PWA por cookie) → regresión real. | Declarar el parámetro de body opcional (`body: Optional[RefreshBodyOptional] = None`) para que sin body no haya 422; test que lo asevera. | New |
| R-02 | Major | functional-spec.md > firmas | La firma de refresh/logout no bastaba para implementar la precedencia header/body sin adivinar. | Especificar firmas con `Cookie`/`Header(alias=X-Refresh-Token)`/body opcional y la resolución `cookie or header or body`. | New |
| R-03 | Major | entities.md | Mapeaba el cambio sobre un `LoginResponse` inexistente; `login()` devuelve un dict crudo. | Corregir: añadir la clave `refresh_token` al dict crudo; documentar `TokenResponse`/`RefreshRequest` existentes y por qué no se reutiliza `RefreshRequest` (obligatorio). | New |
| R-04 | Major | functional-spec.md > test 7 | El test de precedencia no observaba el canal ganador y pasaría trivialmente. | Rediseñar: dos tokens de dos usuarios distintos por cookie/body; aseverar el `sub` del access token devuelto == usuario de la cookie. | New |
| R-05 | Minor | functional-spec.md | Borde cookie-revocada + body-válido sin definir. | Definir precedencia por presencia (gana cookie → 401) y fijarlo con test. | New |

### Summary

Pase adversarial del functional-spec del ajuste de transporte del refresh token. Un fallo Critical (regresión por 422 ante petición cookie-only sin body) y tres Major (firmas insuficientes para la precedencia; `entities.md` sobre un `LoginResponse` inexistente cuando `login()` devuelve dict crudo; test 7 de precedencia trivial) impiden la implementación fiel. Un Minor sobre el borde cookie-revocada+body-válido. NOT-READY: requiere revisión antes de generar código.
