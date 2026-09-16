# Scope Document — Durabilidad del estado y credenciales Futmondo

> Etapa: Scope Definition (Ideación). Scope de workflow: `feature`.
> Deriva de intent-statement.md, feasibility-assessment.md y constraint-register.md.

## Sources

- intent-statement.md — problema, cliente, métricas de éxito, disparador (FR1, FR5) [desc]
- feasibility-assessment.md — viabilidad a coste 0 €, persistencia en Neon [Q1]
- constraint-register.md — C-T1..C-T3, C-O1..C-O2, C-R1 [scope]
- scope-definition-questions.md — respuestas Q1–Q5 (confirmadas) [Q1] [Q2] [Q3] [Q4] [Q5]

## Objetivo del alcance

Hacer que dos piezas de estado crítico dejen de vivir solo en la memoria del
proceso backend, atacando juntos los dos hallazgos "Crítico" del plan de mejoras:

- **FR1 — Durabilidad**: el estado de las tareas de sync (`TaskManager`) y de las
  sesiones Futmondo por usuario (`SessionStore`) sobrevive a un reinicio de la
  máquina Fly, persistiéndose en Neon PostgreSQL. [Q1]
- **FR5 — Credenciales**: la contraseña Futmondo del usuario deja de almacenarse
  en claro en el estado del proceso. [Q1]

Ambos se abordan en el mismo intent porque comparten el estado en memoria de
`SessionStore`/`TaskManager`, lo que permite reutilizar un único diseño de
persistencia. [Q1] [desc]

## Dentro de alcance (IN)

| # | Capacidad | Prioridad | Trazabilidad |
|---|-----------|-----------|--------------|
| 1 | Persistir el estado de las tareas de sync en Neon, de modo que una tarea sea consultable tras un reinicio y refleje su último estado conocido | Must-have | FR1 [Q2] |
| 2 | Persistir las sesiones Futmondo por usuario en Neon, preservando el TTL (12h) y la concurrencia con locks por usuario | Must-have | FR1, C-T3 [Q2] |
| 3 | Devolver al usuario una acción clara (re-login/reintento) en lugar de un 403 opaco cuando la sesión no está disponible tras un reinicio | Must-have | FR1 (métrica de éxito) [Q2] |
| 4 | Eliminar el almacenamiento en claro de la contraseña Futmondo (por re-auth bajo demanda o cifrado en reposo; a decidir en diseño) | Must-have | FR5 [Q2] [Q3] |
| 5 | Limpieza/expiración de tareas y sesiones antiguas en la BD (housekeeping) | Nice-to-have | FR1 [Q2] |
| 6 | Reanudar automáticamente las tareas de sync interrumpidas por el reinicio | Nice-to-have (declarada OUT en esta entrega) | FR1 [Q2] [Q5] |

Alcance de trabajo confirmado: **diseño + implementación + tests**, sin
reescrituras grandes, manteniendo el stack actual y a coste 0 €. [desc] [memory:M1]

## Fuera de alcance (OUT)

| # | Exclusión | Motivo | Trazabilidad |
|---|-----------|--------|--------------|
| O1 | Reescrituras grandes o refactor arquitectónico amplio | Límite de producto confirmado | C-T1 [desc] |
| O2 | Cambios de stack o dependencias con gasto recurrente | Coste 0 € | C-O1, C-T2 [memory:M1] |
| O3 | Reanudación automática de tareas de sync (solo se persiste el estado; no se re-lanzan las tareas interrumpidas) | Decisión Q5; evita salto de complejidad | [Q5] |
| O4 | Requisitos regulatorios formales / cumplimiento normativo | No aplican; rige solo la buena práctica de no guardar secretos en claro | C-R1 [Q2] |

## Enfoque de FR5 (diferido a diseño)

La contraseña no debe quedar en claro. La elección concreta se decide en la
etapa de diseño entre dos vías, ambas coste 0 €: [Q3]

- **(A) Re-auth / token bajo demanda**: no persistir la contraseña en absoluto.
- **(B) Cifrado en reposo**: cifrar la contraseña con una clave gestionada como
  secret de Fly.io; mantiene la UX actual.

Este documento fija el *qué* (no en claro) y deja el *cómo* para diseño,
conforme a la disciplina de la fase de Ideación (sin detalle de implementación). [Q3]

## Secuenciación (dependency-first)

1. **Capa de persistencia en Neon**: esquema (tablas nuevas) y acceso a estado.
   Es la base común de las cuatro capacidades must-have. [Q4]
2. **Durabilidad de tareas de sync** (capacidad 1) sobre esa capa.
3. **Durabilidad de sesiones** (capacidad 2), preservando TTL y locks.
4. **Mensaje de acción clara** (capacidad 3) apoyado en la sesión persistida.
5. **Tratamiento de credenciales FR5** (capacidad 4).

El riesgo identificado (TTL/concurrencia de sesiones, migración de esquema)
queda cubierto dentro del paso 1–3, sin necesidad de un orden risk-first
separado. [Q4] [Q5]

## Mapa de flujo de valor

| Capacidad | Salida técnica | Resultado para el cliente |
|-----------|----------------|---------------------------|
| Persistencia en Neon (base) | Tablas de estado + acceso | Estado que no depende de la vida del proceso |
| Durabilidad de tareas | Estado de tarea consultable tras reinicio | El sync no "desaparece"; menos tareas huérfanas que diagnosticar |
| Durabilidad de sesiones | Sesión Futmondo recuperable tras reinicio | Menos cortes de sesión inesperados |
| Mensaje de acción clara | Respuesta con re-login/reintento | El usuario sabe qué hacer, en vez de un 403 opaco |
| Credenciales FR5 | Contraseña no en claro | Se elimina el riesgo de exponer credenciales |

## Criterios de éxito (del intent)

- Tras un reinicio de Fly, una tarea de sync se consulta y refleja su último estado conocido. [desc]
- Tras un reinicio, el usuario recibe una acción clara (re-login/reintento) en vez de un 403 opaco. [desc]
- La contraseña Futmondo no está almacenada en claro en el estado del proceso. [desc]
- La suite de tests existente sigue en verde. [desc]

## Assumptions & Open Questions

- [assumption] Neon (tier free) admite las tablas nuevas de estado sin acercarse a los límites del tier, dado el volumen actual (uso personal/grupo reducido). [Q1] [memory:M1]
- La elección concreta de FR5 (re-auth vs. cifrado en reposo) queda abierta y se decide en la etapa de diseño. [Q3]
