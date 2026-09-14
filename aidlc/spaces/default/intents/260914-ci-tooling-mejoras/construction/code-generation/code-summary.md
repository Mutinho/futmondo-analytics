# Resumen de Código — Mejoras de CI/Tooling

> Etapa Code Generation (Construction) · Intent `260914-ci-tooling-mejoras` · Scope `refactor`.

## Ficheros creados/modificados

| Fichero | Cambio | Mejora |
|---------|--------|--------|
| `.github/workflows/ci.yml` | `actions/setup-node@v4`→`@v5`; retirado `setup-chrome` y `--browsers=ChromeHeadless`; test frontend con Vitest | 1, 4 |
| `.github/workflows/fly-deploy.yml` | `actions/setup-node@v4`→`@v5`; retirado `setup-chrome` y `--browsers=ChromeHeadless`; test frontend con Vitest | 1, 4 |
| `.nvmrc` | Creado con `22.22.3` | 5 |
| `README.md` | Sección "Versión de Node (desarrollo local)" con `nvm use`/`.nvmrc` | 5 |
| `angular-app/angular.json` | `test.runner` `karma`→`vitest`; retirado `browsers` | 4 |
| `angular-app/package.json` | Retiradas devDeps de Karma + `jasmine-core`/`@types/jasmine`; añadido `vitest@^4.0.8` y `jsdom@^25.0.1` (entorno DOM para Vitest) | 2, 4 |
| `angular-app/package-lock.json` | Regenerado (npm 11.12.1): sin Karma, con Vitest, sin `punycode` | 2, 4 |
| `angular-app/tsconfig.spec.json` | `types: ["jasmine"]`→`["vitest/globals"]` | 4 |
| `angular-app/karma.conf.js` | Eliminado | 4 |
| `angular-app/src/app/core/interceptors/auth.interceptor.spec.ts` | Migrado de Jasmine a Vitest (mismas aserciones) | 4 |
| `aidlc/spaces/default/codekb/futmondo-analytics/dependencies.md` | Nota de vigilancia de `punycode` (cadena transitiva + resolución) | 2 |
| `aidlc/spaces/default/codekb/futmondo-analytics/architecture.md` | Documentado acoplamiento Material↔animaciones + observación de vigilancia | 3 |

## Decisiones clave

- **Mejora 1 (Actions)**: solo `actions/setup-node@v4` usaba una major susceptible de subir; `checkout@v5`, `setup-python@v5`, `gitleaks-action@v2` ya cumplen Node 24. `flyctl-actions/setup-flyctl@master` es un script de superfly (no JS action con runtime Node de GitHub). Sin `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` (BR1.2 cumplida).
- **Mejora 1 (Actions) — corrección post-ejecución (2026-09-14)**: los logs reales del workflow mostraron que `actions/setup-python@v5` y `gitleaks/gitleaks-action@v2` **aún declaraban Node 20** (aviso de deprecación del runner). Corregido: `setup-python@v5→@v6` (usa `node24`, verificado en su `action.yml`) en `ci.yml` y `fly-deploy.yml`, y `gitleaks-action@v2→@v3` (usa `node24`, misma interfaz, sin coste para usuario individual) en `ci.yml`. Con esto, todas las JS actions de GitHub usan Node 24. Vigilancia: la licencia de gitleaks-action v3 es gratuita solo para uso individual.
- **Mejora 2 (punycode)**: se resuelve por la mejora 4. La cadena `dom-serialize → ent → punycode@1.4.1` era `dev` del stack de Karma; tras retirar Karma, `punycode` desaparece del lock (0 entradas). Nota de vigilancia registrada.
- **Mejora 3 (animaciones)**: sin migración (0 uso de la API antigua verificado). Se conserva `provideAnimationsAsync()` y `@angular/animations` por Angular Material (BR3.2). Acoplamiento y observación documentados (BR3.3).
- **Mejora 4 (Karma→Vitest)**: runner cambiado; Karma y Jasmine retirados; único spec migrado a Vitest; `vitest@^4.0.8` por peer de `@angular/build`. CI simplificado (sin Chrome headless).
- **Mejora 5 (Node local)**: `.nvmrc` = `22.22.3` (≥ la línea 22 de CI) + doc en README.

## Cobertura de tests

- Scope `refactor`: sin nuevo suelo de tests. No se crean tests nuevos.
- Único spec existente migrado a Vitest conservando sus 6 casos (Bearer, exclusión auth+withCredentials, sin token, 401→refresh+reintento, 401 refresh fallido→logout, 403→logout).
- **Verificado el 2026-09-14** en contenedor `node:22.22.3`: `ng test --watch=false` con Vitest 4.1.11 (entorno jsdom) → **6 tests, 6 pasados**, 0 vulnerabilidades. No regresión confirmada (BR4.3/FR4.5).
- Criterio de no regresión: suite existente en verde + pipeline operativo (BR6.1).

## Desviaciones respecto al plan

- **`ng test` verificado en contenedor `node:22.22.3`**: el Node local (22.22.1) es inferior al mínimo que exige Angular CLI 22 (22.22.3), así que la verificación se ejecutó en un contenedor efímero con la versión correcta. Resultado: 6/6 tests verdes con Vitest.
- **`jsdom@^25.0.1` añadido**: Vitest corre en Node y necesita un entorno DOM para los tests de Angular/TestBed (Karma usaba un navegador real). Tier gratuito, coste 0€.
- **npm 11.12.1 / contenedor node:22.22.3**: el npm 9.2.0 del entorno host fallaba al resolver el árbol de Angular 22/Vitest 4 (`edgesOut`); se usó el `packageManager` declarado / la imagen oficial para regenerar el lock correctamente.
- **`vitest` fijado a `^4.0.8`** (no 3.x) por el peer de `@angular/build`.

## Verificación pendiente en fases posteriores

- Ejecución de `ng test` con Vitest en CI (Node 22) para confirmar la línea base verde sin regresión (BR4.3) — ya verificado en local vía contenedor `node:22.22.3` (6/6 verdes); CI lo confirma en su entorno — etapa Build and Test.
- Desaparición efectiva del aviso DEP0040 en la salida de CI/build (el lock ya no contiene `punycode`).
- `fly-deploy.yml` sigue desplegando (BR6.1).
