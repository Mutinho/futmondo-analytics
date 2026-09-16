# Initiative Brief — Durabilidad del estado y credenciales Futmondo

> Compilación de la fase de Ideación (scope `feature`). Agrega intent, alcance,
> feasibility, restricciones y stakeholders en un one-pager para el gate de
> traspaso a Inception.

## Sources

- intent-statement.md, stakeholder-map.md [desc]
- scope-document.md, intent-backlog.md [scope]
- feasibility-assessment.md, constraint-register.md [Q1]
- approval-handoff-questions.md (Q1–Q3 confirmadas) [Q1] [Q2] [Q3]

## Intent y problema

Dos piezas de estado crítico del backend viven solo en la memoria del proceso y
convergen en el mismo componente (`SessionStore`/`TaskManager`): [desc]

- **FR1 — Durabilidad**: un reinicio de la máquina Fly pierde las tareas de sync
  en curso y las sesiones Futmondo, provocando 403 opacos y tareas huérfanas.
- **FR5 — Credenciales**: la contraseña Futmondo se guarda en claro en la
  memoria del proceso.

Se abordan juntos porque comparten el estado en memoria, reutilizando un único
diseño de persistencia. Son los dos hallazgos "Crítico" del plan de mejoras
`260911-analisis-mejoras`. [desc]

## Validación de mercado

No aplica: proyecto de un único propietario-desarrollador, deuda técnica
priorizada internamente; no se ejecutó market-research (fuera del scope
`feature`). [Q6]

## Feasibility y riesgos

Viable dentro del stack actual y a coste 0 € (persistencia en Neon, ya presente).
Riesgos reconocidos con mitigación aceptada: [Q1] [Q2]

| Riesgo | Nivel | Mitigación |
|--------|-------|------------|
| Persistencia de sesiones con TTL (12h) y concurrencia | Moderado | Preservar los locks por usuario y el TTL ya existentes al mover el estado a BD |
| Migración de esquema en Neon | Bajo-moderado | Añadir tablas nuevas sin tocar las existentes |
| Trade-off FR5 (re-auth vs. cifrado) | Bajo | Decisión concreta en la etapa de diseño; ambas vías coste 0 € |

## Límite de alcance

- **Dentro**: durabilidad de tareas y sesiones en Neon, mensaje de acción clara
  en vez de 403, y eliminación de la contraseña en claro (FR1 + FR5 completos).
- **Fuera**: reescrituras grandes, cambios de stack, coste recurrente y la
  reanudación automática de tareas (solo se persiste el estado). [scope] [Q5]

MVP = proto-Units PU-1..PU-5 (Must). PU-6 housekeeping (Should); PU-7
reanudación automática (Won't-this-time). [scope]

## Visuales de concepto

No aplica: cambio de backend sin superficie nueva de UI; no se ejecutó
rough-mockups (fuera del scope `feature`). [Q6]

## Plan de equipo

No aplica: un único propietario-desarrollador; sin mobs que dotar ni
team-formation (fuera del scope `feature`). El decisor de alcance y prioridad es
el propietario, vía los gates de aprobación. [Q6] [Q7]

## Recomendación go/no-go

**GO — proceder a la fase de Inception.** Alcance acotado, coste 0 €, dentro del
stack actual, riesgos reconocidos y cuatro métricas de éxito medibles. Aprobado
por el propietario en el gate (Q3 = GO). [Q3]

## Criterios de éxito

- Tras un reinicio de Fly, una tarea de sync se consulta y refleja su último estado conocido. [desc]
- Tras un reinicio, el usuario recibe una acción clara (re-login/reintento) en vez de un 403 opaco. [desc]
- La contraseña Futmondo no está almacenada en claro en el estado del proceso. [desc]
- La suite de tests existente sigue en verde. [desc]

## Assumptions & Open Questions

- [assumption] Neon (tier free) admite las tablas nuevas de estado sin acercarse a los límites del tier. [Q1] [memory:M1]
- La elección concreta de FR5 (re-auth vs. cifrado en reposo) se decide en Inception/diseño. [Q3]
