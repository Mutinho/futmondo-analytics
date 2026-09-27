# Configuración CD — Oleada 1 (analytics)

> Intent `260927-god-files-refactor`, scope `refactor`, brownfield. Conversation language: Spanish.
>
> El pipeline CD **ya existe** (`.github/workflows/fly-deploy.yml`) y está maduro en producción. Esta oleada de refactor **preserva el comportamiento** y NO modifica el workflow, su topología ni los crons. Este documento caracteriza el CD vigente aplicado a la Oleada 1 (adaptación al stack real Fly.io + Neon; coste 0 €).

## Pipeline CD vigente (`fly-deploy.yml`)

Disparadores: `push` a `main` y `workflow_dispatch`. Permisos: `contents: read`.

Cadena de jobs (`needs:` intacta — no se reordena):

```
verify  ->  deploy-backend  ->  deploy-frontend  ->  smoke-test (/health)
```

### Job `verify` (gate bloqueante replicado del PR)

Un rojo nunca llega a producción; el push directo a `main` re-ejecuta el gate (los `needs:` no cruzan workflows):

- gitleaks `@v3` (escaneo de secretos, bloqueante).
- Python 3.12; `pip install -r requirements.txt`.
- `pip-audit` (entorno instalado, bloqueante; allowlist versionada con caducidad).
- `ruff check .` (bloqueante).
- `pytest tests --cov=app --cov-report=term-missing` con piso `--cov-fail-under` de `pytest.ini` (bloqueante). `JWT_SECRET` efímero.
- Node 22; `npm ci`; `npm audit --audit-level=high` (bloqueante); `ng test --watch=false` (cobertura por métrica de `angular.json`, bloqueante).

### Jobs de deploy

- `deploy-backend`: `flyctl deploy` en `./backend` (app `futmondo-api`), `FLY_API_TOKEN` de secrets.
- `deploy-frontend`: `flyctl deploy` en `./angular-app` (app `futmondo-app`), depende de `deploy-backend`.

### Job `smoke-test`

Verifica `GET /health` (por defecto `https://futmondo-api.fly.dev/health`) con 5 reintentos; HTTP 200 = release sano.

## Aplicación a esta oleada

- La extracción de `analytics` es interna al backend (`app/services/analytics/` + shim); **no** añade servicios, apps Fly, ni endpoints, ni cambia el contrato de `/health`.
- El backend se sigue desplegando como `futmondo-api` sin cambios de configuración de deploy.
- El gate `verify` ya valida esta oleada en verde (218 passed, cobertura 29.75% ≥ 27) — ver `construction/build-and-test/test-results.md`.

## Secretos y coste

- Secretos vía GitHub Actions / Fly.io (`FLY_API_TOKEN`, `SMOKE_HEALTH_URL`). En CI el `JWT_SECRET` es efímero y no productivo.
- Todo dentro de tiers gratuitos (GitHub Actions, Fly.io free allowance, Neon free) — coste 0 €.

## Cambios introducidos por esta oleada

**Ninguno en el CD.** No se edita `fly-deploy.yml`, ni `ci.yml`, ni los crons (`daily-sync.yml`, `sofascore-sync.yml`).
