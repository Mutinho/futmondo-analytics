# Incident Response — Preguntas

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés. Sin decisiones nuevas.

## Consolidated Summary Confirmation

Resumen de Incident Response:

- **Sin incidentes de servidor nuevos**: la capa de diseño es cliente iOS; no puede tumbar producción.
- **Runbooks**: R1 (regresión del login revestido → `git revert` + reinstalar con `xtool`), R2 (caducidad de firma ~7 días → refirmar).
- **Escalado**: single-maintainer, sin on-call de pago; el propietario es el único responsable.
- **Producción heredada** (`docs/ROLLBACK.md`, Fly.io): no afectada.

¿Does this all look correct?

[Answer]: Looks correct
