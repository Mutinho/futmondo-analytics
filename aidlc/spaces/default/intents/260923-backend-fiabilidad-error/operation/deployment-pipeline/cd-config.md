# CD Configuration — Operación (FR3.2 + FR4)

El pipeline de despliegue continuo **ya existe y es maduro**; este intent no lo
cambia. Se documenta la configuración vigente (Fly.io, on-merge) adaptada al
stack real y coste 0 €. Los patrones AWS del conocimiento se marcan NO-APLICA.

## Herramienta y disparador

- **GitHub Actions** `fly-deploy.yml`, disparo **push → `main`** (on-merge).
- Despliega a **Fly.io** (región `cdg`), free allowance.

## Cadena de despliegue (sin cambio en `needs:`)

| Job | Acción | Gate |
|---|---|---|
| `verify` | gitleaks + `pytest -q` + `ng test` (re-ejecuta el gate antes de desplegar) | Bloqueante: un rojo NO despliega |
| `deploy-backend` | `flyctl deploy` de `futmondo-api` (puerto 8000, check `/health`) | Requiere `verify` OK |
| `deploy-frontend` | `flyctl deploy` de `futmondo-app` (nginx, puerto 80, check `/`) | Requiere `deploy-backend` OK |
| `smoke-test` | `curl /health` (5 reintentos, HTTP 200) | Verificación de release |

## Secretos y config

- `DATABASE_URL`, `JWT_SECRET` (no-default), credenciales vía `fly secrets` /
  GitHub Actions `secrets`; nunca literales. `gitleaks` bloqueante.
- Config versionada: `fly.toml`, `Dockerfile`/`nixpacks.toml` (drift detectable
  por diff de git).

## Crons de despliegue-adyacente (coste ~0)

- `daily-sync.yml` (04:30 UTC) y `sofascore-sync.yml` (05:00 UTC): máquinas Fly
  one-shot que ejercitan las rutas de sync endurecidas por este intent; NO
  cambian el orden de deploy.

## NO-APLICA (adaptación a Fly.io + coste 0 €)

- AWS CodePipeline / CodeDeploy / entornos gestionados de aprobación → NO-APLICA.
- Feature flags gestionados (CloudWatch Evidently / AppConfig) → NO-APLICA (no
  se usan; sin necesidad en el alcance).
- Registro de artefactos externo (ECR) → NO-APLICA; imagen construida en el
  deploy de Fly.io.

## Assumptions & Open Questions

None.
