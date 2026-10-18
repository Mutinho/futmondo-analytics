## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T18:02:43Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | functional-spec.md > AuthService | Estado mutable compartido (`accessToken` + orquestación) leído por el provider async sin aislamiento → carrera de datos. | Declarar `AuthService` como `actor`; provider lee un snapshot Sendable (holder con lock). | New |
| R-02 | Critical | rules.md > AR4 | El refresh ante 401 concurrente no coalesce → N refresh en paralelo, rotación múltiple y posible revocación de la sesión renovada. | Coalescing: una única `Task` de refresh en vuelo compartida. | New |
| R-03 | Major | AR5 / contract-summary | `pendingLogoutRevocation` "se persiste" sin decir dónde; riesgo de duplicar el refresh token fuera del Keychain. | Flag booleano (UserDefaults); token solo en Keychain hasta revocar/TTL. | New |
| R-04 | Minor | decisions.md ADR-4 | Atribuía el reintento a "AuthViewModel/AuthService", contradiciendo el dueño único. | Alinear: AuthService único dueño; ViewModel no reintenta. | New |
| R-05 | Minor | functional-spec `[weak self]` | Documentar invariante self==nil → provider nil, no `[unowned self]`. | Añadir invariante. | New |

### Summary

Pase adversarial del functional-spec de la auth nativa. Almacenamiento de tokens correcto (access en memoria, refresh en Keychain, nada en claro), bootstrap que distingue 401 de red/5xx, refresh por header/body (D-01) y estrategia de verificación honesta (swift test con dobles + validación en iPhone). Dos Critical materiales: ausencia de modelo de concurrencia para `AuthService` (carrera sobre el token) y falta de coalescing del refresh (tormenta/revocación). Un Major (dónde vive `pendingLogoutRevocation`) y dos Minor. NOT-READY: requiere definir actor + coalescing.
