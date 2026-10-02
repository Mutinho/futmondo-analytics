# Deployment Pipeline — Preguntas

> Intent `261001-sync-god-file-resto` (scope `refactor`, Minimal). Sistema ya en
> producción con pipeline Fly.io maduro. Idioma: castellano.

## Q1 — Impacto del refactor en el pipeline de despliegue

El refactor del dominio `clauses` es equivalencia funcional estricta: código
Python nuevo bajo `backend/app/services/sync/clauses/`, sin dependencias nuevas,
sin cambios de esquema, sin cambios de API ni de superficie pública. El pipeline
CD existente (`.github/workflows/fly-deploy.yml`: cadena `verify` → `deploy-backend`
→ `deploy-frontend` → `smoke-test` `/health` sobre Fly.io región `cdg`) ya cubre
este cambio. ¿Qué hacemos con el pipeline de despliegue?

- A. **No cambiar nada**: el pipeline CD existente despliega este refactor sin
  modificación (el gate `verify` corre pytest/cobertura/lint/audits y el smoke
  test `/health` verifica el release). Sólo se documenta el pipeline vigente, la
  estrategia de despliegue y el runbook de rollback existentes, confirmando que
  cubren el cambio.
- B. Introducir un cambio en el pipeline de despliegue (especificar).
- X. Other (please specify)

[Answer]: A — no cambiar nada; el pipeline CD existente cubre el refactor. Documentar el pipeline vigente, la estrategia de despliegue y el runbook de rollback.

## Consolidated Summary Confirmation

Resumen de la decisión:

- Q1 — No se modifica el pipeline de despliegue. El CD existente
  (`fly-deploy.yml`: `verify` → `deploy-backend` → `deploy-frontend` →
  `smoke-test /health`, Fly.io región `cdg`) despliega este refactor de
  equivalencia estricta sin cambios. Se documentan el pipeline vigente, la
  estrategia de despliegue y el runbook de rollback, confirmando que cubren el
  cambio. No se reordena la cadena `needs:`.

Does this all look correct before I generate the artifacts?

- Looks correct
- Request changes

[Answer]: Looks correct
