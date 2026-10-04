# Deployment Strategy — Fly.io (documented, unchanged by this refactor)

Scope `refactor`, fase Operation. Documenta la **estrategia de despliegue
EXISTENTE** y por qué no cambia con este refactor de equivalencia estricta.

## Fuentes

- Pipeline existente: `.github/workflows/fly-deploy.yml` (ver `cd-config.md`)
- `docs/DEPLOY.md`, `docs/ROLLBACK.md`
- Adaptación de stack: `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`
- Deuda de pipeline diferida conocida (de `operation-fly-stack.md`): paridad
  `--cov` en `verify` (ya cerrada), SAST/DAST frontend más allá de ESLint.

## Estrategia elegida (existente): deploy on-merge, verificación por smoke test

- **Entorno único de producción**, sin staging separado (coste 0 €). Cada merge a
  `main` que pasa el gate `verify` despliega a Fly.io; la **verificación de
  release es el smoke test `/health`** (5 reintentos, HTTP 200).
- **Mecanismo Fly.io**: `flyctl deploy` por app. Fly realiza el reemplazo de la
  release de forma gestionada; el estado en memoria (`TaskManager`, syncs en
  curso) se pierde en el redeploy — limitación aceptada del modelo de un único
  entorno.
- **Orden**: backend (`futmondo-api`) antes que frontend (`futmondo-app`), por la
  cadena `needs:`. El smoke test depende de ambos.

### Por qué NO canary / blue-green / staging en este intent

- El patrón canary/blue-green y un entorno de staging implican **infraestructura
  duplicada y/o servicios de pago**, incompatibles con el mandato coste 0 €
  (tiers gratuitos Fly.io / Neon / GitHub Actions).
- Este intent es un **refactor de equivalencia estricta**: no introduce riesgo de
  comportamiento observable nuevo que justifique un rollout progresivo. El gate
  verde + el smoke test `/health` son verificación suficiente (Q2=A).
- Cambiar la estrategia está **fuera de alcance** (Out of Scope del intent: sin
  cambios en el pipeline de deploy).

## Migración de base de datos

- **No aplica.** El refactor no cambia esquema (los adapters envuelven el SQL
  existente verbatim y no se amplía `data_manager_v2.py`). No hay paso
  expand/migrate/contract que ejecutar.

## Criterios de verificación y aborto del despliegue

- **Éxito**: `deploy-backend` y `deploy-frontend` terminan y el `smoke-test`
  devuelve HTTP 200 en `/health` dentro de 5 reintentos.
- **Aborto / fallo**: si `verify` falla (lint/tests/audits/secret-scan), los
  deploy no se ejecutan (`needs:`); si el smoke test queda en rojo, se dispara el
  procedimiento de rollback manual (`rollback-runbook.md`).

## Ventanas de despliegue

- Sin ventanas formales ni freeze (proyecto single-maintainer). El gate
  bloqueante es la única puerta; un rojo nunca llega a producción.
