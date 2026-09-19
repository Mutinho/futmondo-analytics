# Diseño de Pipeline CI/CD — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). Diseño de cómo el umbral de cobertura del frontend se cablea en el pipeline existente para que bloquee antes de producción (FR17.1). No es infraestructura nueva desplegable: modifica **workflows de GitHub Actions existentes**. Stack real: GitHub Actions (free tier) + Fly.io; NO AWS/CodePipeline. No es código final (eso es code-generation); son decisiones de diseño con snippets ilustrativos ≤15 líneas.

## Contexto del pipeline (estado base verificado)

- **`.github/workflows/ci.yml`** (PR→`main`, job `quality`): gitleaks (BLOQUEANTE) → `pytest -q --cov=app` (BLOQUEANTE) → Node `'22'` + `npm ci` → `ng test --watch=false` (BLOQUEANTE, **hoy sin flag de cobertura**) → auditorías advisory.
- **`.github/workflows/fly-deploy.yml`** (push→`main`), job `verify`: gitleaks (BLOQUEANTE) → `pytest -q` (sin `--cov`, deuda diferida) → `npm ci` → `ng test --watch=false` (BLOQUEANTE, **hoy sin flag de cobertura**). Luego `deploy-backend` → `deploy-frontend` → `smoke-test`.

## Diseño del cableado del gate de cobertura (FR17.1)

- **Fuente única de umbral**: la cobertura y sus umbrales por métrica se declaran en el target `test` de `angular.json`; `ng test` los aplica al ejecutarse.
- **Ejercitar el umbral en AMBOS caminos**: se corrige el comando `ng test --watch=false` en `ci.yml` (PR) y en el job `verify` de `fly-deploy.yml` (push→`main`) para que ejerza la cobertura (flag de cobertura del builder o su default en el target `test`). Snippet ilustrativo del diseño:
  ```yaml
  # Diseño (ci.yml y verify): ng test ejerciendo cobertura desde angular.json
  - run: npm ci
  - run: npx ng test --watch=false   # el target test de angular.json aplica coverage + thresholds
  ```
- **Sin cambio de la cadena `needs:`**: el orden de despliegue (`verify` → `deploy-backend` → `deploy-frontend` → `smoke-test`) no cambia; `verify` solo gana la exigencia de cobertura.
- **Bloqueo preservado**: `ng test` permanece bloqueante en ambos; gitleaks y pytest siguen bloqueantes. No se convierte ningún paso bloqueante en advisory (NFR1.4).
- **Reporte solo observabilidad**: cualquier paso adicional de reporte de cobertura es no bloqueante y NUNCA lleva `continue-on-error` que sustituya el enforcement dentro de `ng test` (NFR1.5).
- **Node fijado**: los jobs usan `node-version: '22'`; `.nvmrc` = `22.22.3`. Verificación local/CI en `node:22.22.3` antes de pushear devDependencies (NFR5).

## Deuda de pipeline diferida (Q8=A)

- Paridad `--cov` de backend en `verify` (hoy `pytest -q` sin `--cov`): fuera de alcance, deuda registrada.
- SAST/DAST del frontend: fuera de alcance, deuda registrada.

## Assumptions & Open Questions

- La sintaxis exacta del flag/opción de cobertura del builder `@angular/build:unit-test` de Angular 22 se valida en el spike de cableado de code-generation (A2).
