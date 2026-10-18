## Review

**Verdict:** NOT-READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-17T18:14:32Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Critical | security-requirements.md > SEC-A3 | El `password` del formulario persiste en `AuthViewModel` (SecureField); ninguna regla exige borrarlo tras login. | Exigir `AuthViewModel.password = ""` tras login OK y en logout. | New |
| R-02 | Critical | security-requirements.md > SEC-A2 | El `TokenHolder` snapshot es una segunda copia del access token fuera del actor; logout no lo nombra como ubicación a borrar. | SEC-A2/AR5: borrar access token en AMBAS ubicaciones (actor + holder). | New |
| R-03 | Minor | security-requirements.md | Supervivencia del Keychain item ante re-firma gratuita (~7 días) no documentada. | Documentar: relectura fallida → `.unauthenticated` (lado seguro). | New |

### Summary

Pase adversarial de seguridad del bolt de auth. SEC-A1 (Keychain `AfterFirstUnlockThisDeviceOnly`, sin iCloud), SEC-A4/A5/A6 (flag sin duplicar token, transporte vía NetworkClient con D-01, solo SDK de Apple, Face ID diferido) son sólidos. Dos Critical en la gestión del token en memoria: el `password` del ViewModel persiste sin borrado exigido, y el `TokenHolder` snapshot (segunda copia del access token) no se incluye en el borrado de logout. Un Minor sobre la supervivencia del Keychain ante re-firma. NOT-READY: requiere exigir el borrado de ambas copias y del password.
