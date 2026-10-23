# Runbooks — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés. Adaptado al stack real (single-maintainer, coste 0 €).

## Alcance

La capa de diseño es cliente iOS, no un servicio en producción. No hay incidentes operativos de servidor atribuibles a este intent. Los únicos "incidentes" plausibles son de **cliente** (regresión visual o funcional del login tras revestir), detectables en el dispositivo, no por telemetría.

## Runbook R1 — Regresión del login revestido

- **Síntoma**: el login no funciona como F1 (p. ej. no permite enviar, foco roto, error mal mostrado) o se ve incorrecto tras revestir.
- **Diagnóstico**: reproducir en el iPhone 13 Pro; comparar con el comportamiento de F1.
- **Remedio**: revertir con `git revert <sha del intent>` y reinstalar la build anterior con `xtool` (ver `operation/deployment-pipeline/rollback-runbook.md`). El `AuthViewModel`/auth de F1 no se tocó, así que el reverso restaura el login funcional.
- **Prevención**: validación en dispositivo antes de dar por buena la instalación (riesgo abierto de la cadena de foco anotado en U2).

## Runbook R2 — Caducidad de firma (~7 días)

- **Síntoma**: la app deja de abrir en el dispositivo (firma gratuita caducada).
- **Remedio**: reinstalar/refirmar con `cd ios && xtool dev build` (deuda B-09 conocida; coste 0 €).

## Producción (heredado)

Incidentes de backend/frontend producción se gobiernan por el runbook heredado (`docs/ROLLBACK.md`, redeploy Fly.io), no afectado por este intent.

## Assumptions & Open Questions

None.
