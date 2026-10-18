## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T14:05:14Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | contract-summary.md > NetworkClient | El enum `NetworkError` difería entre contract-summary y components.md. | Alinear el enum entre artefactos. | New |
| R-02 | Minor | contract-summary.md > Assumptions | El orden header-antes-de-body se declaraba ratificado en §1 pero "propuesta" sin rationale en Assumptions. | Añadir rationale del orden header→body. | New |
| R-03 | Minor | contract-summary.md > AuthService | La "revocación pendiente" (`pendingLogoutRevocation`) de domain-design no aparecía en el contrato de C3. | Exponerla en la firma de C3. | New |
| R-04 | Minor | contract-summary.md > contratos Swift | Tipos `Session`/`AccessToken`/`SessionState`/`AuthState`/`APIRequest` sin pinar. | Pinar/definir la forma de los tipos. | New |
| R-05 | Minor | contract-summary.md > seguridad | El refresh token ahora viaja en el body JSON de login; faltaba guardarraíl de TLS + no-logging. | Anotar TLS obligatorio y no-logging del body. | New |

### Summary

El contrato de auth tras D-01 es sólido, aditivo y sin regresión: `login` añade `refresh_token` al body y sigue fijando la cookie `HttpOnly`; `refresh`/`logout` aceptan cookie O header O body (precedencia cookie-first). Los contratos internos Swift mapean a los componentes del domain-design con `AuthService` como único dueño del reintento único (ADR-4) y `AuthViewModel` que solo refleja estado. No se exponen credenciales en claro y se reutiliza la cripto existente. Cero findings Critical/Major; los cinco Minor (alineación de enum, rationale de precedencia, exponer revocación pendiente, pinar tipos, guardarraíl TLS/no-logging) ya se incorporaron. No bloquea.
