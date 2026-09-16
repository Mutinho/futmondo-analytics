# Developer Code Scan — Enlace 1 (Reverse Engineering)

Escaneo enfocado del frontend Angular `angular-app/` para el eje de optimización del
bundle inicial. Brownfield · scope `refactor` · profundidad Minimal. Sin cambio funcional,
coste 0€. Este documento es el handoff para que el arquitecto sintetice los 9 artefactos
codekb en el enlace 2; no escribe esos artefactos.

## Developer Code Scan Results

### Scan Coverage

- **Analyzed deeply** (todo dentro de `angular-app/`):
  - `angular-app/package.json`
  - `angular-app/package-lock.json` (versiones resueltas de las libs pesadas y sus deps/peers)
  - `angular-app/angular.json` (builder, budgets, optimización, service worker)
  - `angular-app/tsconfig.json`, `angular-app/tsconfig.app.json`
  - `angular-app/eslint.config.js`
  - `angular-app/src/main.ts`
  - `angular-app/src/styles.scss`
  - `angular-app/src/app/app.config.ts`, `app.ts`, `app.routes.ts`
  - `angular-app/src/app/features/analytics/analytics.routes.ts`, `features/budget/budget.routes.ts`
  - `angular-app/src/app/shared/components/assistant-fab.component.ts`, `assistant-chat.component.ts`
  - `angular-app/src/app/features/evolution/evolution.component.ts`, `features/stats/stats.component.ts` (consumidores de Chart.js)
  - Búsqueda exhaustiva de imports de `chart.js`, `ng2-charts`, `marked` en todo `angular-app/src/`
  - Inventario de árbol de `angular-app/src/app/` (features, shared, core)
- **Skimmed only** (superficial, solo contexto; fuera del foco profundo):
  - `angular-app/ngsw-config.json`, `Dockerfile`, `nginx.conf`, `nginx.prod.conf`, `fly.toml` (empaquetado/serving; no afectan a la composición del chunk inicial)
  - Raíz del repo (`README.md`, `docker-compose.yml`) y `backend/` — NO analizados en profundidad (fuera de `angular-app/`)
  - `angular-app/node_modules.old-1789382239/` — directorio residual de una instalación previa; ruido, ignorado

### Packages Found

- `angular-app` — application (Angular 22, standalone, PWA) — TypeScript — el único paquete del scope.

### Build System

