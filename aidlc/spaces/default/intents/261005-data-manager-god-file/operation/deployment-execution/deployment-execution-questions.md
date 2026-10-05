# Deployment Execution — Questions

> Scope `refactor` (equivalencia) · stack Fly.io on-merge. **El deploy a
> producción lo dispara el merge a `main`** vía `fly-deploy.yml` (cadena
> `verify → deploy-backend → deploy-frontend → smoke-test`), NO un comando
> manual desde esta etapa. El código del refactor aún está en el working tree,
> sin commitear/mergear. Por tanto esta etapa **documenta** el procedimiento de
> ejecución on-merge y la verificación de salud esperada; no realiza un deploy
> manual a producción (sería alto impacto + bypass del gate). Respuestas
> fundamentadas en el workspace; confirma o corrige.

## Q1 — ¿Pasan todos los pre-deployment checks?

Recomendado: **Sí**. La suite completa está verde localmente (414 passed /
3 xfailed, cobertura 57.48%, piso 27 sostenido — ver Build and Test). El
gate `verify` on-merge re-ejecutará gitleaks + pip-audit + ruff + pytest con
cobertura + npm audit + ng test antes de cualquier deploy.

[Answer]: A. Sí — suite verde local; el gate verify re-valida on-merge

## Q2 — ¿Se requieren migraciones de BD y están testeadas?

Recomendado: **No se requieren**. Equivalencia estricta: el esquema de Neon y
los DTOs no cambian; el SQL se mueve verbatim. No hay migración que ejecutar.

[Answer]: A. No se requieren migraciones (sin cambio de esquema)

## Q3 — ¿Están disponibles y sanos los servicios dependientes?

Recomendado: **Sí** (sin cambios). Backend `futmondo-api` (`/health`), frontend
`futmondo-app` (`/`), Neon PostgreSQL (Frankfurt). El refactor no cambia
integraciones externas (Futmondo/Sofascore) ni su cliente.

[Answer]: A. Sí — dependencias sin cambios; health checks existentes

## Q4 — ¿Cuál es la ventana de despliegue?

Recomendado: **on-merge** (deploy-on-merge a `main`, single-maintainer, sin
ventana formal ni freeze). El gate bloqueante es la salvaguarda.

[Answer]: A. On-merge a main (sin ventana formal; gate como salvaguarda)

## Q5 — ¿Ejecución del deploy ahora o documentada on-merge?

Recomendado: **documentada on-merge**. No disparo `flyctl deploy` manual desde
aquí: el deploy real sucede cuando se abre el PR del refactor y se fusiona a
`main` con el gate en verde (nunca push directo a `main`; un rojo nunca llega a
producción). Esta etapa registra el procedimiento y el resultado de salud
esperado del smoke `/health`.

[Answer]: A. Documentar la ejecución on-merge (sin deploy manual a producción)

## Consolidated Summary Confirmation

Resumen de lo que se generará (ejecución documentada on-merge; sin deploy manual
a producción ni commit/merge por mi parte):

- **deployment-log.md**: procedimiento de ejecución on-merge (abrir PR del
  refactor → gate `verify` en verde → merge squash a `main` → `fly-deploy.yml`
  despliega backend y frontend → smoke `/health`); estado actual = pendiente de
  merge; sin migraciones de BD; rollback quirúrgico por commit de módulo.
- **smoke-test-results.md**: el smoke `/health` esperado (5 reintentos, HTTP 200,
  `{"status":"healthy"}`) que `fly-deploy.yml` ejecuta tras el deploy; se marca
  como el criterio de verificación de release, pendiente de ejecución on-merge.
- **health-check-report.md**: checks existentes (backend `/health`, frontend `/`,
  Neon) sin cambios; equivalencia estricta ⇒ comportamiento observable nulo.

[Answer]: Looks correct

