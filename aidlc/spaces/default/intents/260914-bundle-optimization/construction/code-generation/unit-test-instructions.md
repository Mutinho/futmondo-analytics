# Unit Test Instructions — Optimización del bundle inicial

> Stage 3.5 Code Generation · Intent `260914-bundle-optimization` · scope `refactor` · Test Strategy Minimal · brownfield.
> Metodología del Testing Contract: `test-after`. Runner: Vitest vía `@angular/build:unit-test`.

## Framework y configuración

- Test runner: **Vitest**, ejecutado por el builder `@angular/build:unit-test` de Angular 22 (definido en `angular.json` → `projects.angular-app.architect.test`, `tsConfig: tsconfig.spec.json`).
- No se añade ni cambia ninguna dependencia de test (coste 0 €, NFR3). El runner ya está operativo en el proyecto.
- Los componentes del proyecto usan `skipTests: true` por convención (`angular.json` schematics); la verificación funcional de los componentes de gráficos y chat es **manual** (BR5.1), no vía specs de componente nuevos.

## Comando exacto scoped a esta unidad

El único spec **nuevo** de esta unidad es la lógica de la estrategia de precarga. Ejecutarlo aislado con el filtro de Vitest:

```bash
cd angular-app && npx ng test --no-watch --include "src/app/core/preloading/idle-preloading-strategy.spec.ts"
```

Si el flag `--include` no estuviera soportado por esta versión del builder, filtrar por nombre de fichero con Vitest:

```bash
cd angular-app && npx ng test --no-watch -- --run idle-preloading-strategy
```

> No usar `npm test` / `ng test` sin filtro: Build and Test ejecuta el comando de cada unidad y un comando sin scope reejecutaría toda la suite.

## Verificación de no regresión (suite completa — una sola vez, NFR2/BR5.1)

Además del spec scoped, esta unidad exige que la suite existente completa siga verde (es una obligación de no-regresión del refactor, no un test nuevo por unidad):

```bash
cd angular-app && npx ng test --no-watch
```

Si el Node local no alcanza el mínimo del Angular CLI 22, ejecutar en contenedor `node:<versión de .nvmrc>` con volumen anónimo para `node_modules` (regla de proyecto, coste 0 €):

```bash
docker run --rm -v "$PWD/angular-app":/app -v /app/node_modules -w /app node:22.22.3 \
  sh -c "npm ci && npx ng test --no-watch"
```

## Alcance de tests (Minimal + floor de refactor)

- **Nuevo spec** (`idle-preloading-strategy.spec.ts`): 3–4 tests sobre la lógica pura de la estrategia:
  - happy-path: precarga la ruta tras detectar inactividad/retardo.
  - edge: NO precarga inmediatamente (antes del idle).
  - edge: rutas marcadas `data.preload === false` o sin `loadChildren`/`loadComponent` no se cargan (`EMPTY`/`of(null)`).
- **Suite existente**: debe permanecer verde (BR5.1). El scope `refactor` no añade floor de tests nuevos más allá de la Test Strategy Minimal.

## Coverage objetivo

- Test Strategy Minimal: un test verificable por requisito al nivel más estrecho + happy-path por componente de lógica. No hay floor de línea (refactor no añade el 80 %).
- La estrategia de precarga (única pieza de lógica pura nueva) debe quedar cubierta en su happy-path y sus dos ramas de "no precargar".

## Mocking / stubbing

- Usar **fake timers** de Vitest (`vi.useFakeTimers()`) para simular el retardo/inactividad sin espera real.
- Stub de `requestIdleCallback`/`cancelIdleCallback` cuando no existan en el entorno de test (jsdom): fallback a `setTimeout` y avanzar el reloj con `vi.advanceTimersByTime()`.
- Mock del callback `load` de cada `Route` con un spy para verificar si se invocó o no.

## Gestión de datos de test

- No hay datos de negocio implicados. Los tests construyen objetos `Route` sintéticos en memoria (`{ path, loadComponent: () => Promise.resolve(...) }`) y un spy de `load`.
