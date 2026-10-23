# Incident Plan — F2 (Incident Response)

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Alcance

F2 añade una capa de app cliente; **no introduce incidentes de servidor** (no despliega backend). Los "incidentes" posibles son locales (build/firma/datos) y se cubren con los runbooks R1–R3. No hay P1/P2 de producción atribuibles a F2 por sí mismo.

## Severidad y respuesta

- **Bajo**: regresión visual o firma caducada → runbook R1/R2, resolución local inmediata.
- **Dependiente del backend**: error de datos → la app degrada con Reintentar; la causa (si es de servidor) se trata en el backend, fuera de F2.
- **Post-incidente**: para cualquier incidente real de producción del backend sigue vigente su propio proceso (no cambia por F2).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/operation/incident-response/runbooks.md`

## Assumptions & Open Questions

None.