- **Type**: npm (`packageManager: npm@11.12.1`); Angular CLI 22 con builder `@angular/build:application` (esbuild/vite, no Webpack).
- **Config Files**: `angular.json`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.spec.json`, `.nvmrc` (raíz repo, Node `22.22.3`).
- **Build Dependencies**: `@angular/build`, `@angular/cli`, `@angular/compiler-cli` (devDependencies). `test` usa el runner `vitest` vía `@angular/build:unit-test`.
- **Budgets actuales** (`configurations.production.budgets`, tipo `initial`):
  - `maximumWarning`: `1MB`
  - `maximumError`: `1.2MB`  ← el intent pide **restaurar `maximumError` a `1MB`**. Hoy está relajado a `1.2MB`, señal de que el bundle inicial ya rebasó 1 MB y se subió el techo para no romper el build.
  - `anyComponentStyle`: warning `8kB` / error `12kB`.
- Optimización production: `scripts: true`, `styles.minify: true`, `styles.inlineCritical: false`, `outputHashing: all`, `serviceWorker: ngsw-config.json`.

### APIs Discovered

- No aplica al eje del bundle (frontend SPA). El SPA consume una API REST backend vía `/api/v1/*` y `/auth/*` a través de `proxy.conf.json` (dev) / nginx (prod). Fuera del foco profundo.

### Frameworks & Libraries

Versiones resueltas en `package-lock.json` (lockfileVersion 3):

- `@angular/*` (animations, cdk, common, compiler, core, forms, material, platform-browser, router, service-worker) — `22.1.x` — framework + Material Design.
- `@angular/material` — `22.1.6` (peer: cdk, common, core, forms, platform-browser, rxjs) — **lib pesada**.
- `@angular/cdk` — `22.1.6` (dep transitiva: `parse5`).
- `chart.js` — `4.5.1` (dep: `@kurkle/color@0.3.4`) — **lib pesada**; gráficos.
- `ng2-charts` — `10.0.0` (deps: `es-toolkit`, `tslib`; peers: `@angular/*`, `chart.js`, `rxjs`) — wrapper Angular de Chart.js.
- `marked` — `18.0.13` — **lib pesada**; parser Markdown, usado solo por el chat del asistente.
- `rxjs` — `7.8.2`; `tslib` — `2.8.1`.
- Test: `vitest@^4.0.8` + `jsdom@^25` (devDependencies). No hay karma/jasmine (migrado a `@angular/build:unit-test` con runner vitest).
- Lint: ESLint flat config (`eslint.config.js`) con `typescript-eslint` y `angular-eslint`; hoy en modo **advisory** (las reglas base degradadas a `warn`; las devDependencies de eslint aún NO están instaladas — se añadirán al pasar el gate a bloqueante).

### Test Coverage

- **Test Directories**: co-located `*.spec.ts` en `src/`. Presencia mínima: prácticamente solo `src/app/core/interceptors/auth.interceptor.spec.ts`.
- **Test Frameworks**: Vitest (runner) + jsdom, vía builder `@angular/build:unit-test` (`tsConfig: tsconfig.spec.json`).
- **Coverage Config**: no configurado explícitamente. Schematics generan componentes con `skipTests: true`, de ahí la cobertura casi nula. Bajo scope `refactor` no hay nuevo floor de tests; la suite existente debe seguir verde.

### Code Quality Indicators

- **Linting**: ESLint flat config presente pero advisory (no bloqueante) y con toolchain aún sin instalar; Prettier (`.prettierrc`) para formato JS/TS.
- **CI/CD**: fuera del foco profundo; el deploy es Fly.io + GitHub Actions (contexto de repo, skimmed).
- **Documentation**: `README.md` del app y raíz presentes.
- **Arquitectura frontend**: standalone components (sin NgModules), routing 100% con `loadComponent`/`loadChildren` (lazy por ruta), signals, `ChangeDetectionStrategy.OnPush` en varios componentes. Estructura por feature (`features/<x>/`), con `core/` (services, guards, interceptors, models) y `shared/` (components, utils, pipes, styles).

### Technical Debt Signals (relevantes al bundle inicial)

1. **`provideCharts(withDefaultRegisterables())` en `src/app/app.config.ts`** (líneas 5 y 17): registra Chart.js con TODOS los "registerables" a nivel de `ApplicationConfig`, que se evalúa en el arranque (`main.ts` → `bootstrapApplication(App, appConfig)`). Esto arrastra **`chart.js` + `ng2-charts` al bundle inicial** de forma **eager**, aunque los únicos consumidores de gráficos son rutas **lazy** (`features/evolution` y `features/stats`, que importan `BaseChartDirective` + `chart.js`). Es el mayor candidato de peso evitable en el chunk inicial.
2. **`withPreloading(PreloadAllModules)` en `src/app/app.config.ts`**: aunque las rutas son lazy, esta estrategia **precarga todos los chunks lazy** en cuanto la app estabiliza. No engorda el chunk `initial` medido por el budget, pero anula en la práctica el beneficio de red del lazy-loading (descarga todo poco después del arranque). A revisar frente al objetivo real de "bajar de 1 MB" (el budget mide `initial`, no el total precargado).
3. **`marked@18` en el bundle inicial vía cadena eager**: `App` (root, eager) → `imports: [AssistantFabComponent]` → `AssistantFabComponent` importa estáticamente `AssistantChatComponent` → `AssistantChatComponent` importa estáticamente `marked` (`src/app/shared/components/assistant-chat.component.ts:10`). El chat se renderiza tras `@if (chatOpen())`, pero el import estático mete `marked` en el initial chunk igualmente. Candidato a carga diferida (import dinámico de `marked` o del propio chat).
4. **Carga de Angular Material**: `src/app/app.ts` importa múltiples módulos Material (sidenav, toolbar, list, icon, button, select, form-field) + CDK (layout, scrolling) en el shell raíz — necesarios para el chrome de la app, por lo que son legítimamente eager; el margen está más en tree-shaking/uso puntual que en diferirlos. `styles.scss` incluye el theming Material (`@use '@angular/material'` + `mat.theme(...)`), coste de CSS inicial.
5. **`budgets.maximumError` relajado a `1.2MB`**: es el síntoma que el intent quiere revertir. Restaurar a `1MB` sin antes recortar (1)+(3) haría fallar el build de production; el orden correcto es recortar primero, restaurar el budget después.

## Handoff Summary

- **Intent-relevant finding**: El bundle inicial excede 1 MB principalmente por **tres cargas eager evitables**, todas concentradas en dos ficheros:
  1. `src/app/app.config.ts` → `provideCharts(withDefaultRegisterables())` arrastra `chart.js@4.5.1` + `ng2-charts@10.0.0` (+ `@kurkle/color`) al chunk inicial pese a que solo los usan rutas lazy (`features/evolution`, `features/stats`).
  2. Cadena `src/app/app.ts` → `AssistantFabComponent` → `AssistantChatComponent` → `import { marked } from 'marked'` (`assistant-chat.component.ts:10`) mete `marked@18.0.13` en el inicial aunque el chat va tras `@if`.
  3. `src/app/app.config.ts` → `withPreloading(PreloadAllModules)` precarga todos los chunks lazy tras el arranque (impacta transferencia total, no el budget `initial`).
  El budget objetivo vive en `angular.json` (`configurations.production.budgets`, `type: initial`): hoy `maximumError: 1.2MB` / `maximumWarning: 1MB`; el intent pide restaurar `maximumError` a `1MB`.
- **Risks / follow-up**:
  - Restaurar `maximumError` a `1MB` **antes** de recortar las cargas eager romperá el build de production (fail-closed del budget). Orden: primero mover Chart.js/ng2-charts y `marked` fuera del inicial (registro de charts a nivel de las rutas/componentes lazy que los usan; import diferido de `marked` o del chat), luego bajar el budget.
  - Sin cambio funcional: los gráficos de `evolution`/`stats` y el chat del asistente deben seguir operando; validar tras diferir.
  - Testing (scope `refactor`): no hay nuevo floor de tests, pero la suite existente (mínima, esencialmente `auth.interceptor.spec.ts`) debe permanecer verde; verificar `npm ci` + `ng test`/build. El Node local puede no alcanzar el mínimo del Angular CLI 22 → usar contenedor `node:22.22.3` (`.nvmrc`), coste 0€.
  - `PreloadAllModules` es una decisión de UX (velocidad de navegación) vs. peso de red inicial; su cambio debe documentarse con tradeoff (guardrail Inception) porque puede alterar la percepción de rendimiento aunque no toque el chunk `initial`.
  - Coste 0€: todas las mejaras propuestas son de configuración/estructura de imports; ninguna introduce dependencias nuevas ni gasto recurrente.
