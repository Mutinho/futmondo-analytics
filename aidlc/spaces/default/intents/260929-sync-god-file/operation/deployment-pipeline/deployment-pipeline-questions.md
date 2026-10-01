# Deployment Pipeline — Preguntas de clarificación

Intent: `sync-god-file` (Oleada 3, FR13) · scope `refactor` · fase Operation.
El sistema ya está en producción con un pipeline Fly.io maduro (`fly-deploy.yml`):
cadena `verify → deploy-backend → deploy-frontend → smoke-test` (`/health`),
región `cdg`, dos apps, Neon PostgreSQL, coste 0 €. Este intent **no cambia la
topología ni el orden de despliegue**; documenta el pipeline existente y adapta al
stack real. Estas preguntas confirman las pocas decisiones abiertas.

---

## Q1 — Alcance del pipeline en este intent

¿Qué hace esta etapa respecto al pipeline de despliegue?

- A. **Documentar el pipeline Fly.io existente sin cambios** (cd-config, estrategia,
  runbook de rollback), ya que el refactor preserva la superficie pública y no
  altera el despliegue.
- B. Documentar y además proponer mejoras al pipeline (fuera del alcance del refactor).
- C. Rediseñar el pipeline de despliegue.
- D. Sin preferencia — documentar el existente sin cambios (A).
- X. Other (please specify)

[Answer]: A (documentar el pipeline Fly.io existente sin cambios: el refactor preserva la superficie pública y no altera el despliegue)

---

## Q2 — Estrategia de despliegue a documentar

El pipeline actual despliega on-merge a `main` (backend → frontend → smoke test),
sin staging separado; el smoke test `/health` es la verificación de release.
¿Cómo se documenta la estrategia?

- A. **Recreate on-merge con verificación por healthcheck** (lo que hace hoy):
  `verify` bloqueante → deploy secuencial backend/frontend en Fly.io → smoke test
  `/health` (5 reintentos, HTTP 200). Sin blue/green ni canary (no hay staging;
  coste 0 €).
- B. Documentar como si fuese blue/green (no es el caso real).
- C. Sin preferencia — reflejar exactamente el comportamiento actual (A).
- X. Other (please specify)

[Answer]: A (recreate on-merge con verificación por healthcheck: verify bloqueante → deploy secuencial backend/frontend en Fly.io → smoke test /health con 5 reintentos HTTP 200; sin blue/green ni canary, sin staging, coste 0 €)

---

## Q3 — Runbook de rollback

Existe `docs/ROLLBACK.md`; el mecanismo Fly.io es redeploy de la release anterior
(`fly releases` / `fly deploy` de la imagen previa).

- A. **Referenciar y resumir `docs/ROLLBACK.md`** en el runbook de la etapa,
  adaptado al stack Fly.io (redeploy de release anterior; el estado en memoria
  —`TaskManager`, syncs en curso— se pierde en el redeploy, limitación aceptada),
  con los triggers (smoke test `/health` fallido) y pasos concretos.
- B. Escribir un runbook de rollback nuevo desde cero, ignorando `docs/ROLLBACK.md`.
- C. Sin preferencia — referenciar y resumir el existente (A).
- X. Other (please specify)

[Answer]: A (referenciar y resumir docs/ROLLBACK.md adaptado a Fly.io: redeploy de la release anterior; trigger = smoke test /health fallido; limitación honesta: el estado en memoria —TaskManager, syncs en curso— se pierde en el redeploy)

---

## Consolidated Summary Confirmation

Resumen de las decisiones antes de generar los artefactos de la etapa:

- **Q1 — Alcance (A)**: documentar el pipeline Fly.io existente SIN cambios. El refactor preserva la superficie pública y no altera el despliegue; no se reordena la cadena `needs:` ni se amplía el alcance.
- **Q2 — Estrategia (A)**: recreate on-merge con verificación por healthcheck, reflejando `fly-deploy.yml` tal cual — `verify` bloqueante (gitleaks + pip-audit/allowlist + ruff + pytest con cobertura y piso + npm audit + ng test) → `deploy-backend` → `deploy-frontend` → `smoke-test` `/health` (5 reintentos, HTTP 200). Sin blue/green ni canary; sin staging separado; coste 0 €.
- **Q3 — Rollback (A)**: referenciar y resumir `docs/ROLLBACK.md`, adaptado al stack Fly.io (redeploy de la release anterior); trigger = smoke test `/health` fallido; limitación honesta: el estado en memoria se pierde en el redeploy.
- **Adaptación al stack real (regla afirmada)**: se documenta contra Fly.io + Neon + GitHub Actions, marcando NO-APLICA/diferido lo que asumiría AWS (blue/green gestionado, canary con CloudWatch alarms, feature flags AppConfig/Evidently), con la alternativa gratuita en su lugar. No se inventa infraestructura inexistente.
- **Artefactos a generar**: `cd-config.md` (el pipeline `fly-deploy.yml` documentado), `deployment-strategy.md` (recreate on-merge + verificación), `rollback-runbook.md` (resumen de `docs/ROLLBACK.md` + triggers/pasos). Cobertura de `consumes` ausentes (ci-config, infrastructure-specification) por scope refactor: se trabaja contra el pipeline y la infra existentes en el workspace, sin inventar.

Does this all look correct before I generate the artifact?

- Looks correct
- Request changes

[Answer]: Looks correct
