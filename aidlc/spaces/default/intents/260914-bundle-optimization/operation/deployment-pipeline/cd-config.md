# CD Configuration — Optimización del bundle inicial

> Stage 4.1 Deployment Pipeline · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield (fase Operation).
> Rol: release engineer. El pipeline de CD YA existe; este refactor NO lo modifica. Coste 0 €.

## Sources

- `.github/workflows/fly-deploy.yml`, `.github/workflows/ci.yml` — pipelines existentes.
- `angular-app/fly.toml`, `angular-app/Dockerfile`, `angular-app/nginx.prod.conf` — despliegue del frontend.

## Pipeline de CD existente (sin cambios)

El flujo de entrega continua está definido en GitHub Actions y NO se modifica para este refactor:

### Gate de PR — `ci.yml` (en cada `pull_request` a `main`)
- **Bloqueantes**: `pytest` (backend), `ng test` con Vitest (frontend), `gitleaks` (secret scan).
- **Advisory** (no bloquean aún): `ruff`, `ESLint` (`ng lint`), `pip-audit`, `npm audit`.
- Combinado con branch protection (required status check en `main`): ningún cambio se fusiona en rojo.

### Deploy — `fly-deploy.yml` (en `push` a `main` y `workflow_dispatch`)
Jobs encadenados por `needs:`:
1. **`verify`** — reejecuta lint + tests (el gate se replica aquí para el push directo, porque `needs:` no cruza workflows).
2. **`deploy-backend`** — `flyctl deploy` en `./backend` (app `futmondo-api`).
3. **`deploy-frontend`** — `flyctl deploy` en `./angular-app` (app `futmondo-app`); el Dockerfile ejecuta `ng build --configuration production`.
4. **`smoke-test`** — verifica que `/health` del backend responde 200 (con reintentos).

## Impacto de este refactor en el CD

- **Ninguna modificación del pipeline.** El refactor es código frontend; se despliega por `deploy-frontend` tal cual.
- **Fail-closed que protege NFR1**: el `deploy-frontend` ejecuta `ng build --configuration production` dentro del Dockerfile con el budget `maximumError: 1MB` restaurado. Si un cambio futuro engordara el bundle por encima de 1 MB, el build fallaría y el deploy se detendría — el objetivo del intent queda protegido en cada despliegue. Verificado en Build and Test: initial 819 kB < 1 MB.
- **Secrets**: sin cambios (`FLY_API_TOKEN` en GitHub Secrets). El refactor no introduce secretos ni variables nuevas (NFR3, coste 0 €).

## Verificación de release

Sin staging separado (NFR2.2 del proyecto): la verificación de release es el smoke test `/health` post-deploy. Para este refactor, además, la verificación manual de gráficos y chat (documentada en Build and Test) debe hacerse tras el despliegue.
