# Security Requirements — u1-market

> Unit `u1-market` (kind `ui`). La novedad de F3 frente a F1/F2 es la
> **escritura** (pujar/cancelar) y un **2º endpoint externo** (Sofascore); ambos
> **refuerzan** las garantías de seguridad ya afirmadas, sin introducir nada
> nuevo. IDs derivados de NFR3 (seguridad) de inception.

## Sources

- `.../inception/requirements-analysis/requirements.md` (NFR3).
- `.../construction/u1-market/functional-design/functional-spec.md` (W4–W7, seguridad).
- `aidlc/spaces/default/memory/{project,team}.md` (reglas afirmadas de credenciales).
- `nfr-requirements-questions.md` (Q2).

## Modelo de autenticación / autorización

| ID | Requisito | Verificación | Origen |
|---|---|---|---|
| NFR3.1 | Todas las llamadas autenticadas | `/market/today`, `/market/bid`, `/market/cancelbid`, `/sofascore/player/{name}` viajan con `Authorization: Bearer <access token>`. | NFR3, W1/W4/W5/W7 |
| NFR3.2 | Access token sólo en memoria | El access token vive en memoria (`AuthService` actor / `TokenHolder`); NUNCA se persiste. | NFR3, F1 |
| NFR3.3 | Refresh token sólo en Keychain | El refresh token permanece en Keychain (`AfterFirstUnlockThisDeviceOnly`, sin iCloud sync); NUNCA en `localStorage`/`ApplicationSettings`/claro. | regla durable afirmada |
| NFR3.4 | Backend como autoridad de validación | La UI valida en cliente para UX, pero el backend revalida la puja (`price>0`, `price≤5_000_000_000`) y es la autoridad; un rechazo del backend se refleja como `.rejected`. | W4/W6, FR6 |
| NFR3.5 | TLS obligatorio | La base URL es `https`; `URLSessionNetworkClient` rechaza en el `init` cualquier base URL no-https (SEC-N1). | F1, NFR3 |

## Protección de credenciales (refuerzo de reglas afirmadas)

| ID | Requisito | Verificación | Origen |
|---|---|---|---|
| NFR3.6 | Sin material de credencial en errores | Ni el password ni el token aparecen en el mensaje, `repr`, `exc_info` ni en los avisos de puja/cancelación; los avisos usan el `message`/`detail` del backend o un texto genérico. | regla durable afirmada, W6 |
| NFR3.7 | Sin secretos hardcodeados | No se hardcodean tokens/secretos en el código ni en los tests; los tests usan dobles/fakes (gitleaks escanea el árbol). | phase guardrails, memoria |
| NFR3.8 | Escritura = endpoints autenticados | Pujar y cancelar son operaciones de escritura autenticadas; no hay bypass de auth; la sesión es la de F1. | W4/W5, NFR3 |

## Amenazas consideradas

- **Fuga de credenciales por logging**: mitigada por NFR3.6 (avisos sin material
  de credencial) y NFR3.7 (sin secretos en código/tests).
- **MITM**: mitigada por NFR3.5 (TLS obligatorio, rechazo de no-https).
- **Persistencia insegura del refresh token**: mitigada por NFR3.3 (Keychain
  `ThisDeviceOnly`, nunca en claro).
- **Puja fuera de límites / manipulación de importe**: la UI valida
  (`BidAmountValidator`) y el backend revalida (NFR3.4); la UI nunca es la única
  barrera.

## Assumptions & Open Questions

None.
