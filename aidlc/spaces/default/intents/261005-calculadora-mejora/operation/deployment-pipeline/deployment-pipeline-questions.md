# Deployment Pipeline — Preguntas (calculadora-mejora)

Contexto: el proyecto ya está **en producción** con un pipeline Fly.io maduro
(on-merge a `main`, región `cdg`, dos apps, smoke test `/health`) y un gate de
CI bloqueante operativo. Este cambio es **frontend-only** y no cambia la
topología ni el orden de despliegue. Las etapas CI Pipeline e Infrastructure
Design están SKIP por scope `refactor`. Por tanto, esta etapa **documenta** el
pipeline de despliegue existente aplicado a este cambio, adaptado a Fly.io
(coste 0 €), no crea uno nuevo.

> Opciones A-E o `X. Other`. La mayoría ya están fijadas por práctica afirmada;
> confírmalas o corrígelas.

## Q1 — Estrategia de despliegue para este cambio

- A. La actual: on-merge a `main` → Fly.io (sin staging), con smoke test `/health` como verificación de release. Sin blue/green ni canary (no aplican al tier free / topología actual).
- B. Introducir una estrategia nueva (blue/green, canary) para este cambio.
- X. Other (please specify)

[Answer]: A — Mantener la estrategia actual (on-merge a `main` → Fly.io, smoke test `/health`); este cambio frontend-only no justifica introducir blue/green ni canary, y saldría del tier free (coste 0 €).

## Q2 — Rollback

- A. El actual: redeploy de la release anterior en Fly.io (`fly releases rollback`), runbook en `docs/ROLLBACK.md`. El toggle no toca backend ni datos, así que el rollback frontend es un simple redeploy.
- B. Procedimiento de rollback nuevo/ampliado.
- X. Other (please specify)

[Answer]: A — Rollback por redeploy de la release anterior (Fly.io), sin migraciones ni cambios de datos que revertir (frontend-only). `docs/ROLLBACK.md` sigue vigente.

## Q3 — Gates de promoción / aprobación a producción

- A. Los actuales: gate de CI bloqueante (`gitleaks` + `pytest` + `ng test`) en PR y en el job `verify` de push a `main`; el merge a `main` dispara el deploy. Sin entorno de staging separado.
- B. Añadir una aprobación manual extra a producción para este cambio.
- X. Other (please specify)

[Answer]: A — Gates actuales (CI bloqueante en PR + `verify` en push); on-merge despliega. Sin aprobación manual extra para un cambio frontend acotado.

---

## Consolidated Summary Confirmation

- **Estrategia**: on-merge a `main` → Fly.io (región `cdg`), sin staging; smoke test `/health` (5 reintentos, HTTP 200) como verificación de release. Sin blue/green ni canary (coste 0 €, topología actual).
- **Rollback**: redeploy de la release anterior en Fly.io (`fly releases rollback`); runbook `docs/ROLLBACK.md`. Frontend-only: sin migraciones ni datos que revertir.
- **Gates**: CI bloqueante (`gitleaks` + `pytest` + `ng test`) en PR y en el job `verify` de push a `main`; on-merge despliega. Sin aprobación manual extra.
- **Alcance**: esta etapa DOCUMENTA el pipeline existente aplicado a este cambio frontend; no crea pipeline nuevo. CI Pipeline e Infrastructure Design SKIP por scope.

Does this all look correct before I generate the artifacts?

- Looks correct
- Request changes

[Answer]: Looks correct
