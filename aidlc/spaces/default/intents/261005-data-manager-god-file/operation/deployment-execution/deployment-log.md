# Deployment Execution Log — refactor `data_manager_v2`

Scope `refactor` (equivalencia) · stack Fly.io on-merge · coste 0 €. El deploy a
producción se dispara **on-merge** a `main` (nunca push directo); esta etapa
documenta el procedimiento y su estado, sin deploy manual.

## Estado actual

**Pendiente de merge.** El código del refactor (14 módulos DDD extraídos +
fachada adelgazada + 14 tests de caracterización) está en el working tree,
verificado en verde localmente (Build and Test). El deploy ocurrirá cuando el PR
se abra y se fusione a `main` con el gate en verde.

## Procedimiento de ejecución (on-merge)

1. **Abrir PR** del refactor hacia `main` (rama corta con prefijo, p. ej.
   `refactor/data-manager-god-file`). Conventional Commits en castellano, scope
   `backend`/`refactor`. Idealmente los 14 commits aislados por módulo se
   preservan en la rama; el squash-merge aterriza como un commit sobre `main`
   (o, si se prefiere trazabilidad por módulo, merge no-ff — decisión de merge
   del equipo; la base afirmada es squash).
2. **Gate de PR (`ci.yml`, job `quality`)** — required status check: gitleaks +
   ruff + pytest con cobertura + pip-audit + ng test + npm audit. Debe pasar
   antes de fusionar.
3. **Merge a `main`** → dispara `fly-deploy.yml`:
   - `verify` (re-ejecuta el gate completo, paridad con el PR).
   - `deploy-backend` → `flyctl deploy` app `futmondo-api`.
   - `deploy-frontend` → `flyctl deploy` app `futmondo-app`.
   - `smoke-test` → `curl /health` (5 reintentos, HTTP 200).
4. **Verificación de release**: el smoke `/health` es la verificación (sin
   staging). Verde ⇒ release OK. Rojo ⇒ rollback (ver abajo).

## Migraciones de BD

**Ninguna.** Equivalencia estricta: el esquema de Neon y los DTOs no cambian; el
SQL se movió verbatim a los adapters. No hay paso de migración.

## Rollback

Según `operation/deployment-pipeline/rollback-runbook.md`: `fly releases
rollback <vN>` (o redeploy de la imagen previa) + verificación `/health`.
Rollback quirúrgico: `git revert` del commit de un módulo concreto si la
regresión se localiza en una responsabilidad.

## Decisión de no-deploy-manual (registrada)

No se ejecutó `flyctl deploy` manual desde esta etapa: hacerlo desplegaría
código no fusionado, saltando el merge-gate de CI y violando "nunca push directo
a `main`". El deploy es responsabilidad del pipeline on-merge. Esta es una acción
de alto impacto sobre producción reservada al flujo gateado.
