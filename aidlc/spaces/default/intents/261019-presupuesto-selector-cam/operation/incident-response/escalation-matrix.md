# Escalation Matrix — F2 (Incident Response)

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

**Single-maintainer, sin on-call.** No hay cadena de escalado entre personas: el propietario es el único responsable y resuelve los runbooks R1–R3 directamente.

| Situación | Responsable | Acción |
|-----------|-------------|--------|
| Regresión app / firma caducada | Propietario | Runbook R1 / R2 (revert + reinstalar / refirmar) |
| Error de datos (backend) | Propietario | Reintentar en la app; si persiste, revisar backend por sus medios |
| Incidente de producción backend | Propietario | Proceso del backend existente (no cambia por F2) |

Sin contactos/guardias externos (coste 0 €, un solo mantenedor).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/operation/incident-response/incident-plan.md`
- [memory] single-maintainer (team-formation)

## Assumptions & Open Questions

None.
