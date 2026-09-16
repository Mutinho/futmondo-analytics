# Intent Statement — Durabilidad del estado y credenciales Futmondo

## Problem Statement

El backend de futmondo-analytics mantiene dos piezas de estado críticas solo en la memoria del proceso, y ambas convergen en el mismo componente: [Q1] [desc]

- Las tareas de sync asíncronas (`TaskManager`) y las sesiones Futmondo por usuario (`SessionStore`) viven en diccionarios en memoria; un reinicio de la máquina Fly pierde las tareas en curso y las sesiones, provocando 403 opacos ("sesión expirada") y tareas huérfanas (FR1). [Q1] [desc]
- Las credenciales Futmondo del usuario (email + password) se almacenan en claro en la memoria del proceso dentro de la sesión (FR5). [Q1] [desc]

Se abordan juntas porque comparten el estado en memoria de `SessionStore`/`TaskManager`, de modo que atacarlas en un mismo intent evita duplicar el diseño de persistencia. [Q1]

## Target Customer

- El usuario final de la PWA se beneficia de un sync que sobrevive a reinicios y de mensajes de acción claros (re-login/reintento) en lugar de un 403 sin contexto. [Q2] [desc]
- El propietario/operador del proyecto se beneficia de eliminar el riesgo de exponer credenciales en claro y de reducir las tareas huérfanas que hay que diagnosticar. [Q2] [desc]

## Success Metrics

El intent se considera logrado cuando se cumplen de forma medible todos estos criterios: [Q3] [desc]

- Tras un reinicio de la máquina Fly, una tarea de sync puede consultarse y refleja su último estado conocido (no desaparece). [Q3] [desc]
- Tras un reinicio, el usuario recibe una acción clara (re-login/reintento) en lugar de un 403 opaco. [Q3] [desc]
- La contraseña Futmondo no está almacenada en claro en el estado del proceso (se evita guardarla, se cifra, o se sustituye por token/re-auth). [Q3] [desc]
- La suite de tests existente sigue en verde. [Q3]

## Initiative Trigger

Deuda técnica priorizada: FR1 y FR5 son los dos hallazgos de prioridad "Crítico" del plan de mejoras producido en el intent `260911-analisis-mejoras`. [Q4] [desc]

## Initial Scope Signal

- **Workflow-selected scope**: `feature`. [scope]
- **Límite de producto confirmado por el usuario**: implementar FR1 y FR5 juntos, con diseño + implementación + tests, sin reescrituras grandes y a coste 0 € (soluciones sostenibles en tiers gratuitos). [Q8] [memory:M1]

## Assumptions & Open Questions

None.
