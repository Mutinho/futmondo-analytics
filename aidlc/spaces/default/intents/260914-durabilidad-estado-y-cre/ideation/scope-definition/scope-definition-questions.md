# Scope Definition — Preguntas de Alcance y Priorización

> Durabilidad del estado y credenciales Futmondo (FR1 + FR5).
> Responde cada pregunta rellenando su `[Answer]:`. Las letras son solo etiquetas
> de almacenamiento; en la conversación se te presentan como opciones numeradas.

## Sources

- Initial description: intent-statement.md (FR1 durabilidad, FR5 credenciales) [desc]
- feasibility-assessment.md (viabilidad a coste 0 €, persistencia en Neon) [Q1]
- constraint-register.md (C-T1..C-T3, C-O1, C-R1) [scope]
- Workflow-selected scope: `feature` [scope]

## Q1 — Alcance mínimo viable (MVS)

El intent agrupa FR1 (durabilidad de tareas de sync + sesiones) y FR5 (no
almacenar la contraseña en claro). ¿Cuál es el alcance mínimo que aporta valor
en esta entrega?

- A. Ambos completos: durabilidad de tareas Y sesiones (FR1) + tratamiento de credenciales (FR5), todo en este intent.
- B. Solo FR1 (durabilidad) ahora; FR5 se difiere a un intent posterior.
- C. FR1 + FR5 pero limitando FR1 a persistir solo las tareas de sync (sesiones se difieren).
- X. Other (please specify)

[Answer]: A

## Q2 — Must-have vs. nice-to-have (capacidades)

De las siguientes capacidades, ¿cuáles consideras imprescindibles (must-have)
para dar por lograda esta entrega, y cuáles serían deseables pero opcionales?

Capacidades candidatas:
1. Persistir estado de tareas de sync en Neon (sobrevive a reinicio).
2. Persistir sesiones Futmondo en Neon (sobrevive a reinicio).
3. Mensaje de acción clara al usuario (re-login/reintento) en lugar de 403 opaco.
4. Eliminar almacenamiento en claro de la contraseña (cifrado o re-auth).
5. Limpieza/expiración de tareas y sesiones antiguas en BD (housekeeping).
6. Reanudar automáticamente tareas de sync interrumpidas por el reinicio.

- A. Must-have: 1, 2, 3, 4. Nice-to-have: 5, 6.
- B. Must-have: 1, 2, 3, 4, 5. Nice-to-have: 6.
- C. Must-have: 1, 3, 4. Nice-to-have: 2, 5, 6.
- X. Other (please specify)

[Answer]: A

## Q3 — Enfoque para FR5 (credenciales)

La feasibility deja abierta la decisión (a resolver en diseño), pero conviene
fijar la preferencia de alcance. ¿Qué dirección prefieres para no guardar la
contraseña en claro?

- A. Dejar ambas opciones abiertas (re-auth bajo demanda vs. cifrado en reposo) y decidir en la etapa de diseño.
- B. Preferir re-auth/token bajo demanda (no persistir contraseña en absoluto).
- C. Preferir cifrado en reposo con clave gestionada como secret de Fly.io (mantiene UX actual).
- X. Other (please specify)

[Answer]: A

## Q4 — Preferencia de secuenciación

¿Con qué criterio prefieres ordenar la entrega de las capacidades?

- A. Dependency-first: primero la capa de persistencia en Neon, luego tareas, sesiones y credenciales sobre ella.
- B. Risk-first: atacar primero lo más incierto (persistencia de sesiones con TTL/concurrencia y FR5).
- C. Value-first: primero lo que más nota el usuario (durabilidad de tareas + mensaje de acción claro), luego el resto.
- X. Other (please specify)

[Answer]: A

## Q5 — Plazos y exclusiones explícitas

¿Hay algún plazo duro asociado a alguna capacidad, y confirmas qué queda
explícitamente fuera de alcance en este intent?

- A. Sin plazo duro. Fuera de alcance: reescrituras grandes, cambios de stack, y cualquier solución con coste recurrente.
- B. Sin plazo duro. Fuera de alcance además: la reanudación automática de tareas (solo se persiste el estado, no se re-lanza).
- C. Hay un plazo/condición que debo indicar en Other.
- X. Other (please specify)

[Answer]: B

## Consolidated Summary Confirmation

Resumen del alcance acordado, antes de generar los artefactos:

- **Q1 — MVS**: FR1 + FR5 completos en este intent (durabilidad de tareas y sesiones + tratamiento de credenciales).
- **Q2 — Prioridad**: Must-have = persistir tareas (1), persistir sesiones (2), mensaje de acción clara en vez de 403 (3), no guardar contraseña en claro (4). Nice-to-have = housekeeping/expiración en BD (5), reanudación automática de tareas (6).
- **Q3 — FR5**: la contraseña no queda en claro; la elección concreta (re-auth vs. cifrado en reposo) se decide en la etapa de diseño. Ambas vías coste 0 €.
- **Q4 — Secuenciación**: dependency-first — primero la capa de persistencia en Neon, luego tareas, sesiones y credenciales sobre ella.
- **Q5 — Plazos/exclusiones**: sin plazo duro. Fuera de alcance: reescrituras grandes, cambios de stack, coste recurrente, y la reanudación automática de tareas (solo se persiste el estado, no se re-lanza).

[Answer]: Looks correct

