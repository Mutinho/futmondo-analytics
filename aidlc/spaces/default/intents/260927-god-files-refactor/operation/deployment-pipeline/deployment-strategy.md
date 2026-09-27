# Estrategia de Despliegue — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, brownfield. Conversation language: Spanish.
>
> Estrategia **vigente y no modificada** por esta oleada. Se documenta aplicada a la Oleada 1.

## Modelo de despliegue

**Deploy-on-merge a `main`** hacia Fly.io (región `cdg`), **sin entorno de staging separado**. La verificación de release es el smoke test contra `/health`.

- **Topología**: dos apps Fly.io — backend `futmondo-api` (puerto 8000, check `/health`) y frontend `futmondo-app` (nginx, check `/`). Base de datos Neon PostgreSQL (Frankfurt, tier free).
- **Estrategia por app**: redeploy directo de Fly.io (recreate/rolling gestionado por Fly), sin blue/green ni canary. No cambia con esta oleada.
- **Gates de promoción**: no hay tiers dev→staging→prod; el único gate previo a producción es el job `verify` (gitleaks + audits + lint + pytest con piso + ng test). Un rojo bloquea el deploy vía `needs:`.
- **Aprobación de producción**: el merge a `main` (tras pasar el gate de PR) es la aprobación; no hay aprobación manual adicional (modelo de un solo entorno afirmado por el equipo).

## Orden de despliegue (cadena `needs:` intacta)

```
verify  ->  deploy-backend  ->  deploy-frontend  ->  smoke-test (/health)
```

Esta oleada **no reordena** la cadena ni cambia el contenido de los jobs.

## Verificación de release

Smoke test `GET /health` con 5 reintentos (sleep 10 s), HTTP 200 = sano. Es la verificación de release en ausencia de staging (Q2 confirmada: se mantiene).

## Migraciones de BD

No aplica en esta oleada: la extracción de `analytics` no cambia el esquema ni añade migraciones (los 2 SELECT movidos son de solo lectura, mismo SQL). Neon sin cambios.

## Feature flags

No se usan feature flags en el proyecto; no se introducen en esta oleada (coste 0 €, sin tooling nuevo). La extracción es transparente para el consumidor (import path preservado).

## Crons (sin cambios)

`daily-sync.yml` y `sofascore-sync.yml` (máquinas Fly one-shot) no se tocan.

## Restricción

Todo en tiers gratuitos — coste 0 €.
