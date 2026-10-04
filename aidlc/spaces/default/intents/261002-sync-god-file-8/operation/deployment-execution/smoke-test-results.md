# Smoke Test Results — Sync Domain Decomposition

El smoke test de release es el job `smoke-test` de `fly-deploy.yml` contra
`/health`. Como el deploy es on-merge (no ejecutado en vivo desde esta sesión —
Q1=A), este documento recoge el **procedimiento, la expectativa, y la
verificación pre-merge** ya realizada en local.

## Fuentes

- `operation/deployment-execution/deployment-log.md`
- `.github/workflows/fly-deploy.yml` (job `smoke-test`)
- `construction/build-and-test/test-results.md`

## Smoke test de release (on-merge) — definición

```
URL = ${SMOKE_HEALTH_URL:-https://futmondo-api.fly.dev/health}
Reintentos = 5 (espera 10 s entre intentos)
Éxito = HTTP 200
```

Depende de `deploy-backend` y `deploy-frontend`. Si no devuelve 200 tras 5
intentos, el job falla (rojo) → dispara el procedimiento de rollback manual.

**Resultado esperado on-merge**: `HTTP 200` con `{"status":"healthy"}`. Como el
refactor es equivalencia estricta y la superficie pública (`/health` y los
endpoints de sync) no cambia, no se espera regresión en el smoke test.

## Verificación pre-merge (local, ya ejecutada)

Equivalente al "smoke" de la lógica refactorizada antes del merge: la suite
completa en verde con las characterization tests que congelan el comportamiento
observable.

| Check | Comando | Resultado |
|-------|---------|-----------|
| Suite backend + cobertura | `cd backend && pytest -q --cov=app --cov-fail-under=27` | **329 passed, 3 xfailed**; cobertura **43.19%** (≥ 27) |
| Lint ficheros nuevos | `ruff check --config ruff.toml app/services/sync/*` | **All checks passed** |
| god-file intacto | `git diff --stat .../data_manager_v2.py` | **vacío** |
| Superficie pública | `grep` 10 `sync_*` + `sync_all()` claves/orden | **idéntica** |

## Estado

- Smoke test de release: **pendiente del merge** (lo ejecuta el pipeline).
- Verificación pre-merge: **PASS** (suite verde, equivalencia congelada).
- Sin servicios dependientes nuevos que verificar (Q3=A).
