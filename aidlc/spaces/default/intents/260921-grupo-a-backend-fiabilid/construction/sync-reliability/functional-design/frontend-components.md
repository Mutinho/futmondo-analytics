# Componentes de frontend — U1 sync-reliability

> Conversation language: Spanish.

## No aplica

Este intent es **backend-only**. No introduce ni modifica componentes de frontend.
La validación de `price` del frontend ya existe y no se toca; el estado `degraded`
de un paso es consumible por el frontend existente vía `progress[step].status` sin
cambios de contrato (el frontend actual muestra el progreso paso a paso).

## Sources

- `inception/scope-definition/scope-document.md` (OUT: frontend).

## Assumptions & Open Questions

None.
