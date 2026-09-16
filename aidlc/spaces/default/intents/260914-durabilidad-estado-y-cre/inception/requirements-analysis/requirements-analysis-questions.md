# Requirements Analysis — Preguntas de Clarificación

> Durabilidad del estado y credenciales Futmondo (FR1 + FR5). Proyecto brownfield.
> Responde rellenando cada `[Answer]:`.

## Sources

- intent-statement.md, scope-document.md (alcance aprobado) [scope]
- codekb: architecture.md, code-quality-assessment.md (estado en memoria FR1, credenciales FR5) [desc]
- team-practices.md (test-after + caracterización; coste 0 €) [scope]

## Q1 — Comportamiento de la sesión tras un reinicio (FR1)

Hoy, tras un reinicio, la sesión Futmondo se pierde y el usuario recibe un 403
opaco. ¿Cuál es el comportamiento esperado que debe cumplir el intent?

- A. La sesión se reconstruye de forma transparente (el usuario no nota el reinicio; la primera petición tras el reinicio funciona sin re-login).
- B. Si la sesión no puede reconstruirse, el backend devuelve una respuesta de acción clara (p. ej. 401 con "vuelve a iniciar sesión") en lugar de un 403 opaco; no se exige reconstrucción transparente.
- C. Ambas: intentar reconstruir de forma transparente y, si no es posible, devolver la acción clara.
- X. Other (please specify)

[Answer]: C

## Q2 — Estado de las tareas de sync tras un reinicio (FR1)

Hoy una tarea de sync en curso queda huérfana tras un reinicio (el hilo muere).
¿Qué debe garantizar el intent para las tareas?

- A. Que el estado de la tarea sea consultable tras el reinicio y refleje su último estado conocido (p. ej. "interrumpida por reinicio"); NO se exige reanudar automáticamente.
- B. Además de A, marcar explícitamente como fallida/interrumpida cualquier tarea que estuviera en curso, para que el usuario pueda relanzarla manualmente.
- C. Reanudar automáticamente la tarea interrumpida (fuera del alcance acordado en scope-definition).
- X. Other (please specify)

[Answer]: B

## Q3 — Idempotencia / tarea duplicada (FR1)

Hoy el backend responde 409 si ya hay una tarea de sync activa. Al persistir el
estado de tareas, ¿cómo debe comportarse ante un intento de lanzar otra?

- A. Mantener el comportamiento actual: rechazar (409) si hay una tarea activa según el estado persistido.
- B. Igual que A, pero considerar "no activa" una tarea marcada como interrumpida por reinicio (para que el usuario pueda relanzar tras un reinicio).
- X. Other (please specify)

[Answer]: B

## Q4 — Alcance del cifrado/no-persistencia de credenciales (FR5)

La regla dura ya afirmada es NEVER guardar la contraseña en claro. Para los
requisitos, ¿qué debe garantizar el intent respecto a las credenciales?

- A. Que la contraseña no esté en claro en ningún estado persistente ni en memoria del proceso (el "cómo" —re-auth o cifrado— se decide en diseño).
- B. Solo que no esté en claro en el estado PERSISTENTE (BD); se acepta que siga en memoria del proceso durante la vida de la sesión.
- X. Other (please specify)

[Answer]: B

## Q5 — NFRs medibles a fijar

¿Qué objetivos no funcionales quieres fijar como requisitos verificables?

- A. Rendimiento: la persistencia de sesión/tarea no debe degradar de forma perceptible el camino de sesión (objetivo: overhead de lectura/escritura de estado < ~50 ms por operación, sobre Neon free). Seguridad: contraseña nunca en claro en reposo. Coste: 0 € (tiers gratuitos). Compatibilidad: la suite existente permanece en verde.
- B. Igual que A, pero sin fijar un umbral numérico de latencia (solo "sin degradación perceptible", a validar en diseño).
- X. Other (please specify)

[Answer]: B

## Consolidated Summary Confirmation

Resumen de las respuestas, antes de generar el artefacto de requisitos:

- **Q1 — Sesión tras reinicio**: ambas garantías — reconstrucción transparente cuando sea posible y, si no, respuesta de acción clara (re-login) en lugar de 403 opaco.
- **Q2 — Tareas tras reinicio**: el estado de la tarea es consultable y una tarea en curso se marca explícitamente como interrumpida por reinicio (sin reanudación automática), para relanzamiento manual.
- **Q3 — Idempotencia**: se mantiene el 409 ante tarea activa, salvo cuando la tarea está marcada como interrumpida por reinicio (entonces es relanzable).
- **Q4 — Credenciales (FR5)**: la contraseña nunca en claro en el estado persistente (BD); se acepta que siga en memoria del proceso durante la vida de la sesión (el "cómo" —re-auth vs cifrado— se decide en diseño).
- **Q5 — NFRs**: sin degradación perceptible del camino de sesión (sin umbral numérico fijo; a validar por medición en diseño/build); contraseña nunca en claro en reposo; coste 0 €; la suite de tests existente permanece en verde.

[Answer]: Looks correct
