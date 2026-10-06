# Deployment Execution — Preguntas pre-despliegue (calculadora-mejora)

Contexto: el despliegue a producción es **on-merge a `main`** (GitHub Actions →
Fly.io). El cambio de código **aún no está commiteado/merged**; esta etapa
confirma que todo está listo para desplegar y documenta el procedimiento y la
verificación (smoke test `/health`). El deploy real lo dispara el merge a `main`.

## Q1 — ¿Pasan todos los checks pre-despliegue?

- A. Sí: `ng test` 75/75 en verde (contenedor `node:22.22.3`), cobertura por encima de umbrales, build OK; el gate de CI (gitleaks + pytest + ng test) se re-ejecutará en PR y en `verify` al mergear.
- B. No / con reservas (detallar).
- X. Other (please specify)

[Answer]: A — Checks locales en verde (75/75, cobertura ≥ umbrales, build OK). El gate bloqueante se re-valida en el PR y en el job `verify` del push a `main` antes del deploy.

## Q2 — ¿Se requieren migraciones de base de datos?

- A. No: cambio frontend-only, sin esquema ni datos.
- B. Sí (detallar).
- X. Other (please specify)

[Answer]: A — No. Cambio puramente de UI (Angular); no hay migraciones ni cambios de datos.

## Q3 — Servicios dependientes y ventana de despliegue

- A. Sin dependencias nuevas; servicios actuales (Futmondo/Sofascore, Neon) sin cambios. Sin ventana formal (single-maintainer); on-merge continuo con smoke test `/health` como verificación.
- B. Hay dependencias/ventana a considerar (detallar).
- X. Other (please specify)

[Answer]: A — Sin dependencias nuevas ni ventana formal; on-merge continuo, smoke test `/health` verifica el release.

---

## Consolidated Summary Confirmation

- **Readiness**: `ng test` 75/75 en verde, cobertura ≥ umbrales, build OK. El gate de CI (gitleaks + pytest + ng test) se re-valida en PR y en el job `verify` del push a `main`.
- **Migraciones**: ninguna (frontend-only).
- **Dependencias/ventana**: sin dependencias nuevas; on-merge continuo; smoke test `/health` (5 reintentos, HTTP 200) verifica el release.
- **Mecanismo de deploy**: on-merge a `main` → GitHub Actions → Fly.io (`deploy-frontend` publica el bundle). El código aún no está mergeado; el deploy real lo dispara el merge (acción del humano).

Does this all look correct before I generate the artifacts?

- Looks correct
- Request changes

[Answer]: Looks correct
