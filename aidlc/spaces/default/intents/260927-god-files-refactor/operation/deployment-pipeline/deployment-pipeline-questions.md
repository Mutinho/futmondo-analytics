# Preguntas — Deployment Pipeline (Oleada 1: analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, depth Minimal, brownfield. Conversation language: Spanish.
>
> El pipeline CD (`fly-deploy.yml`), la estrategia de deploy y el runbook de rollback (`docs/ROLLBACK.md`) **ya existen y están maduros en producción**. Esta oleada de refactor **preserva el comportamiento** y NO cambia topología, orden de deploy ni crons (regla afirmada). Las preguntas se limitan a confirmar ese encuadre; no hay CD nuevo que diseñar.

## Q1 — Encuadre del deploy para esta oleada

Dado que el CD Fly.io existente (verify → deploy-backend → deploy-frontend → smoke-test `/health`) no cambia con esta extracción, ¿el enfoque es documentar la estrategia/rollback existentes aplicados a la Oleada 1, sin modificar workflows?

- A. Sí — documentar el CD existente aplicado a esta oleada; no tocar `fly-deploy.yml` ni crons.
- B. No — proponer cambios en el pipeline CD como parte de esta oleada.
- X. Other (please specify)

[Answer]: A

## Q2 — Verificación de release

La verificación de release es el smoke test contra `/health` (5 reintentos, HTTP 200), sin staging separado. ¿Se mantiene como verificación de release para esta oleada?

- A. Sí — el smoke test `/health` existente es la verificación de release.
- B. No — añadir verificación adicional específica de esta oleada.
- X. Other (please specify)

[Answer]: A

## Q3 — Rollback

El rollback es manual vía redeploy de la release previa en Fly.io (`docs/ROLLBACK.md`). ¿Sigue siendo el procedimiento para esta oleada?

- A. Sí — `docs/ROLLBACK.md` (fly releases rollback / redeploy imagen previa) es el procedimiento vigente.
- B. No — definir un rollback distinto.
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
