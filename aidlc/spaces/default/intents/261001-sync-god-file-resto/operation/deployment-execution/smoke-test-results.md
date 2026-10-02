# Smoke Test Results — `261001-sync-god-file-resto`

> El smoke test lo ejecuta el job `smoke-test` de `fly-deploy.yml` tras el deploy
> disparado por el humano. Estado: **pendiente de disparo humano**. Idioma: castellano.

## Smoke test definido (vigente, sin cambios)

- Comando: `curl` a `/health` del backend (`https://futmondo-api.fly.dev/health`),
  5 reintentos, espera HTTP `200`.
- Es la verificación de release (no hay staging separado).

## Resultado

**PENDIENTE** — se registrará automáticamente en la ejecución de `fly-deploy.yml`
cuando el humano empuje a `main`. Un `200` confirma el release; un fallo del job
`smoke-test` señala la necesidad de rollback (ver `rollback-runbook.md`).

## Criterio de éxito

- `/health` responde `200` dentro de los 5 reintentos.
- Verificación complementaria sugerida (manual, coste 0 €): lanzar un sync y
  confirmar en `fly logs` que `sync_clauses` produce el mismo `SyncResult` y no
  aparecen pasos `degraded` inesperados.
