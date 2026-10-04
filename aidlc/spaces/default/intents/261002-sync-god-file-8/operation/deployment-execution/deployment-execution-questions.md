# Deployment Execution — Questions (intent 261002-sync-god-file-8)

Scope `refactor` (depth Minimal), fase Operation, última etapa. `environment-provisioning`
está saltada por el alcance (la infra Fly.io ya existe); el target se inventaría
del workspace (`backend/fly.toml`, `.github/workflows/fly-deploy.yml`).

**Contexto importante**: el despliegue de este proyecto es **on-merge a `main`**
vía GitHub Actions (`fly-deploy.yml`), gateado por `verify`. El código del
refactor aún no está fusionado; el deploy real lo dispara el merge a `main`, no
una ejecución `flyctl deploy` manual desde esta sesión. Por eso esta etapa
**documenta y verifica la ruta de release** (readiness + procedimiento de
smoke/health que correrá on-merge), sin ejecutar un push a producción en vivo.

---

## Q1. Modo de ejecución del despliegue para este refactor

¿Cómo tratamos la "ejecución" del despliegue en esta etapa?

A. **Documentar la ruta de release on-merge y la readiness pre-deploy** (gate
   `verify` verde, smoke test `/health` definido), SIN ejecutar un `flyctl deploy`
   en vivo desde aquí: el deploy real ocurre cuando el PR del refactor se fusiona
   a `main` y lo dispara el pipeline. (Recomendado — alineado con trunk-based,
   gate bloqueante, y el Out of Scope del intent.)
B. Ejecutar un despliegue en vivo a producción ahora desde esta sesión
   (`flyctl deploy`).
C. Otro (lo indico en el detalle).
X. Other (please specify)

[Answer]: A. Documentar la ruta de release on-merge y la readiness pre-deploy (gate `verify` verde, smoke test `/health` definido), SIN ejecutar `flyctl deploy` en vivo desde aquí: el deploy real ocurre al fusionar el PR a `main`. **Mode:** guided

---

## Q2. Migraciones de base de datos

¿Se requiere alguna migración de BD como parte de este despliegue?

A. **No**: el refactor es equivalencia estricta, no cambia esquema ni escribe
   datos nuevos (los adapters envuelven el SQL existente verbatim; no se amplía
   `data_manager_v2.py`). No hay migración que ejecutar. (Recomendado.)
B. Sí, hay una migración (la indico en el detalle).
X. Other (please specify)

[Answer]: A. No: equivalencia estricta, no cambia esquema ni escribe datos nuevos (los adapters envuelven el SQL existente verbatim; no se amplía `data_manager_v2.py`). No hay migración que ejecutar. **Mode:** guided

---

## Q3. Checks pre-despliegue

¿Qué constituye el conjunto de checks pre-despliegue para dar por lista la
release?

A. **El gate `verify` en verde** (gitleaks + pip-audit + ruff + pytest con piso
   de cobertura + npm audit + ng test) **más el smoke test `/health`** post-deploy
   (5 reintentos, HTTP 200). Suite ya verde: 329 passed, cobertura 43.19% ≥ 27.
   Sin servicios dependientes nuevos. (Recomendado.)
B. Hay checks adicionales a incluir (los indico en el detalle).
X. Other (please specify)

[Answer]: A. El gate `verify` en verde (gitleaks + pip-audit + ruff + pytest con piso de cobertura + npm audit + ng test) más el smoke test `/health` post-deploy (5 reintentos, HTTP 200). Suite verde: 329 passed, cobertura 43.19% ≥ 27. Sin servicios dependientes nuevos. **Mode:** guided

---

## Consolidated Summary Confirmation

Resumen de decisiones:

- Q1: Esta etapa **documenta la ruta de release on-merge y la readiness pre-deploy**, SIN ejecutar `flyctl deploy` en vivo desde la sesión; el deploy real lo dispara el merge del PR a `main` a través de `fly-deploy.yml` (trunk-based, gate bloqueante).
- Q2: **Sin migración de BD** — equivalencia estricta, sin cambio de esquema ni datos nuevos.
- Q3: Checks pre-deploy = **gate `verify` verde** (gitleaks + pip-audit + ruff + pytest con piso + npm audit + ng test) **+ smoke test `/health`** (5 reintentos, HTTP 200). Suite verde (329 passed, cobertura 43.19% ≥ 27), sin servicios dependientes nuevos.
- Artefactos a generar: `deployment-log.md` (ruta on-merge + estado de readiness), `smoke-test-results.md` (procedimiento y expectativa del smoke `/health`), `health-check-report.md` (checks de salud adaptados a Fly.io + Neon, coste 0 €).

- Looks correct
- Request changes

[Answer]: Looks correct
