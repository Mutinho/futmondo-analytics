# Preguntas — Deployment Pipeline (Fiabilidad de la sync)

> Conversation language: Spanish. Fase Operation. Intent acotado y aditivo: la
> CD **ya existe** (`.github/workflows/fly-deploy.yml`) y el runbook de rollback
> también (`docs/ROLLBACK.md`). Esta etapa **documenta** la CD, la estrategia de
> despliegue y el rollback; NO cambia la topología ni el orden de despliegue
> (solo se endureció antes la señal de calidad previa al deploy). Infra real:
> Fly.io (región `cdg`) + Neon PostgreSQL. Respuestas determinadas por la CD
> real (Operation: preguntas excepcionales). Coste 0 €.

## Q1 — ¿Estrategia de despliegue?

A. Redeploy on-merge (imagen nueva reemplaza a la anterior) con smoke test de release
B. Blue/green
C. Canary
D. Rolling
X. Other (please specify)

[Answer]: A. Redeploy on-merge a `main` hacia Fly.io, verificado por smoke test contra `/health` (5 reintentos, HTTP 200). Sin blue/green ni canary (entorno único; coste 0 €).

## Q2 — ¿Gates de promoción entre entornos (dev → staging → prod)?

A. Sin staging separado; un único entorno de producción, gate = `verify` + smoke test
B. dev → staging → prod
X. Other (please specify)

[Answer]: A. No hay staging separado. El gate previo al deploy es el job `verify` (gitleaks + pytest + ng test, bloqueantes) del que dependen los deploys vía `needs:`; la verificación de release es el smoke test `/health`.

## Q3 — ¿Workflow de aprobación para producción?

A. Automático on-merge a `main` (branch protection + gate de CI verde); sin aprobación manual extra
B. Aprobación manual (tech lead + product owner)
X. Other (please specify)

[Answer]: A. Deploy automático on-merge a `main`, gobernado por branch protection (required status check) y por el gate `verify` re-ejecutado en el push. Un rojo nunca llega a producción (FR8.2).

## Q4 — ¿Procedimiento de rollback?

A. Redeploy manual de la release previa con `flyctl` (runbook documentado)
B. Automático
X. Other (please specify)

[Answer]: A. Manual: `fly releases rollback <vN>` (o redeploy explícito de la imagen previa) + verificación `/health`. Documentado en `docs/ROLLBACK.md`. Limitación aceptada: el estado en memoria (TaskManager, syncs en curso) se pierde en el redeploy.

## Q5 — ¿Estrategia de feature flags?

A. Ninguna (no aplica a este intent; sin servicio de flags)
B. Sí (especificar)
X. Other (please specify)

[Answer]: A. No aplica. El intent es una intervención de fiabilidad backend acotada y aditiva; no introduce feature flags ni un servicio de flags (coste 0 €).

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
