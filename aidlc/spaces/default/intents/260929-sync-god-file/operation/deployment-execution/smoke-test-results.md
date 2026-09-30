# Smoke Test Results — sync god-file refactor

## Estado

**Pendiente de ejecución on-merge.** El smoke test de producción se ejecuta
automáticamente en el job `smoke-test` de `fly-deploy.yml` tras el deploy, cuando
el humano fusione el PR a `main`. No se ejecuta contra producción en esta sesión
(el deploy no se ha realizado, Q2=A).

## Definición del smoke test (verificación de release)

- **Qué**: `curl` contra `${SMOKE_HEALTH_URL:-https://futmondo-api.fly.dev/health}`.
- **Criterio de éxito**: HTTP 200 (payload esperado `{"status":"healthy"}`).
- **Reintentos**: 5 intentos con `sleep 10` entre ellos.
- **Efecto de fallo**: el job `smoke-test` en rojo marca el release fallido y es el
  trigger de rollback (`../deployment-pipeline/rollback-runbook.md`).

## Verificación local equivalente (proxy pre-release)

Como el refactor preserva la equivalencia estricta y no añade endpoints, la
verificación funcional del cambio es la **caracterización** ya ejecutada en verde
(no un smoke HTTP, que requiere el servicio desplegado):

- `test_sync_match_odds_characterization.py`: 7/7 verde, congela el `SyncResult`
  observable de `sync_match_odds` y la clave/orden en `sync_all()`.
- Suite completa: 251 passed / 3 xfailed. El endpoint `/api/v1/sync/*` y `sync_all()`
  conservan su comportamiento (mismo payload, mismas claves literales).

## Resultado esperado on-merge

Tras el deploy, `/health` debe devolver HTTP 200. Al no cambiar el arranque del
servicio ni el contrato público, no se espera regresión en el healthcheck
atribuible a este refactor.
