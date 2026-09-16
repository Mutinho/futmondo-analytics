# Smoke Test Results — Optimización del bundle inicial

> Stage 4.3 Deployment Execution · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield (fase Operation).

## Sources

- `construction/build-and-test/test-results.md`.
- `.github/workflows/fly-deploy.yml` (job `smoke-test`).

## Smoke tests pre-despliegue (ejecutados localmente en contenedor node:22.22.3)

| Verificación | Resultado |
|---|---|
| Build de producción con `maximumError: 1MB` | ✓ PASS (initial 819.05 kB < 1 MB) |
| Suite de tests (`ng test --no-watch`) | ✓ 11/11 verde |
| chart.js/ng2-charts fuera del chunk inicial | ✓ verificado (en chunk lazy) |
| marked fuera del chunk inicial | ✓ verificado (`assistant-chat-component` lazy) |
| Compilación de `@defer` del chat | ✓ PASS (tras fix NG8001) |

## Smoke test post-despliegue (a ejecutar en el pipeline al mergear)

El job `smoke-test` de `fly-deploy.yml` verifica automáticamente tras el deploy:

```bash
curl -sS https://futmondo-api.fly.dev/health   # espera HTTP 200
```

Con reintentos (5 × 10s). Un fallo marca el workflow en rojo → aplicar rollback (`rollback-runbook.md`).

## Estado

- Pre-despliegue: **todo verde**.
- Post-despliegue: **PASADO**. El `flyctl deploy` ejecutó smoke checks y health checks sobre la máquina `1850356b030438`, que alcanzó estado `started` y `good state`; DNS de `futmondo-app.fly.dev` verificado. Build en el pipeline: initial 819.05 kB (< 1 MB). App en vivo: https://futmondo-app.fly.dev/
