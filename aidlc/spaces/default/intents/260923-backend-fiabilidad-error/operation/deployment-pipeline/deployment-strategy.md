# Deployment Strategy — Operación (FR3.2 + FR4)

Estrategia de despliegue del intent de fiabilidad. **Sin cambio** respecto a la
línea base afirmada: on-merge a `main` → Fly.io, un único entorno productivo.

## Estrategia

- **Modelo**: **recreate** implícito por redeploy de Fly.io (la máquina se
  reemplaza en el deploy). **Sin blue/green ni canary**: la topología es fija
  (`min=max=1`, `shared-cpu-1x`/256 MB por app) y el mandato es coste 0 €, así
  que no hay capacidad para entornos paralelos ni traffic-shifting.
- **Sin entorno de staging separado**: el **smoke test `/health`** (5 reintentos,
  HTTP 200) es la verificación del release.
- **Promoción**: no hay matriz dev→staging→prod; el gate CI bloqueante
  (gitleaks + `pytest` + `ng test`) en `verify` es la puerta única antes del
  deploy. Un rojo nunca llega a producción.

## Criterios de éxito / aborto del release

- **Éxito**: `deploy-backend` y `deploy-frontend` OK **y** `smoke-test /health`
  = 200. La release queda activa.
- **Aborto/rojo**: si `verify` falla, no se despliega. Si el smoke test falla
  tras el deploy, el workflow lo marca en rojo → se ejecuta el **rollback**
  (ver `rollback-runbook.md`).

## Relación con la fiabilidad de este intent (principio de release)

- Un fallo **recuperable** en el sync degrada y continúa (`StepStatus.DEGRADED`
  vía `sync_step_status.py`), sin corromper datos.
- Un fallo **fatal** aborta limpio (excepción tipada propagada), sin dejar datos
  a medias — el reemplazo transaccional atómico de `team_prizes` garantiza la
  no-corrupción.

## Feature flags

- No se usan feature flags gestionados; el endurecimiento es aditivo y va tras
  el gate de CI. NO-APLICA (coste 0 €).

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- Blue/green, canary con traffic-shifting, multi-región activo-activo → NO-APLICA
  (topología fija, coste 0 €). Se documenta la alternativa (recreate + smoke test)
  en vez de inventar infraestructura de pago.

## Assumptions & Open Questions

None.
