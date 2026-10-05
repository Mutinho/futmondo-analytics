# Deployment Strategy — refactor `data_manager_v2` (equivalencia)

Scope `refactor` · fase Operation · stack Fly.io + Neon · coste 0 €. Este refactor
es de **equivalencia estricta**: resultado observable nulo, misma superficie
pública, mismos payloads. Por tanto **no cambia la estrategia ni la topología de
despliegue existentes**; este documento las registra aplicadas a este cambio.

## Estrategia: recreate / redeploy on-merge (sin cambios)

- **Modelo**: redeploy on-merge a `main` hacia Fly.io (región `cdg`). Fly realiza
  un reemplazo de máquinas (recreate); **no** hay blue/green ni canary. Un
  refactor de equivalencia no justifica introducir canary/blue-green (coste y
  complejidad; mandato coste 0 €, single-maintainer).
- **Topología (sin cambios)**: dos apps Fly.io — backend `futmondo-api` (puerto
  8000, check `/health`) y frontend `futmondo-app` (nginx, check `/`). BD Neon
  PostgreSQL (Frankfurt, free tier).
- **Cadena de despliegue (orden intacto)**:
  `verify → deploy-backend → deploy-frontend → smoke-test` (`fly-deploy.yml`).
  Los `needs:` encadenan los jobs; un rojo en `verify` impide los deploys.
- **Sin staging separado**: la verificación de release es el **smoke test
  `/health`** (5 reintentos, HTTP 200). Es la realidad del stack, no una
  decisión nueva.

## Gates de promoción

- **Gate único bloqueante (`verify`)**: gitleaks + allowlist-expiry + pip-audit
  (entorno instalado) + ruff check + pytest con cobertura y piso + npm audit
  (high) + ng test con cobertura. Paridad con el gate de PR (`ci.yml`).
- **Promoción a producción**: merge a `main` (trunk-based, squash). El push a
  `main` re-ejecuta el gate en `verify` (los `needs:` no cruzan workflows).
- **Aprobación**: sin aprobación manual adicional (single-maintainer); el gate
  de CI es el control.

## Esquema de BD (sin cambios en este refactor)

El refactor **no modifica el esquema de Neon** ni los DTOs: el SQL se mueve
**verbatim** a los adapters (misma consulta, mismas tablas). No hay migración
expand/contract que ejecutar en este despliegue. (Si un intent futuro tocara el
esquema, aplicaría expand-contract con cambios backward-compatible.)

## Migración de datos

Ninguna. Equivalencia estricta: sin cambio de datos ni de forma de datos.

## Ventanas de despliegue / freeze

No aplica una política formal (single-maintainer, deploy on-merge). El gate
bloqueante es la salvaguarda; un rojo nunca llega a producción.
