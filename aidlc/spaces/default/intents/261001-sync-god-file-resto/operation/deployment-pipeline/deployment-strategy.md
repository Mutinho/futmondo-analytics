# Deployment Strategy — `261001-sync-god-file-resto`

> Refactor de equivalencia estricta sobre sistema en producción. Idioma: castellano.

## Estrategia vigente

- **On-merge a `main`** → Fly.io (región `cdg`), sin entorno de staging separado.
  El smoke test contra `/health` (5 reintentos, HTTP 200) es la verificación de
  release.
- **Tipo de despliegue**: `flyctl deploy` por app (backend `futmondo-api` puerto
  8000 check `/health`; frontend `futmondo-app` nginx check `/`). Fly realiza un
  reemplazo con healthcheck; equivale a un rolling/recreate gestionado por la
  plataforma.
- **Orden**: `deploy-backend` → `deploy-frontend` (backend primero para que el
  frontend hable con una API ya actualizada).

## Idoneidad para este refactor

Equivalencia funcional estricta: sin cambios de esquema (no hay migración),
sin cambios de API ni de superficie pública, sin dependencias nuevas. El
despliegue es, por tanto, un redeploy del backend con el código reestructurado;
el patrón on-merge + smoke test `/health` existente es suficiente y seguro.

## Compatibilidad de esquema (expand-contract)

No aplica en este intent: no hay cambios de esquema. El patrón expand-contract
queda documentado como referencia para futuros intents que sí toquen el esquema.

## Gates de promoción

- PR → `main`: gate `ci.yml` (required status check).
- push → `main`: gate `verify` en `fly-deploy.yml` (replica del gate) del que
  dependen los deploys vía `needs:`. Un rojo nunca llega a producción.
- Post-deploy: smoke test `/health` como verificación de release.

## Ventanas / freeze

Sin ventanas formales ni freeze (proyecto single-maintainer). El gate bloqueante
y el smoke test son la salvaguarda.
