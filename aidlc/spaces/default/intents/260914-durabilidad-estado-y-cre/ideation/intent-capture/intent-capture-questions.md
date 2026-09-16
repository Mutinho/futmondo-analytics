## Sources

- [desc] Initial description: "Implementar FR1 (durabilidad del estado de sync y sesiones Futmondo: TaskManager y SessionStore viven solo en memoria; un reinicio de Fly pierde tareas en curso y sesiones, provocando 403 opacos y tareas huerfanas) y FR5 (no almacenar credenciales Futmondo en claro: SessionStore guarda email+password en claro en memoria). Ambos requisitos comparten el estado en memoria de SessionStore/TaskManager y provienen del plan del intent 260911-analisis-mejoras (requirements.md). Restricciones: mantener stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io), sin reescrituras grandes, coste 0 EUR (tiers gratuitos). Proyecto brownfield futmondo-analytics."
- [scope] Workflow-selected scope: `feature`.
- [memory:M1] `aidlc/spaces/default/memory/project.md#Corrections`: "ALWAYS mantener el proyecto a coste 0€: descartar toda mejora o dependencia con gasto recurrente; solo proponer soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free) (learned 2026-09-11)"

## Q1. ¿Qué problema de negocio/operativo resolvemos y con qué urgencia?

La descripción indica que un reinicio de la máquina Fly pierde las tareas de sync en curso y las sesiones Futmondo (403 opacos, tareas huérfanas) y que las credenciales Futmondo se guardan en claro en memoria. ¿Cuál es el impacto real que quieres eliminar? [desc]

- A. Fiabilidad: que un reinicio no rompa un sync en curso ni deje al usuario con un 403 sin contexto
- B. Seguridad: que las credenciales Futmondo dejen de estar en claro en la memoria del proceso
- C. Ambas por igual (fiabilidad + seguridad), que es el motivo de agruparlas en un mismo intent
- D. Otra prioridad de negocio
- E. Not yet defined
- X. Other (please specify)

[Answer]: C. Ambas por igual (fiabilidad + seguridad), que es el motivo de agruparlas en un mismo intent

## Q2. ¿Quién es el usuario afectado y qué dolor experimenta hoy?

¿A quién impacta el problema y cómo se manifiesta? [desc]

- A. El usuario final de la PWA (pierde el progreso del sync / recibe 403 y debe re-loguear sin explicación)
- B. El propietario/operador del proyecto (riesgo de exposición de credenciales, tareas huérfanas que hay que diagnosticar)
- C. Ambos
- D. Not identified
- X. Other (please specify)

[Answer]: C. Ambos

## Q3. ¿Cómo se ve el éxito y qué criterios medibles importan?

¿Qué resultado observable define que el intent está "hecho"? [desc]

- A. Tras un reinicio de Fly, una tarea de sync puede consultarse y refleja su último estado conocido (no desaparece), y el usuario recibe una acción clara (re-login/reintento) en vez de un 403 opaco
- B. La contraseña Futmondo no está almacenada en claro en el estado del proceso (se evita guardarla, se cifra, o se sustituye por token/re-auth)
- C. Ambos criterios (A + B) se cumplen y la suite de tests existente sigue en verde
- D. Not yet defined
- X. Other (please specify)

[Answer]: C. Ambos criterios (A + B) se cumplen y la suite de tests existente sigue en verde

## Q4. ¿Cuál es el disparador de esta iniciativa?

¿Por qué ahora? [desc]

- A. Deuda técnica priorizada: FR1 y FR5 son los dos hallazgos "Críticos" del plan del intent 260911-analisis-mejoras
- B. Un incidente concreto (pérdida de tareas / 403) ya observado en producción
- C. Preocupación de seguridad por las credenciales en claro
- D. Not applicable
- X. Other (please specify)

[Answer]: A. Deuda técnica priorizada: FR1 y FR5 son los dos hallazgos "Críticos" del plan del intent 260911-analisis-mejoras

## Q5. ¿Quiénes son los stakeholders clave y qué le importa a cada uno?

¿Qué partes interesadas hay más allá de ti como desarrollador/propietario? [desc]

- A. Solo tú (propietario-desarrollador único), sin otros stakeholders formales
- B. Tú + los usuarios de los campeonatos (afectados por la fiabilidad del sync)
- C. Otros colaboradores del proyecto
- D. Not identified
- X. Other (please specify)

[Answer]: A. Solo tú (propietario-desarrollador único), sin otros stakeholders formales

## Q6. ¿Quién decide alcance/prioridad y quién influye?

¿Quién aprueba las decisiones de alcance de este intent? [desc]

- A. Tú decides en solitario (aprobación en los gates de AI-DLC)
- B. Tú decides con input de otros
- C. Not applicable
- X. Other (please specify)

[Answer]: A. Tú decides en solitario (aprobación en los gates de AI-DLC)

## Q7. ¿Hay requisitos de comunicación o cadencia de reporte?

¿Necesitas algún reporte o comunicación formal durante el trabajo? [desc]

- A. No; basta con los gates de aprobación de AI-DLC
- B. Sí, alguna cadencia o notificación concreta
- C. Not applicable
- X. Other (please specify)

[Answer]: A. No; basta con los gates de aprobación de AI-DLC

## Q8. El workflow se inició con scope `feature`. ¿Coincide con el límite de producto que quieres?

El scope seleccionado es `feature`. ¿Confirmas ese scope, o el límite de producto real es otro? [scope] [desc]

- A. Confirmo el scope `feature`: implementar FR1 y FR5 juntos, con diseño + implementación + tests, sin reescrituras grandes y a coste 0 €
- B. En realidad el límite debería ser más pequeño (p. ej. solo FR5, o solo FR1)
- C. En realidad el límite debería ser mayor (incluir otros FR del plan)
- D. Not yet defined
- X. Other (please specify)

[Answer]: A. Confirmo el scope `feature`: implementar FR1 y FR5 juntos, con diseño + implementación + tests, sin reescrituras grandes y a coste 0 €

## Consolidated Summary Confirmation

Resumen consolidado presentado al usuario: intent que agrupa FR1 (durabilidad del estado en memoria de `TaskManager`/`SessionStore` ante reinicios de Fly) y FR5 (credenciales Futmondo en claro en `SessionStore`); beneficiarios usuario final PWA + propietario-operador; éxito = estado de sync consultable tras reinicio + acción clara en vez de 403 + contraseña no en claro + suite de tests en verde; disparador = hallazgos "Críticos" del plan 260911-analisis-mejoras; scope `feature` confirmado, coste 0 €, sin reescrituras grandes.

- Looks correct
- Request changes

[Answer]: Looks correct
