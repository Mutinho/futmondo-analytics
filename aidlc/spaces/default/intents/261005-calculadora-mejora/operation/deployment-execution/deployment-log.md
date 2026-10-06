# Deployment Log — calculadora-mejora

## Estado: LISTO PARA DESPLEGAR (deploy pendiente del merge a `main`)

El despliegue a producción es **on-merge a `main`** (GitHub Actions → Fly.io).
El cambio de código de este intent (frontend-only, unidad `calculator-toggle`)
está implementado y verificado en local, pero **aún no commiteado/merged**. El
deploy real se dispara cuando el humano abra el PR y lo fusione a `main`.

## Procedimiento de despliegue

1. Commit del cambio (`feat(calculator): toggle Incorporar jugadores en venta`),
   PR a `main`.
2. **PR-gate** (`ci.yml`): gitleaks + pytest + ng test. Bloqueante.
3. Merge a `main` (squash) → dispara `fly-deploy.yml`:
   - `verify` (gitleaks + pytest + ng test) →
   - `deploy-backend` (`futmondo-api`, sin cambios en este intent) →
   - `deploy-frontend` (`futmondo-app`, publica el bundle con el toggle) →
   - `smoke-test` (`/health`, 5 reintentos, HTTP 200).
4. Verificación: ver `smoke-test-results.md` y `health-check-report.md`.

## Artefactos desplegados

- Bundle Angular con la unidad `calculator-toggle` (ficheros
  `calculator.component.{ts,html,scss,spec.ts}`). Sin cambios de backend ni BD.

## Registro de ejecución

- **Deploy ejecutado**: pendiente (on-merge). Este registro se completa tras el
  merge; el estado del release lo refleja `fly status --app futmondo-app`.
- **Migraciones de BD**: N/A (frontend-only).

## Sources

- `operation/deployment-pipeline/cd-config.md`, `deployment-strategy.md`.
- `construction/build-and-test/test-results.md` (readiness).

## Assumptions & Open Questions

None.
