# RAID Log — Durabilidad del estado y credenciales Futmondo

## Risks

| ID | Riesgo | Mitigación | Source |
|----|--------|-----------|--------|
| R1 | Al mover sesiones a BD se rompe el TTL de 12h o la re-autenticación automática | Preservar la lógica de TTL/re-auth en el diseño; cubrir con tests | [Q5] [desc] |
| R2 | Concurrencia: perder la protección de los locks por usuario al persistir estado | Mantener el bloqueo por usuario; validar acceso concurrente en tests | [Q5] [desc] |
| R3 | Migración de esquema en Neon con impacto en datos existentes | Solo añadir tablas nuevas; no tocar las existentes; migración idempotente | [Q5] [Q1] |
| R4 | Para FR5, el enfoque de re-auth degrada la UX (re-login frecuente) | Evaluar en diseño frente al cifrado en reposo; elegir por impacto UX/complejidad | [Q3] |
| R5 | Superar límites del tier free de Neon con las tablas nuevas | Volumen actual bajo (uso personal); monitorizar; diseño ligero de tablas | [Q1] [memory:M1] |

## Assumptions

| ID | Asunción | Source |
|----|----------|--------|
| A1 | Neon (tier free) admite las tablas nuevas de estado sin acercarse a sus límites al volumen actual | [Q1] [memory:M1] |
| A2 | El endurecimiento de seguridad ya presente (JWT, refresh HttpOnly, etc.) se mantiene | [desc] |

## Issues

| ID | Incidencia | Source |
|----|-----------|--------|
| I1 | La dirección concreta para FR5 (re-auth vs cifrado en reposo) está sin decidir; se resuelve en diseño | [Q3] |

## Dependencies

| ID | Dependencia | Source |
|----|-------------|--------|
| D1 | Neon PostgreSQL disponible y con capacidad de esquema (ya en producción) | [Q1] |
| D2 | Gestión de secrets de Fly.io para la clave de cifrado, si se elige el enfoque B de FR5 | [Q3] |

## Assumptions & Open Questions

None.
