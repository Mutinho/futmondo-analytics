# NFR Design — U1 `u1-error-layer` (preguntas)

Unidad: **U1 capa de errores** (`kind: library`). Único NFR con peso: seguridad
(NFR3, SR1: sin secretos en excepciones). Artefactos aplicables por kind:
`security-design`, `logical-components`, `traceability`.

## Sources

- [desc] Initial description: "FR4.1 modulo integration_errors; NFR3 sin secretos en excepciones. NO ampliar god-files; coste 0 EUR. Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/project.md#Forbidden`: "NEVER incluir el password ni el token Futmondo del usuario en el mensaje, el `repr` ni el `exc_info` de una excepción de integración (NFR3)."

---

## Q1. Diseño de la garantía de no-filtración de secretos (SR1)

¿Cómo se materializa el requisito de que las excepciones nunca lleven credenciales?

- A. **Por construcción + spec de defensa**: las excepciones de `integration_errors` se construyen SOLO con `failure_mode` + contexto no sensible explícito (`status`, `endpoint`); nunca reciben el objeto de request/credenciales. El diseño es "no pasar el secreto al constructor" (defensa en profundidad: aunque un llamador pase texto, la firma del constructor no acepta credenciales). Se refuerza con un spec que asvera la ausencia de credenciales en `str/repr/args`.
- B. **Por saneo/redacción**: la excepción recibe contexto libre y un paso de redacción elimina patrones de credencial.
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A. Por construcción + spec de defensa: las excepciones de integration_errors se construyen solo con failure_mode + contexto no sensible explícito (status, endpoint); la firma del constructor no acepta credenciales (defensa en profundidad, filtración imposible por construcción). Reforzado con un spec que asvera ausencia de credenciales en str/repr/args.

## Consolidated Summary Confirmation

Resumen del diseño NFR de U1 (antes de fijar los artefactos):

- **Seguridad (Q1=A)**: no-filtración por construcción — el constructor de las excepciones solo acepta failure_mode + contexto no sensible; la credencial nunca llega a la excepción. Defensa en profundidad + spec que lo asvera.
- **Componentes lógicos**: el módulo integration_errors es un componente sin estado, sin dependencias, sin blast radius (biblioteca de tipos).
- **Artefactos** (kind=library): security-design.md, logical-components.md, traceability.json.

[Answer]: Looks correct
