# NFR Requirements — U1 `u1-error-layer` (preguntas)

Unidad: **U1 capa de errores** (`kind: library`). Artefactos aplicables por kind:
`security-requirements`, `tech-stack-decisions`, `traceability`
(performance/scalability/reliability/observability aplican a `service`, no a
`library`).

## Sources

- [desc] Initial description: "FR3.2 + FR4.1; NO ampliar god-files; stack fijo (FastAPI/Python 3.12), sin dependencias nuevas, coste 0 EUR. Conversation language: Spanish."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/project.md#Forbidden`: "NEVER incluir el password ni el token Futmondo del usuario en el mensaje, el `repr` ni el `exc_info` de una excepción de integración (NFR3)."

---

## Q1. Requisito de seguridad de la capa de errores (NFR3)

- A. **Sin secretos en excepciones (verificable)**: ninguna excepción de `integration_errors` incluye password/token en su mensaje, `repr` o `exc_info`; solo `failure_mode` + contexto no sensible (status, endpoint). Verificable con un spec que construye la excepción con credenciales de prueba y asvera que no aparecen en `str(exc)`/`repr(exc)`/`exc.args`. gitleaks escanea los tests (fakes, nunca credenciales reales).
- B. Otra cosa (indícala en Other).
- X. Other (please specify)

[Answer]: A. Sin secretos en excepciones (verificable): ninguna excepción de integration_errors incluye password/token en su mensaje, repr o exc_info; solo failure_mode + contexto no sensible. Verificable con un spec que construye la excepción con credenciales de prueba y asvera que no aparecen en str/repr/args.

## Q2. Decisiones de stack para U1

- A. **Sin dependencias nuevas**: la jerarquía de excepciones es stdlib de Python 3.12 (clases que heredan de `Exception`); ubicada en un módulo nuevo `integration_errors` bajo `backend/app/`. Sin librerías nuevas, coste 0 €. Tests con `pytest` desde `backend/`.
- B. Otra cosa (indícala en Other).
- X. Other (please specify)

[Answer]: A. Sin dependencias nuevas: jerarquía de excepciones stdlib de Python 3.12 en un módulo nuevo integration_errors bajo backend/app/. Sin librerías nuevas, coste 0 €. Tests con pytest.

## Consolidated Summary Confirmation

Resumen NFR de U1 (antes de fijar los artefactos):

- **Seguridad (Q1=A)**: NFR3 verificable — sin secretos en mensaje/repr/exc_info de las excepciones; spec que lo prueba con credenciales de prueba.
- **Stack (Q2=A)**: sin dependencias nuevas; módulo `integration_errors` con stdlib; coste 0 €.
- **Artefactos** (aplicables a kind=library): security-requirements.md, tech-stack-decisions.md, traceability.json.

[Answer]: Looks correct
