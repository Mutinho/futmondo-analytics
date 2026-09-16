# Intent Backlog — Durabilidad del estado y credenciales Futmondo

> Backlog priorizado de proto-Units (candidatos a Unidades de Trabajo).
> Priorización MoSCoW; orden de construcción dependency-first. Deriva de
> scope-document.md y de las respuestas Q1–Q5 confirmadas.

## Sources

- scope-document.md — capacidades IN/OUT, secuenciación [scope]
- scope-definition-questions.md — Q1–Q5 confirmadas [Q1] [Q2] [Q3] [Q4] [Q5]
- feasibility-assessment.md — viabilidad a coste 0 € en Neon [Q1]

## Método de priorización

- **Marco**: MoSCoW (must / should / could / won't-this-time).
- **Orden de construcción**: dependency-first — la capa de persistencia habilita
  al resto de proto-Units. [Q4]

## Proto-Units (backlog priorizado)

| Orden | Proto-Unit | Descripción | MoSCoW | Depende de | Trazabilidad |
|-------|-----------|-------------|--------|-----------|--------------|
| 1 | PU-1 · Capa de persistencia de estado en Neon | Esquema (tablas nuevas para tareas y sesiones) y acceso a estado desde el backend; base común del resto | Must | — | FR1, C-T2 [Q4] |
| 2 | PU-2 · Durabilidad de tareas de sync | Persistir/leer el estado de las tareas de `TaskManager` en Neon; consultable tras reinicio con su último estado conocido | Must | PU-1 | FR1 (cap. 1) [Q2] |
| 3 | PU-3 · Durabilidad de sesiones Futmondo | Persistir/leer las sesiones de `SessionStore` en Neon, preservando TTL (12h) y locks de concurrencia por usuario | Must | PU-1 | FR1, C-T3 (cap. 2) [Q2] |
| 4 | PU-4 · Acción clara ante sesión no disponible | Sustituir el 403 opaco por una respuesta con acción (re-login/reintento) cuando la sesión no esté presente tras un reinicio | Must | PU-3 | FR1 métrica (cap. 3) [Q2] |
| 5 | PU-5 · Tratamiento de credenciales (FR5) | Eliminar la contraseña en claro; vía concreta (re-auth vs. cifrado en reposo) a decidir en diseño, ambas coste 0 € | Must | PU-1, PU-3 | FR5 (cap. 4) [Q3] |
| 6 | PU-6 · Housekeeping de estado | Limpieza/expiración de tareas y sesiones antiguas en la BD | Should | PU-1, PU-2, PU-3 | FR1 (cap. 5) [Q2] |
| — | PU-7 · Reanudación automática de tareas | Re-lanzar automáticamente tareas interrumpidas por el reinicio | Won't (this time) | PU-2 | FR1 (cap. 6); OUT por Q5 [Q5] |

## Definición de MVP

El MVP lo componen las proto-Units **Must-have**: PU-1, PU-2, PU-3, PU-4 y PU-5.
Cumplen las cuatro métricas de éxito del intent (estado que sobrevive al
reinicio, acción clara en vez de 403, contraseña no en claro) y mantienen verde
la suite de tests existente. PU-6 es deseable (Should) y PU-7 queda fuera de
esta entrega (Won't-this-time). [Q2] [Q5]

## Cobertura de trazabilidad

- **FR1** → PU-1, PU-2, PU-3, PU-4 (y PU-6 higiene; PU-7 diferida). 
- **FR5** → PU-5.

Todas las proto-Units trazan a un hallazgo del intent (FR1 o FR5); no hay
proto-Units huérfanas ni requisitos del alcance sin cobertura.

## Assumptions & Open Questions

- [assumption] La elección de FR5 en PU-5 (re-auth vs. cifrado en reposo) se
  concreta en diseño; no altera la prioridad Must ni el orden del backlog. [Q3]
