# CD Configuration — pipeline de despliegue (vigente, sin cambios)

Intent `260929-assistant-god-file`, scope `refactor` (Minimal), fase Operation. Brownfield: el
sistema ya está en producción con un pipeline Fly.io maduro. Este refactor **no cambia el
comportamiento observable** ni el artefacto desplegado (el shim de re-export preserva la superficie
pública), por lo que el pipeline CD existente sirve **sin cambios**. Regla afirmada: no se toca la
topología ni el orden de despliegue.

## Fuente de verdad

- **Workflow CD**: `.github/workflows/fly-deploy.yml` (disparo `push` → `main` y
  `workflow_dispatch`).
- **Gate de PR**: `.github/workflows/ci.yml` (disparo `pull_request` → `main`, required status
  check con branch protection).
- **Hosting**: Fly.io región `cdg` — backend `futmondo-api` (puerto 8000, check `/health`) y
  frontend `futmondo-app` (nginx, check `/`). BD: Neon PostgreSQL (Frankfurt, tier free).

## Topología y orden (cadena `needs:` intacta)

```
verify ──► deploy-backend ──► deploy-frontend ──► smoke-test (/health)
```

1. **`verify`** (gate bloqueante replicado en push→`main`; `needs:` no cruza workflows):
   gitleaks (`@v3`) → allowlist expiry check → `pip-audit==2.10.1` (entorno instalado) →
   `ruff==0.16.9 check` → `pytest --cov=app` con piso `--cov-fail-under` → `npm audit --audit-level=high`
   → `ng test --watch=false` (umbrales de cobertura por métrica en `angular.json`).
2. **`deploy-backend`** (`needs: verify`): `flyctl deploy` desde `backend/`.
3. **`deploy-frontend`** (`needs: deploy-backend`): `flyctl deploy` desde `angular-app/`.
4. **`smoke-test`** (`needs: [deploy-backend, deploy-frontend]`): `curl` a `/health`, 5 reintentos,
   espera HTTP 200 — es la verificación de release (no hay staging separado).

## Impacto del refactor sobre el CD

- **Ninguno en la configuración**: el refactor mueve código dentro de `backend/app/services/` a un
  paquete DDD y deja un shim de re-export; el contenedor backend se construye y despliega igual. No
  se añaden pasos, jobs ni cambios de orden.
- **El gate `verify` ya ejercita el paquete nuevo**: `pytest --cov=app` corre los 6 tests de
  caracterización nuevos + la suite completa (244 passed, cobertura 33.82% ≥ piso), y `ruff check .`
  cubre el paquete nuevo. Un rojo nunca llega a producción.

## Secretos y coste

- Secretos vía `secrets`/`vars` de GitHub Actions y Fly.io (`FLY_API_TOKEN`, `SMOKE_HEALTH_URL`);
  en CI el `JWT_SECRET` es efímero y no productivo. gitleaks bloqueante en ambos gates.
- **Coste 0 €**: GitHub Actions free + Fly.io free allowance + Neon free. Sin servicios de pago.

## NO-APLICA (equivalentes AWS de pago, por coste 0 €)

- CodePipeline/CodeDeploy, entornos gestionados dev/staging/prod separados, aprobaciones
  CodePipeline: sustituidos por on-merge a `main` + gate `verify`.
- Pin por SHA de acciones de terceros mutables (`superfly/flyctl-actions/setup-flyctl@master`): se
  decide en la etapa **ci-pipeline**, no en este refactor.
