# Deployment Execution Questions — Durabilidad del estado

> Etapa Deployment Execution (Operation). En Operation las preguntas son excepcionales. El despliegue
> de este proyecto es automático on-merge a `main` (`fly-deploy.yml`); esta etapa documenta el
> runbook/plan de ejecución y los criterios de verificación. El despliegue efectivo lo realiza el
> pipeline al fusionar el MR; NO se dispara `fly deploy` manual ni se tocan secretos productivos desde
> esta sesión. No se abren preguntas nuevas.

## Contexto resuelto (no requiere pregunta)

- **Mecanismo de despliegue**: automático on-merge a `main` vía `.github/workflows/fly-deploy.yml`
  (job `verify` → `deploy-backend` → `deploy-frontend` → `smoke-test`). deployment-pipeline se saltó
  (pipeline existente adecuado), así que `cd-config`/`deployment-strategy` ausentes son esperados; se
  usa la config real del workspace.
- **Acción previa obligatoria**: fijar el secret `FUTMONDO_CRED_KEY` (Fernet) en Fly.io `futmondo-api`
  antes del deploy (validado en environment-provisioning). Degradación segura si falta (401 accionable).
- **Migraciones**: ninguna manual; el esquema durable (`sync_session`/`sync_task`) se crea idempotente
  en el arranque.
- **Verificación de release**: smoke test contra `/health` (5 reintentos, HTTP 200) — sin staging
  separado.
- **Estado de la red de seguridad**: 125 tests passed, 0 regresiones (de build-and-test); el gate de
  MR (gitleaks + pytest + ng test) debe pasar antes de fusionar.
- **Rollback**: `docs/ROLLBACK.md` (redeploy de release anterior); esquema durable aditivo/idempotente,
  sin rollback de BD.

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
