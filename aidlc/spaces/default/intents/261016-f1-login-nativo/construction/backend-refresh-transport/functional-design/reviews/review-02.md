## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T14:22:08Z
**Iteration:** 2

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | functional-spec.md > /auth/refresh | Un body opcional mal cableado en FastAPI devuelve 422 ante una petición sin body (la de la PWA por cookie) → regresión real. | Declarar el parámetro de body opcional (`body: Optional[RefreshBodyOptional] = None`) para que sin body no haya 422; test que lo asevera. | Resolved (reviewer) |
| R-02 | Major | functional-spec.md > firmas | La firma de refresh/logout no bastaba para implementar la precedencia header/body sin adivinar. | Especificar firmas con `Cookie`/`Header(alias=X-Refresh-Token)`/body opcional y la resolución `cookie or header or body`. | Resolved (reviewer) |
| R-03 | Major | entities.md | Mapeaba el cambio sobre un `LoginResponse` inexistente; `login()` devuelve un dict crudo. | Corregir: añadir la clave `refresh_token` al dict crudo; documentar `TokenResponse`/`RefreshRequest` existentes y por qué no se reutiliza `RefreshRequest` (obligatorio). | Resolved (reviewer) |
| R-04 | Major | functional-spec.md > test 7 | El test de precedencia no observaba el canal ganador y pasaría trivialmente. | Rediseñar: dos tokens de dos usuarios distintos por cookie/body; aseverar el `sub` del access token devuelto == usuario de la cookie. | Resolved (reviewer) |
| R-05 | Minor | functional-spec.md | Borde cookie-revocada + body-válido sin definir. | Definir precedencia por presencia (gana cookie → 401) y fijarlo con test. | Resolved (reviewer) |

> R-01 Reviewer note: Body opcional `Optional[RefreshBodyOptional] = None`; sin body no hay 422; test 2 lo asevera.

> R-02 Reviewer note: Firmas explícitas Cookie/Header(alias X-Refresh-Token)/body opcional con resolución cookie or header or body.

> R-03 Reviewer note: entities.md reconoce dict crudo de login(); añade solo la clave refresh_token; explica por qué no reutiliza RefreshRequest.

> R-04 Reviewer note: Test 7 observa el canal ganador (sub == usuario de la cookie), no trivial.

> R-05 Reviewer note: Borde cookie-revocada+body-válido definido (precedencia por presencia) y testeado (test 8).

### Summary

Iteración 2 (final) del pase adversarial. Las cinco observaciones de la iteración 1 están resueltas y verificadas contra el código real (`routes.py`/`models.py`/`jwt_utils.py`): el 422 queda descartado con body opcional + test; las firmas de refresh/logout son construibles sin adivinar; entities.md refleja que `login()` devuelve dict crudo y por qué no reutiliza `RefreshRequest`; el test de precedencia observa el canal ganador; el borde cookie-revocada+body-válido está definido y testeado. Cero Critical y cero Major abiertos. Los artefactos describen la firma objetivo (la implementación es trabajo de code-generation). READY.
