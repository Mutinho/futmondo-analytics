# Resultados de Build y Test — Mejoras de CI/Tooling

> Etapa Build and Test (Construction) · Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Estrategia Minimal.
> Ejecución en contenedor `node:22.22.3` (el Node local 22.22.1 < 22.22.3 que exige Angular CLI 22).

## Estado del build

- **`npm ci`**: OK — 400 paquetes, **0 vulnerabilidades**, sin stack de Karma, con Vitest 4.1.11 y jsdom.
- **`ng build` (producción)**: **FALLA** — el bundle inicial (1.03 MB) supera el presupuesto `maximumError: 1 MB` definido en `angular.json` (excede por 29.89 kB).
  - **Causa raíz**: tamaño del bundle inicial + presupuesto de 1 MB, **ambos preexistentes** al intent. `git diff` de `angular.json` confirma que este intent solo cambió `test.runner` (karma→vitest) y retiró `browsers`; **no** tocó el bloque `budgets`.
  - **Fuera de alcance**: ninguna de las 5 mejoras de CI/tooling modifica código de aplicación que afecte al tamaño del bundle. Debilitar el presupuesto está prohibido (regla de calidad).

## Resultados de tests

| Tipo | Comando | Total | Pasados | Fallidos | Omitidos |
|------|---------|-------|---------|----------|----------|
| Unit (frontend, Vitest) | `cd angular-app && npx ng test --watch=false` | 6 | 6 | 0 | 0 |

- Fichero de test: `src/app/core/interceptors/auth.interceptor.spec.ts` (migrado de Jasmine a Vitest).
- Sin regresión respecto a la línea base (BR4.3/FR4.5): los 6 casos que pasaban con Karma pasan con Vitest.
- Cobertura: no se define suelo nuevo (scope `refactor`, estrategia Minimal).

## Estrategia Minimal — ficheros de test adicionales

Según el stage file, la estrategia **Minimal** no genera `integration-test-instructions.md`, `performance-test-instructions.md` ni `security-test-instructions.md`. No hay NFR de rendimiento/seguridad nuevos en este intent (solo NFR4 de CI, verificado por inspección de workflows).

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| FR1-actions-node24 | requirements.md FR1 | setup-node a última major (Node 24), sin flag inseguro | `actions/setup-node@v5` en ci.yml y fly-deploy.yml; sin `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` | ci.yml, fly-deploy.yml | Met |
| FR2-punycode | requirements.md FR2 | DEP0040 eliminado o con nota de vigilancia | `punycode` fuera del lock tras retirar Karma; nota de vigilancia en codekb/dependencies.md | package-lock.json, dependencies.md | Met |
| FR3-animaciones | requirements.md FR3 | Sin aviso de deprecación de @angular/animations tras la mejora; provider conservado por Material | Sin uso de API antigua (0 grep); provider conservado; acoplamiento documentado | app.config.ts, architecture.md | Met |
| FR4-karma-vitest | requirements.md FR4 | runner vitest; sin restos de Karma; suite verde sin regresión | runner=vitest; karma.conf.js y devDeps Karma retirados; 6/6 tests verdes con Vitest | angular.json, package.json, test run | Met |
| FR5-node-local | requirements.md FR5 | .nvmrc >=22.22.3 + README | .nvmrc=22.22.3; sección en README | .nvmrc, README.md | Met |
| NFR4-ci-seguridad | requirements.md NFR4 | Sin runtime inseguro de Node en actions | Sin flag inseguro; actions a Node 24 | ci.yml, fly-deploy.yml | Met |
| BUILD-prod-budget | angular.json production budgets | Bundle inicial <= 1 MB | 1.03 MB (excede por 29.89 kB) | ng build output | Not Met (preexistente, fuera de alcance del intent) |

## Failure predicate

Build and Test ha fallado según el predicado del stage: `ng build` falla y el target `BUILD-prod-budget` está `Not Met`. No obstante, ese fallo es **preexistente y ajeno al alcance** de este intent de CI/tooling; los tests (criterio real de estas mejoras) pasan en verde. La resolución (optimizar el bundle o ajustar el presupuesto) queda fuera del scope `refactor` de CI/tooling y su decisión corresponde al humano (halt-and-ask, modo gated).
