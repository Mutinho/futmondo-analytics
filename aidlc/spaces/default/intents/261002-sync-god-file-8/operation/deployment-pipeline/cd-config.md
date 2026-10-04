# CD Configuration — Fly.io (documented, unchanged by this refactor)

Scope `refactor`, fase Operation, coste 0 €. `ci-pipeline` e `infrastructure-design`
están **saltadas por el alcance**: el proyecto ya tiene pipeline e infraestructura
en producción. Este documento describe la configuración de **despliegue continuo
EXISTENTE** y confirma que el refactor de descomposición de dominios de sync fluye
por ella **sin cambios** (Out of Scope del intent: sin tocar deploy ni crons).
La terminología AWS del stage se adapta al stack real Fly.io + Neon
(ver `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`).

## Fuentes (inputs saltados por alcance → se inspecciona el workspace existente)

- `ci-config` / `quality-gates` (de `ci-pipeline`): **N/A por alcance** — el gate
  vive en `.github/workflows/ci.yml` (PR→`main`) y en el job `verify` de
  `.github/workflows/fly-deploy.yml` (push→`main`).
- `infrastructure-specification` / `cicd-pipeline` (de `infrastructure-design`):
  **N/A por alcance** — la infra Fly.io (2 apps + Neon) ya existe y no cambia.
- Workspace existente: `.github/workflows/fly-deploy.yml`, `ci.yml`,
  `daily-sync.yml`, `sofascore-sync.yml`; `docs/ROLLBACK.md`, `docs/DEPLOY.md`.

## Pipeline de CD existente (fuente: `fly-deploy.yml`)

Disparo: `push` a `main` (y `workflow_dispatch`). Cadena de jobs vía `needs:`
(intacta — el endurecimiento previo refuerza el contenido de `verify`, no su
topología):

```
verify ──> deploy-backend ──> deploy-frontend ──> smoke-test
```

- **verify** (gate bloqueante replicado para el push directo; `needs:` no cruza
  workflows): gitleaks (`@v3`) · allowlist-expiry (`pip-audit`) · `pip-audit`
  sobre el entorno instalado · `ruff check` · `pytest --cov=app` con el piso de
  `pytest.ini` · `npm audit --audit-level=high` · `ng test --watch=false`.
- **deploy-backend**: `flyctl deploy` en `./backend` (app `futmondo-api`, puerto
  8000, check `/health`).
- **deploy-frontend**: `flyctl deploy` en `./angular-app` (app `futmondo-app`,
  nginx, check `/`); `needs: deploy-backend`.
- **smoke-test**: `curl` contra `/health` (5 reintentos, espera HTTP 200);
  `needs: [deploy-backend, deploy-frontend]`.

Secretos vía `secrets`/`vars` de GitHub Actions / Fly.io (`FLY_API_TOKEN`,
`SMOKE_HEALTH_URL`); `JWT_SECRET` efímero y no productivo en CI.

## Cómo encaja este refactor (sin cambios)

- El refactor es Python-backend-only y de **equivalencia estricta**: el job
  `verify` ya ejerce la suite extraída (329 passed, cobertura 43.19% ≥ piso 27)
  y `ruff check` sobre los ficheros nuevos (All checks passed).
- No se añade, reordena ni elimina ningún job; no se tocan los crons
  `daily-sync.yml` / `sofascore-sync.yml`.
- No hay migración de BD ni variable de entorno nueva: la superficie pública
  (`sync_all()` + 10 `sync_*`) está congelada, así que el worker del router sigue
  consumiendo las mismas 10 claves.

## Mapeo de adaptación (AWS del stage → equivalente gratuito real)

| Concepto AWS del stage | Equivalente en este stack | Estado |
|---|---|---|
| CodePipeline / CodeDeploy | GitHub Actions `fly-deploy.yml` (`needs:` chain) | Aplica |
| Promoción dev→staging→prod | **Sin staging**: deploy on-merge a `main`; `/health` es la verificación de release | Sustituido |
| Aprobación manual de producción | branch protection + gate bloqueante en PR; push directo re-gateado por `verify` | Aplica (parcial) |
| Registro de artefactos (ECR/S3) | registry de Fly.io (`registry.fly.io/futmondo-*`) | Aplica |
| Feature flags (AppConfig/Evidently) | **N/A**: no se usan; el refactor no los necesita | N/A |
| CloudWatch alarms → auto-rollback | smoke test `/health` en rojo → rollback manual (`docs/ROLLBACK.md`) | Sustituido |
