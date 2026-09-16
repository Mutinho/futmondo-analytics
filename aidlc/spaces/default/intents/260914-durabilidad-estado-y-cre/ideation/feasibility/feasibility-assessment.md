# Feasibility Assessment — Durabilidad del estado y credenciales Futmondo

## Viabilidad técnica

La solución es viable dentro del stack actual y a coste 0 €: [Q1] [Q4] [memory:M1]

- **FR1 (durabilidad)**: persistir el estado de tareas de sync (`TaskManager`) y de sesiones Futmondo (`SessionStore`) en Neon PostgreSQL, ya presente en el stack, mediante tablas nuevas; no requiere infraestructura adicional ni gasto recurrente. Tras un reinicio, el estado se lee de la BD en vez de perderse con el proceso. [Q1] [desc]
- **FR5 (credenciales)**: eliminar el almacenamiento en claro de la contraseña Futmondo. Dos direcciones viables, ambas coste 0 €, a decidir en diseño: (A) evitar guardar la contraseña rediseñando hacia re-auth/token bajo demanda; (B) cifrar la contraseña en reposo con una clave de entorno gestionada como secret de Fly.io. [Q3] [desc]

No hay reescrituras grandes: ambos cambios se localizan en `backend/app/auth/session_store.py`, `backend/app/services/task_manager.py` y sus consumidores, más una migración de esquema en Neon. [desc]

## Análisis de riesgo

- Riesgo moderado en la persistencia de sesiones con TTL (12h) y en la concurrencia (ya existen locks por usuario en `SessionStore`); ambos deben preservarse al mover el estado a BD. [Q5] [desc]
- Riesgo bajo-moderado en la migración de esquema en Neon (añadir tablas nuevas, sin tocar las existentes). [Q5] [Q1]
- Para FR5, el enfoque de re-auth (A) puede impactar la UX si obliga a re-login más a menudo; el de cifrado (B) mantiene la UX pero introduce gestión de clave. Se evalúa en diseño. [Q3]

## Cumplimiento

No hay requisitos regulatorios formales aplicables; rige la buena práctica de seguridad de no almacenar secretos en claro. [Q2]

## Assumptions & Open Questions

- [assumption] Se asume que Neon (tier free) admite las tablas nuevas de estado sin acercarse a los límites del tier, dado el volumen actual (uso personal/grupo reducido). [Q1] [memory:M1]
- La elección concreta para FR5 (re-auth vs cifrado en reposo) queda abierta y se decidirá en la etapa de diseño. [Q3]
