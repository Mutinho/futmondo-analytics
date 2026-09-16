## Sources

- [desc] Initial description: "Implementar FR1 (durabilidad del estado de sync y sesiones Futmondo: TaskManager y SessionStore viven solo en memoria; un reinicio de Fly pierde tareas en curso y sesiones, provocando 403 opacos y tareas huerfanas) y FR5 (no almacenar credenciales Futmondo en claro: SessionStore guarda email+password en claro en memoria). Ambos requisitos comparten el estado en memoria de SessionStore/TaskManager y provienen del plan del intent 260911-analisis-mejoras (requirements.md). Restricciones: mantener stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io), sin reescrituras grandes, coste 0 EUR (tiers gratuitos). Proyecto brownfield futmondo-analytics."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/project.md#Corrections`: "ALWAYS mantener el proyecto a coste 0€: descartar toda mejora o dependencia con gasto recurrente; solo proponer soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free) (learned 2026-09-11)"

## Q1. ¿Con qué sistemas existentes debe integrarse la solución de persistencia?

FR1 requiere persistir el estado de tareas de sync y sesiones fuera de la memoria del proceso. ¿Dónde debe apoyarse? [desc] [memory:M1]

- A. Neon PostgreSQL (ya en el stack): tablas nuevas para tareas/sesiones, coste 0 €
- B. Almacenamiento de Fly.io (volumen persistente) u otro mecanismo
- C. A definir en diseño; la restricción firme es coste 0 € y no añadir dependencias con gasto
- D. Not applicable
- X. Other (please specify)

[Answer]: A. Neon PostgreSQL (ya en el stack): tablas nuevas para tareas/sesiones, coste 0 €

## Q2. ¿Hay requisitos regulatorios/de cumplimiento que afecten al tratamiento de las credenciales Futmondo (FR5)?

Las credenciales Futmondo son de terceros (el usuario). ¿Aplica alguna normativa (p. ej. protección de datos) que condicione cómo se almacenan/cifran? [desc]

- A. No hay requisitos regulatorios formales; aplica buena práctica de seguridad (no guardar secretos en claro)
- B. Sí, aplica alguna normativa concreta (especificar)
- C. Not applicable
- X. Other (please specify)

[Answer]: A. No hay requisitos regulatorios formales; aplica buena práctica de seguridad (no guardar secretos en claro)

## Q3. Para FR5, ¿qué enfoque de tratamiento del secreto es aceptable?

`SessionStore` hoy guarda email+password en claro para poder re-autenticar la sesión Futmondo (TTL 12h). ¿Qué dirección prefieres explorar en diseño? [desc]

- A. Evitar guardar la contraseña: rediseñar hacia token/re-auth bajo demanda (el usuario re-introduce credenciales o se usa un token de sesión Futmondo)
- B. Cifrar la contraseña en reposo con una clave de entorno (secret de Fly.io), coste 0 €
- C. A decidir en diseño evaluando ambas (A y B) por impacto en UX y complejidad
- D. Not yet defined
- X. Other (please specify)

[Answer]: C. A decidir en diseño evaluando ambas (A y B) por impacto en UX y complejidad

## Q4. ¿Hay restricciones de presupuesto/plazo o bloqueos organizativos?

¿Alguna limitación más allá de las ya conocidas (coste 0 €, sin reescrituras grandes)? [desc] [memory:M1]

- A. Solo las ya conocidas: coste 0 € (tiers gratuitos) y sin reescrituras grandes
- B. Hay además una restricción de plazo concreta
- C. Not applicable
- X. Other (please specify)

[Answer]: A. Solo las ya conocidas: coste 0 € (tiers gratuitos) y sin reescrituras grandes

## Q5. ¿Hay incertidumbre técnica significativa que debamos registrar como riesgo?

Por ejemplo, el impacto en el TTL de sesión, la concurrencia (locks por usuario ya existentes) o la migración de esquema en Neon. [desc]

- A. Sí: registrar como riesgos la persistencia de sesiones con TTL, la concurrencia y la migración de esquema; mitigarlos en diseño
- B. No hay incertidumbre relevante; es un cambio de bajo riesgo
- C. Not yet defined
- X. Other (please specify)

[Answer]: A. Sí: registrar como riesgos la persistencia de sesiones con TTL, la concurrencia y la migración de esquema; mitigarlos en diseño

## Consolidated Summary Confirmation

Resumen: solución viable en el stack actual a coste 0 €. FR1 → persistir tareas de sync y sesiones en Neon PostgreSQL (tablas nuevas). FR5 → eliminar la contraseña en claro, decidiendo en diseño entre re-auth/token o cifrado en reposo con secret de Fly.io. Sin normativa formal aplicable. Riesgos registrados: TTL de sesión, concurrencia (locks por usuario), migración de esquema, impacto UX del re-auth, límites del tier free de Neon. Sin reescrituras grandes.

- Looks correct
- Request changes

[Answer]: Looks correct
