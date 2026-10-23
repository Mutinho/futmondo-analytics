# Incident Plan — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Clasificación (proyecto personal, single-maintainer)

| Severidad | Ejemplo | Respuesta |
|-----------|---------|-----------|
| P1/P2 (producción) | No aplica a este intent: la capa de diseño es cliente; no puede tumbar el backend/frontend producción. | — (gobernado por el runbook heredado si ocurriera por otra causa) |
| P3 cliente | Regresión del login revestido o fallo visual en el dispositivo | Runbook R1: revertir + reinstalar |
| P4 fricción | Caducidad de firma ~7 días | Runbook R2: refirmar |

## Post-incidente

Para un proyecto personal single-maintainer no hay proceso formal de post-mortem; si una regresión del login llega al dispositivo, se anota la causa (p. ej. cadena de foco del `TextInputField`) como aprendizaje y se corrige. No hay P1/P2 de servidor atribuibles a este intent.

## Assumptions & Open Questions

None.
