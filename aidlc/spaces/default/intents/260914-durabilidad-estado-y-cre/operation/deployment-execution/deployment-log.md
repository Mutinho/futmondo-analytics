# Deployment Log — Durabilidad del estado

> Etapa Deployment Execution (Operation). **Plan/runbook de ejecución del despliegue.** El despliegue
> de este proyecto es automático on-merge a `main` (`.github/workflows/fly-deploy.yml`); el código de
> durabilidad aún no está fusionado. Este log documenta la ejecución planificada y sus criterios; el
> despliegue efectivo lo realiza el pipeline al fusionar el MR. NO se ejecutó `fly deploy` manual ni
> se tocaron secretos productivos desde el workflow.

## Estado de la ejecución

- **Estado**: PLANIFICADO — pendiente de fusión a `main`. El deploy real se dispara con el merge del MR.
- **Mecanismo**: automático, `fly-deploy.yml` (push→`main`).
- **Ejecución manual desde el workflow**: NO (acción de alto impacto; el modelo del equipo es deploy-on-merge).

## Acción previa obligatoria (antes del primer deploy con durabilidad de sesión)

Fijar el secret nuevo en Fly.io (validado en environment-provisioning):

```bash
fly secrets set \
  FUTMONDO_CRED_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" \
  --app futmondo-api
```

Si falta: el backend arranca igual pero no rehidrata sesiones tras reinicio (401 accionable, degradación segura).

## Secuencia de despliegue planificada (`fly-deploy.yml`)

| Paso | Job | Acción | Criterio de éxito |
|------|-----|--------|-------------------|
| 1 | `verify` | gitleaks + `pytest` + `ng test` | Todos verdes (bloqueante) |
| 2 | `deploy-backend` | `flyctl deploy` de `backend/` (`futmondo-api`) | Deploy OK; app arranca (crea esquema durable idempotente, sweep de interrumpidas) |
| 3 | `deploy-frontend` | `flyctl deploy` de `angular-app/` (`futmondo-app`) | Deploy OK |
| 4 | `smoke-test` | `curl /health` (5 reintentos) | HTTP 200 |

## Migraciones de base de datos

- **Ninguna manual.** El esquema durable (`sync_session`, `sync_task`) se crea de forma idempotente en
  el arranque de la app (`ensure_durable_session_schema` / `ensure_durable_task_schema`). No hay paso
  de migración en el pipeline.

## Precondiciones verificadas (de etapas previas)

- Red de seguridad: 125 tests passed, 0 regresiones (`construction/build-and-test/test-results.md`).
- Entorno validado: inventario y validación de secretos en `operation/environment-provisioning/`.
- Gate de MR obligatorio antes de fusionar (gitleaks + pytest + ng test bloqueantes).

## Rollback

- Runbook: `docs/ROLLBACK.md` (redeploy de la release anterior en Fly.io).
- El esquema durable es aditivo e idempotente: un rollback de la app no requiere rollback de BD.

## Notas

- Región `cdg` (fly.toml); memoria 256 MB por máquina — vigilar tras el deploy, margen para
  `fly scale memory 512` dentro del free allowance si fuese necesario.
- Coste 0 € — sin recursos de pago nuevos.
