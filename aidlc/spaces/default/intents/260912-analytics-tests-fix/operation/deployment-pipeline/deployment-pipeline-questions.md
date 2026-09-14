# Deployment Pipeline — Preguntas de Clarificación

Contexto: bugfix brownfield. El pipeline de CD ya existe
(`.github/workflows/fly-deploy.yml`: verify → deploy backend → deploy frontend →
smoke `/health`). Este cambio solo toca un fichero de test; desbloquea el gate
`verify` (pytest) sin alterar el comportamiento de la app.

## Q1: Ruta de despliegue de este cambio

¿Cómo debe llegar este arreglo a producción?

- A. Por el pipeline existente sin cambios: merge a `main` → `fly-deploy.yml` ejecuta verify (pytest+ng test) → deploy backend/frontend → smoke `/health`. Recomendado (no requiere tocar el pipeline).
- B. Igual que A pero además ajustar/añadir algo en el pipeline (especificar qué).
- X. Other (please specify)

[Answer]: A

## Q2: Rollback

En caso de fallo tras el despliegue, ¿qué procedimiento de rollback aplica?

- A. El existente documentado en `docs/ROLLBACK.md` (revert del commit + re-deploy por el mismo pipeline / `fly deploy` de la release anterior). Recomendado.
- B. Otro procedimiento (especificar).
- X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Ruta de despliegue: por el pipeline existente `fly-deploy.yml` sin cambios (merge a `main` → verify pytest+ng test → deploy backend/frontend → smoke `/health`).
- Rollback: procedimiento existente de `docs/ROLLBACK.md` (revert del commit + re-deploy por el mismo pipeline / `fly deploy` de la release anterior).

Does this all look correct before I generate the deployment pipeline artifacts?

- Looks correct
- Request changes

[Answer]: Looks correct
