## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T18:02:43Z
**Iteration:** 2

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | functional-spec.md > AuthService | Estado mutable compartido (`accessToken` + orquestación) leído por el provider async sin aislamiento → carrera de datos. | Declarar `AuthService` como `actor`; provider lee un snapshot Sendable (holder con lock). | Resolved (reviewer) |
| R-02 | Critical | rules.md > AR4 | El refresh ante 401 concurrente no coalesce → N refresh en paralelo, rotación múltiple y posible revocación de la sesión renovada. | Coalescing: una única `Task` de refresh en vuelo compartida. | Resolved (reviewer) |
| R-03 | Major | AR5 / contract-summary | `pendingLogoutRevocation` "se persiste" sin decir dónde; riesgo de duplicar el refresh token fuera del Keychain. | Flag booleano (UserDefaults); token solo en Keychain hasta revocar/TTL. | Resolved (reviewer) |
| R-04 | Minor | decisions.md ADR-4 | Atribuía el reintento a "AuthViewModel/AuthService", contradiciendo el dueño único. | Alinear: AuthService único dueño; ViewModel no reintenta. | Resolved (reviewer) |
| R-05 | Minor | functional-spec `[weak self]` | Documentar invariante self==nil → provider nil, no `[unowned self]`. | Añadir invariante. | Resolved (reviewer) |

> R-01 Reviewer note: `AuthService` es `actor`; provider lee snapshot Sendable (holder con lock). Carrera eliminada.

> R-02 Reviewer note: Refresh coalescido (`refreshInFlight`, una Task compartida); sin tormenta/revocación.

> R-03 Reviewer note: `pendingLogoutRevocation` booleano persistido; refresh token solo en Keychain hasta revocar/TTL.

> R-04 Reviewer note: ADR-4 alineado: AuthService dueño único; ViewModel no reintenta.

> R-05 Reviewer note: Invariante `[weak self]` documentada.

### Summary

Iteración 2 (final). Los dos Critical están resueltos: `AuthService` es un `actor` y el provider síncrono del `NetworkClient` lee un snapshot Sendable (holder con lock) actualizado por el actor, sin carrera sobre el access token; el refresh ante 401 concurrente coalesce en una única `Task` en vuelo compartida (una sola rotación del refresh token). El Major (dónde vive `pendingLogoutRevocation` = booleano persistido, token solo en Keychain) y los Minor (ADR-3/ADR-4 alineados, invariante `[weak self]`) también cerrados. Cero Critical/Major abiertos. READY.
