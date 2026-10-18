## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T18:19:04Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | security-design.md > TokenHolder | `OSAllocatedUnfairLock` es iOS 16+/macOS 13 y no existe en el Swift de Linux; `TokenHolder` vive en `FutmondoKit` y debe compilar bajo `swift test` en WSL → rompería el build de tests. | Usar `NSLock` (portable a Linux/Darwin). | New |
| R-02 | Minor | security-design.md > logout | Orden de borrado actor-vs-holder frente a petición en vuelo no precisado. | Borrar primero el holder, luego el actor. | New |

### Summary

Pase adversarial del security-design de la auth. SEC-A1 (KeychainTokenStore con `AfterFirstUnlockThisDeviceOnly`, upsert con `OSStatus`), SEC-A3 (password del formulario borrado), SEC-A5 (transporte vía NetworkClient) y SEC-A6 (Face ID diferido) son correctos y consistentes con REL-A4. Un fallo material: `TokenHolder` con `OSAllocatedUnfairLock` no compila en el Swift de Linux donde corre `swift test`, rompiendo la verificación acordada del bolt. Un Minor sobre el orden de borrado. NOT-READY: cambiar a `NSLock`.
