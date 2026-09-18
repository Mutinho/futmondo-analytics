# Preguntas — Code Generation (Backend Security Hardening)

Scope `security-patch`, zero-Unit. Depth Minimal: en Construcción las preguntas
son excepcionales; las decisiones ya se tomaron en Análisis de Requisitos y NFR
Requirements. La única interacción de esta etapa es la aprobación del plan.

## Plan Approval

Aprueba este plan exacto de generación de código, que cubre
`code-generation-plan.md` (con su Testing Contract embebido) y
`unit-test-instructions.md`.

Alcance: FR6 (validar `price>0` → 422 en `place_bid`), FR9 (corregir el bug de
precedencia de `is_refresh_token_valid` + regresión + actualizar caracterización),
FR7 (documentar + test que congela la exposición de fotos), FR8 (eliminar
`SSL_VERIFY=0` + test anti-`verify=False`), FR18 (confirmar/consolidar la guarda
de administración). Metodología test-after, strategy Minimal.

[Approval Fingerprint]: sha256:v3:e7ff61b8e05acba57d5383811fe5e9bfd497a3422238c7289a7251fd106a635c
[Planned Source]: 83f745620a665feaf9cf889fd1e4e2cab55c2087c01470fcd2a36f2dea39987c

- Approve Plan
- Request Changes

[Answer]: Approve Plan
