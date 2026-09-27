# Log de Ejecución de Despliegue — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, brownfield. Conversation language: Spanish.
>
> Modelo deploy-on-merge: el despliegue a producción lo ejecuta el push/merge a `main` vía `.github/workflows/fly-deploy.yml`. Este log documenta la verificación previa (ya realizada) y el estado de la ejecución en producción.

## Estado del cambio

- Rama: `main`.
- Código de la extracción: en el working tree, **pendiente de commit/merge** al generar este log. Ficheros: `backend/app/services/analytics/**` (nuevo paquete), `backend/app/services/analytics_service.py` (shim), `backend/tests/test_analytics_service.py` (tests). Consumidores no tocados.
- El asistente **no** ha hecho push directo a `main` (regla de git safety; el push/merge es decisión humana o del flujo de PR).

## Verificación pre-despliegue (realizada localmente)

| Check | Resultado |
|-------|-----------|
| Import del paquete (`app.main`) | OK (shim re-exporta la fachada) |
| Suite pytest | 218 passed, 0 failed, 3 xfailed |
| Cobertura | 29.75% ≥ piso 27% |
| Ruff (módulos nuevos) | All checks passed |

Evidencia: `construction/build-and-test/test-results.md`.

## Ejecución en producción (pendiente del merge)

El despliegue real se dispara al fusionar a `main`. Secuencia que ejecutará `fly-deploy.yml`:

1. `verify` — re-ejecuta el gate bloqueante (gitleaks + pip-audit + ruff + pytest con piso + npm audit + ng test). Un rojo aborta el deploy.
2. `deploy-backend` — `flyctl deploy` de `futmondo-api` (incluye la extracción de `analytics`).
3. `deploy-frontend` — `flyctl deploy` de `futmondo-app` (sin cambios en esta oleada).
4. `smoke-test` — `GET /health` (5 reintentos, HTTP 200).

**Estado**: PENDIENTE — se completará cuando el cambio se fusione a `main`. Hasta entonces, esta oleada queda verificada localmente y lista para desplegar.

## Migraciones de BD

Ninguna. La extracción no cambia el esquema (los 2 SELECT movidos son de solo lectura, mismo SQL). Neon sin cambios.

## Rollback

Disponible: `operation/deployment-pipeline/rollback-runbook.md` (redeploy de la release previa en Fly.io). No requerido salvo fallo del smoke test post-merge.

## Coste

Dentro de tiers gratuitos (GitHub Actions, Fly.io, Neon) — coste 0 €.
