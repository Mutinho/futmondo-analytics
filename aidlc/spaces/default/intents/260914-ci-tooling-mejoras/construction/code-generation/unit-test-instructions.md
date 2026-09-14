# Instrucciones de Test — Mejoras de CI/Tooling

> Etapa Code Generation (Construction) · Intent `260914-ci-tooling-mejoras` · Scope `refactor` · Estrategia de test: Minimal · Metodología: test-after (Testing Contract).

## Alcance de tests para este intent

Scope `refactor`: **no se añade suelo de tests nuevo** (Testing Contract: `poc/refactor/workshop` no añaden nuevo suelo). Este intent son 5 mejoras de CI/tooling, dependencias y configuración de entorno; no introduce unidades de negocio testeables (sin modelo de datos, repositorios, lógica ni endpoints nuevos). Por tanto:

- **No se escriben tests unitarios nuevos.**
- La obligación es **mantener verde la suite de tests existente del frontend** tras cada mejora (BR6.1, FR6.2, NFR2), y que el pipeline `fly-deploy.yml` siga desplegando.

## Framework de test y configuración

- **Runner actual**: Angular `@angular/build:unit-test` con `runner: karma` (línea base).
- **Runner objetivo tras la mejora 4**: `runner: vitest` en `angular-app/angular.json`.
- La configuración de test se gestiona vía `angular.json`; Vitest no requiere navegador (a diferencia de Karma con ChromeHeadless), pero necesita un entorno DOM (`jsdom`, devDependency añadida) para los tests de Angular/TestBed.

## Cómo ejecutar los tests de este trabajo (comando scoped al frontend)

Comando exacto, scoped únicamente al frontend (no `npm test` global de raíz):

```bash
cd angular-app && npm ci && npx ng test --watch=false
```

Si el Node local es < 22.22.3 (Angular CLI 22 lo exige), usar un contenedor efímero con la versión correcta (coste 0€, sin navegador):

```bash
docker run --rm \
  -v "$PWD/angular-app":/app -w /app \
  -v /app/node_modules \
  node:22.22.3 \
  bash -c "npm ci && npx ng test --watch=false"
```

Verificado el 2026-09-14 en `node:22.22.3`: **6 tests, 6 pasados** con Vitest 4.1.11 (entorno jsdom), 0 vulnerabilidades.

Verificación pre-push obligatoria tras cambiar devDependencies del frontend (BR4.4, project.md ## Corrections):

```bash
cd angular-app && npm ci && npx ng test --watch=false
```

(o revisar el `package-lock.json` si no es posible ejecutar en local).

## Objetivos de cobertura

- No se define suelo de cobertura nuevo (scope `refactor`, sin nuevo suelo de tests).
- Objetivo de no regresión: **el conjunto de tests que pasaba en verde antes debe seguir pasando** tras cada mejora, en local y en CI.

## Guía de mocking/stubbing

- No aplica trabajo de mocking nuevo: no se escriben tests nuevos.
- En la migración a Vitest, si algún spec existente usa APIs específicas de Jasmine/Karma que Vitest no expone igual, se ajusta el spec (o su import) lo mínimo para conservar la aserción original — nunca relajando la aserción para "hacer pasar" el test.

## Gestión de datos de test

- No aplica: no hay datos de test nuevos. Los specs existentes conservan sus propios datos.

## Criterio de "hecho" de la fase de test

1. Línea base Karma registrada en verde antes de la mejora 4.
2. Tras cada mejora, `npx ng test --watch=false` (scoped al frontend) en verde.
3. Tras la mejora 4, suite en verde con Vitest sin regresión respecto a la línea base y sin restos de Karma.
4. Pipeline `fly-deploy.yml` sigue desplegando (BR6.1).
