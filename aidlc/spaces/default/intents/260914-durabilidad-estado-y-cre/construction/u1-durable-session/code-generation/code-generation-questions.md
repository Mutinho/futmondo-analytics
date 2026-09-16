# Code Generation Questions — u1-durable-session

## Plan Approval

Aprobación del plan exacto de generación de código para `u1-durable-session`, que cubre
`code-generation-plan.md` (con su Testing Contract embebido) y `unit-test-instructions.md`.

Resumen del plan (14 pasos): estructura + capa `stores/`; runner de tests listo; **caracterización
primero** (congelar el 403 actual y bugs conocidos); esquema durable (`user_session`,
`protected_credential`) por script SQL idempotente; `SessionRepository` con lock BD y purga
perezosa; `CredentialProtection` (handle de re-auth **cifrado** con `FUTMONDO_CRED_KEY`, tipo
redactado, `reauthenticate` público / `resolve` interno) y `SessionService.ensureSession`
idempotente; re-cableo de `/auth/refresh` y `_helpers.get_user_futmondo_client` (401 accionable en
vez de 403 opaco); gitleaks en `verify`; docs + trazabilidad. Tests test-after por capa (Standard,
5–8 por componente) con **fakes de persistencia** (nunca Neon real). Nunca la contraseña en claro.

Instrucciones de test (resumen): `pytest` desde `backend/`, comando por-unidad scoped a
`tests/test_durable_session_*.py`; fakes de persistencia; cobertura como referencia (sin piso
bloqueante adicional).

[Approval Fingerprint]: sha256:v3:648fd74e084ed096dc853814acc0efbaeee0da20db96154b9e98c14dfd78899a
[Planned Source]: 4cca746a795ff3e5ae44dcfc151a70f83a9a776b8cde7aa3d6c3064bf326d8b3

- "Approve Plan" — proceder a generar el código
- "Request Changes" — revisar el plan

[Answer]: Approve Plan
