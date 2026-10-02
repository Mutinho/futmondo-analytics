# CD Configuration — `261001-sync-god-file-resto`

> Stack real: Fly.io (región `cdg`) + Neon PostgreSQL + GitHub Actions, coste 0 €.
> El conocimiento del stage asume AWS; aquí se mapea al stack real. Este refactor
> NO modifica el pipeline (ver `## Decisión`). Idioma: castellano.

## Decisión

Refactor de equivalencia estricta (dominio `clauses`): sin cambios de pipeline.
El CD existente despliega el cambio sin modificación. Documento aquí la config
vigente.

## Pipeline CD vigente (`.github/workflows/fly-deploy.yml`)

- **Disparo**: `push` a `main` (+ `workflow_dispatch`).
- **Cadena de jobs (`needs:` intacta)**:
  1. `verify` — gate bloqueante replicado para el push directo: gitleaks (`@v3`),
     allowlist-expiry, `pip-audit` (entorno instalado), `ruff check`, `pytest`
     con `--cov=app` + piso de `pytest.ini`, `npm audit --audit-level=high`,
     `ng test`.
  2. `deploy-backend` — `flyctl deploy` en `./backend` (app `futmondo-api`).
  3. `deploy-frontend` — `flyctl deploy` en `./angular-app` (app `futmondo-app`).
  4. `smoke-test` — `curl` a `/health` (5 reintentos, HTTP 200) como verificación
     de release.
- **Gate de PR** (`.github/workflows/ci.yml`): required status check en `main`
  que impide fusionar en rojo.

## Mapeo AWS → stack real (coste 0 €)

| Concepto AWS del stage | Equivalente real | Estado |
|---|---|---|
| CodePipeline / CodeBuild | GitHub Actions (`fly-deploy.yml`, `ci.yml`) | Aplica |
| ECR / artifact registry | imágenes Fly.io construidas por `flyctl deploy` | Aplica |
| Manual approval gate prod | gate `verify` bloqueante + branch protection | Aplica (sin staging separado) |
| CloudWatch alarms / auto-rollback | smoke test `/health` + rollback manual `flyctl` | Parcial (ver rollback-runbook) |
| Secrets Manager | `secrets` de GitHub Actions / `fly secrets` | Aplica |
| Feature flags (AppConfig/Evidently) | NO-APLICA — no se usan en este proyecto | NO-APLICA |

## Secretos

Vía `secrets` de GitHub Actions / Fly.io. En CI `JWT_SECRET` es efímero y no
productivo (`ci-ephemeral-secret-not-a-real-one`). `FLY_API_TOKEN` como secret.

## Crons (sin cambios)

`daily-sync.yml` y `sofascore-sync.yml` (máquinas Fly one-shot) no se tocan.
