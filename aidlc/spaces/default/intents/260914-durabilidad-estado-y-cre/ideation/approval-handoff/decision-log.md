# Decision Log — Durabilidad del estado y credenciales Futmondo

> Registro de las decisiones tomadas durante la fase de Ideación (scope `feature`).

## Sources

- Artefactos de intent-capture, feasibility, scope-definition y approval-handoff [desc] [scope]

## Decisiones

| # | Decisión | Etapa | Fecha |
|---|----------|-------|-------|
| D1 | Abordar FR1 y FR5 juntos en un mismo intent, por compartir el estado en memoria de `SessionStore`/`TaskManager` | intent-capture | 2026-09-14 |
| D2 | Persistir el estado (tareas y sesiones) en Neon PostgreSQL, sin infraestructura nueva ni gasto recurrente | feasibility | 2026-09-14 |
| D3 | Alcance = FR1 + FR5 completos (durabilidad de tareas y sesiones + tratamiento de credenciales) | scope-definition | 2026-09-15 |
| D4 | Must-have: persistir tareas, persistir sesiones, mensaje de acción clara, contraseña no en claro. Nice-to-have: housekeeping, reanudación automática | scope-definition | 2026-09-15 |
| D5 | Elección concreta de FR5 (re-auth vs. cifrado en reposo) diferida a la etapa de diseño; ambas vías coste 0 € | scope-definition | 2026-09-15 |
| D6 | Secuenciación dependency-first: capa de persistencia en Neon primero, luego tareas, sesiones y credenciales | scope-definition | 2026-09-15 |
| D7 | Reanudación automática de tareas declarada fuera de alcance en esta entrega (solo se persiste el estado) | scope-definition | 2026-09-15 |
| D8 | Go/no-go = GO: proceder a la fase de Inception | approval-handoff | 2026-09-15 |

## Restricciones vigentes (recordatorio)

- C-O1: coste 0 € — solo soluciones sostenibles en tiers gratuitos. [memory:M1]
- C-T1: mantener el stack actual sin reescrituras grandes. [desc]
- C-T3: preservar TTL (12h) y locks de concurrencia por usuario. [Q5]

## Assumptions & Open Questions

None.
