# Practices Discovery — Entrevista

> Proyecto brownfield futmondo-analytics. Solo se pregunta lo que la evidencia y
> las revisiones (calidad, desarrollo, seguridad) no pudieron establecer.
> Responde rellenando cada `[Answer]:`.

## Sources

- Borrador del lead: team-practices.md, discovered-rules.md, evidence.md [desc]
- Contribuciones: contributions/aidlc-{quality,developer,devsecops}-agent.md [desc]
- Codekb y config del repo (git, CI, ruff, eslint, fly.toml) [scope]

## Q1 — Estrategia de merge (Way of Working)

La evidencia diverge: el default del framework es squash-merge, pero se observan
merge commits de PR en el historial. ¿Cuál formalizamos como práctica?

- A. Squash-merge a `main` (historia lineal; default del framework).
- B. Merge commit de PR (como se observa en el historial actual).
- C. Me da igual / lo que sea más simple para un repo de un solo desarrollador.
- X. Other (please specify)

[Answer]: A

## Q2 — Walking Skeleton

¿Construir primero una rebanada fina end-to-end? Un walking skeleton es una
versión mínima que atraviesa todo el sistema, hecha primero para probar que las
piezas conectan antes de meter las features reales. Para este intent (backend,
sistema ya en producción):

- A. No (OFF) — el sistema ya funciona; no hay nada que bootstrapear.
- B. Sí (ON) — quiero una rebanada fina primero.
- X. Other (please specify)

[Answer]: A

## Q3 — Piso de cobertura de tests (Testing Posture)

Hoy la cobertura es informativa, sin piso bloqueante. El scope `feature` ya
añade un suelo de 80% de líneas. ¿Cómo quieres tratar la cobertura para las
piezas nuevas de durabilidad (SessionStore/TaskManager)?

- A. Mantener el suelo de scope (80% líneas) solo como referencia global, y exigir tests que cubran los caminos nuevos y de error de las piezas de durabilidad (sin piso porcentual adicional bloqueante).
- B. Añadir un piso diferencial bloqueante (p. ej. 80%) específico sobre el código nuevo de durabilidad.
- C. Mantener cobertura totalmente informativa, sin piso.
- X. Other (please specify)

[Answer]: A

## Q4 — Convención de idioma en el código (Code Style)

El desarrollador señaló que el borrador afirmaba "comentarios en castellano",
pero el código real tiene docstrings/comentarios en inglés y solo el texto de
cara al usuario (mensajes de error) y los commits en castellano. ¿Qué convención
afirmamos?

- A. Código (identificadores, docstrings, comentarios) en inglés; texto de usuario y commits en castellano (refleja el código actual).
- B. Todo en castellano (comentarios incluidos).
- X. Other (please specify)

[Answer]: A

## Q5 — Regla de seguridad para credenciales (FR5)

Seguridad propone fijar el orden de preferencia para no guardar la contraseña en
claro, como regla mandada. ¿La afirmas?

- A. Sí: ALWAYS preferir no persistir la contraseña; si hay que conservarla, cifrarla en reposo con clave gestionada como secret de Fly.io. NEVER almacenar la contraseña en claro (memoria o BD).
- B. Solo la prohibición dura (NEVER credenciales en claro), sin fijar orden de preferencia (se decide en diseño).
- X. Other (please specify)

[Answer]: B

## Consolidated Summary Confirmation

Resumen de las prácticas afirmadas, antes de integrarlas y promoverlas:

- **Q1 — Way of Working**: trunk-based; ramas cortas desde `main` + MR con gate de CI; squash-merge a `main` al fusionar.
- **Q2 — Walking Skeleton**: OFF (sistema en producción; nada que bootstrapear).
- **Q3 — Testing Posture**: test-after con caracterización primero; suelo de cobertura del scope `feature` (80%) como referencia global; exigir tests de los caminos nuevos y de error de las piezas de durabilidad (sin piso porcentual adicional bloqueante).
- **Q4 — Code Style**: código (identificadores, docstrings, comentarios) en inglés; texto de usuario y commits en castellano.
- **Q5 — Credenciales (FR5)**: solo la prohibición dura (NEVER contraseña en claro en memoria o BD); el orden de preferencia (re-auth vs. cifrado) se decide en diseño.
- Reglas duras heredadas que se mantienen: coste 0 € (solo tiers gratuitos); JWT_SECRET no-default; gate de CI bloqueante (tests + gitleaks) antes de merge.

[Answer]: Looks correct
