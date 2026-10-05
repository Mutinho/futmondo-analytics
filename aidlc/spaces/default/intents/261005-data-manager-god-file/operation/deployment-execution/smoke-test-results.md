# Smoke Test Results — refactor `data_manager_v2`

El smoke test de release es el que `fly-deploy.yml` ejecuta tras el deploy
on-merge. Como el refactor está pendiente de merge, aquí se registra el criterio
y su estado (pendiente de ejecución on-merge).

## Smoke test de release (definido en `fly-deploy.yml`)

| Campo | Valor |
|---|---|
| Objetivo | `https://futmondo-api.fly.dev/health` (`SMOKE_HEALTH_URL`) |
| Método | `curl` HTTP GET |
| Criterio de éxito | HTTP 200 |
| Reintentos | 5 (sleep 10 s entre intentos) |
| Respuesta esperada | `{"status":"healthy"}` |
| Momento | Tras `deploy-backend` + `deploy-frontend`, job `smoke-test` |

## Estado

**PENDIENTE (on-merge).** No ejecutado desde esta etapa: no se despliega
manualmente a producción. El resultado real se producirá en el job `smoke-test`
cuando el PR se fusione a `main`.

## Expectativa de equivalencia

Al ser un refactor de equivalencia estricta (misma superficie de 57 métodos,
mismos payloads, SQL verbatim), se espera que `/health` siga devolviendo 200 y
que el comportamiento observable de los endpoints (`/api/v1/statistics`,
`/api/v1/market/today`, sync, finanzas, etc.) sea idéntico al pre-refactor. La
red de seguridad local (414 tests verdes) respalda esa expectativa antes del
merge.

## Criterio de fallo / acción

Si el smoke `/health` devuelve != 200 tras los 5 reintentos, el workflow queda
en rojo → ejecutar el rollback de `rollback-runbook.md` y abrir PR con el fix
(añadiendo el caso al characterization test del módulo afectado antes de
reintentar la extracción).
