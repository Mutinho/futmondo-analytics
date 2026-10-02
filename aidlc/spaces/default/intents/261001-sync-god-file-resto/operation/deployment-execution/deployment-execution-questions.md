# Deployment Execution — Preguntas

> Intent `261001-sync-god-file-resto` (scope `refactor`, Minimal). El despliegue a
> producción es **on-merge/push a `main`** (dispara `fly-deploy.yml`). El código
> del dominio `clauses` está en el workspace, en `main`, **sin commitear**.
> Idioma: castellano.

## Q1 — Disparo del despliegue a producción (acción de alto riesgo)

El refactor del dominio `clauses` está listo y verificado (suite verde, piso de
cobertura intacto). El despliegue real a producción ocurre cuando los cambios se
fusionan/empujan a `main`, lo que ejecuta `fly-deploy.yml` (gate `verify` →
deploy backend/frontend → smoke `/health`). ¿Cómo procedemos con el despliegue?

- A. **Lo despliegas tú (humano), no el conductor**: yo documento la ejecución
  del despliegue como el procedimiento a seguir (commit → push/merge a `main` →
  pipeline Fly.io → verificación `/health`), pero NO ejecuto el push a `main` ni
  el deploy a producción. Tú decides cuándo commitear y empujar. El conductor
  nunca despliega a producción sin tu acción explícita.
- B. Autorizas explícitamente que el conductor commitee y empuje a `main` ahora
  para disparar el despliegue (confírmalo con las palabras exactas y el mensaje
  de commit que quieras).
- X. Other (please specify)

[Answer]: A — el despliegue a producción lo dispara el humano (commit + push a `main`); el conductor documenta el procedimiento pero no ejecuta el push ni el deploy.

## Q2 — Migraciones de base de datos

¿Se requieren migraciones de BD para este refactor?

- A. **No** — el refactor es equivalencia estricta sin cambios de esquema; no hay
  migración que ejecutar.
- B. Sí (especificar).
- X. Other (please specify)

[Answer]: A — no hay migraciones; equivalencia estricta sin cambios de esquema.

## Consolidated Summary Confirmation

Resumen de las decisiones:

- Q1 — El despliegue a producción (on-merge/push a `main` → `fly-deploy.yml`) lo
  dispara el **humano**. El conductor documenta el procedimiento de ejecución y
  la verificación esperada, pero NO ejecuta el commit/push a `main` ni el deploy.
- Q2 — **Sin migraciones de BD**: refactor de equivalencia estricta sin cambios
  de esquema.

Does this all look correct before I generate the artifacts?

- Looks correct
- Request changes

[Answer]: Looks correct
