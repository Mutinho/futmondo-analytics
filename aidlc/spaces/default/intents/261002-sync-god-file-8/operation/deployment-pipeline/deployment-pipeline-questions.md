# Deployment Pipeline — Questions (intent 261002-sync-god-file-8)

Scope `refactor` (depth Minimal), fase Operation. El sistema ya está en
producción con un pipeline Fly.io maduro (`verify → deploy-backend →
deploy-frontend → smoke-test`), un gate de CI bloqueante operativo, y un runbook
de rollback (`docs/ROLLBACK.md`). Este intent es un **refactor de equivalencia
estricta** cuyo "Out of Scope" dice explícitamente: **sin cambios en el
frontend, el pipeline de deploy ni los crons**.

Las etapas `ci-pipeline` e `infrastructure-design` están **saltadas por el
alcance** (ya hay pipeline e infra). Por eso, las preguntas aquí son mínimas:
confirmar que los artefactos de CD documentan el pipeline **existente** sin
cambiarlo.

---

## Q1. Alcance de los artefactos de Deployment Pipeline para este refactor

¿Qué deben capturar `cd-config.md`, `deployment-strategy.md` y
`rollback-runbook.md` en este intent?

A. **Documentar el pipeline Fly.io EXISTENTE sin cambios** (deploy on-merge a
   `main`; cadena `verify → deploy-backend → deploy-frontend → smoke-test`;
   rollback manual `fly releases rollback`), explicitando cómo el refactor fluye
   por él sin alterar topología, orden ni crons, y adaptando la terminología
   AWS del stage al stack real Fly.io + Neon (coste 0 €). (Recomendado — alineado
   con el Out of Scope del intent.)
B. Proponer cambios/mejoras al pipeline de deploy (p. ej. estrategia canary,
   staging) como parte de este intent.
C. Otro (lo indico en el detalle).
X. Other (please specify)

[Answer]: A. Documentar el pipeline Fly.io EXISTENTE sin cambios (deploy on-merge a `main`; cadena `verify → deploy-backend → deploy-frontend → smoke-test`; rollback manual), adaptado a Fly.io + Neon (coste 0 €), explicitando que el refactor fluye por él sin alterar topología, orden ni crons. **Mode:** guided

---

## Q2. Consideración de despliegue específica del refactor

El refactor preserva la superficie pública (`sync_all()` y los 10 `sync_*`) y no
cambia esquema de BD ni endpoints. ¿Hay alguna consideración de despliegue
adicional a documentar?

A. **Ninguna especial**: al ser equivalencia estricta sin cambios de esquema ni
   de API, no hay migración de BD ni paso de despliegue nuevo; el smoke test
   `/health` y la suite verde del gate son verificación suficiente. (Recomendado.)
B. Sí, hay una consideración concreta (la indico en el detalle: p. ej. un paso
   de verificación extra, un orden de despliegue, una variable nueva).
X. Other (please specify)

[Answer]: A. Ninguna especial: equivalencia estricta sin cambios de esquema ni de API, sin migración de BD ni paso de despliegue nuevo; el smoke test `/health` y la suite verde del gate son verificación suficiente. **Mode:** guided

---

## Consolidated Summary Confirmation

Resumen de decisiones:

- Q1: Los artefactos de CD (`cd-config.md`, `deployment-strategy.md`, `rollback-runbook.md`) documentan el pipeline Fly.io EXISTENTE sin cambios (deploy on-merge a `main`; cadena `verify → deploy-backend → deploy-frontend → smoke-test`; rollback manual `fly releases rollback`), adaptando la terminología AWS del stage al stack real Fly.io + Neon (coste 0 €), y explicitan que el refactor fluye por el pipeline sin alterar topología, orden ni crons.
- Q2: Ninguna consideración de despliegue especial: equivalencia estricta sin cambios de esquema ni API, sin migración de BD ni paso nuevo; el smoke test `/health` (5 reintentos, HTTP 200) y la suite verde del gate son la verificación de release.
- Alineado con el "Out of Scope" del intent (sin cambios en deploy ni crons) y con la verificación de frontera Construction→Operation (PASS).

- Looks correct
- Request changes

[Answer]: Looks correct
