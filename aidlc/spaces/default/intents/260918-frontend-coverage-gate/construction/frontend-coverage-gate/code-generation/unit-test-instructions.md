# Instrucciones de Test — frontend-coverage-gate

Unidad `frontend-coverage-gate` (kind `packaging`). Estrategia **standard** (5–8 tests por componente sembrado), metodología **test-after**. Los specs son adyacentes a su fuente en `angular-app/src/app/**`.

## Framework y configuración

- Runner: **Vitest** (`^4.0.8`) + `jsdom` (`^25.0.1`) vía el builder `@angular/build:unit-test` (`angular.json` → `architect.test.runner: vitest`, `tsConfig: angular-app/tsconfig.spec.json`, `buildTarget: angular-app:build:development`). Ya existe; no se cambia el runner.
- Proveedor de cobertura a añadir: `@vitest/coverage-v8` a versión exacta casada en major con Vitest 4.x. Config de cobertura en el target `test` de `angular.json` (fuente única): `coverage.all: true`, `coverage.include: ["src/app/**"]`, `coverage.exclude` explícito, `coverage.thresholds` por métrica.
- Node: `22.22.3` (`.nvmrc`). Verificar en contenedor `node:22.22.3` (volumen anónimo para `node_modules`) antes de pushear cambios de devDependencies.

## Cómo ejecutar los tests DE ESTA UNIDAD (comando exacto)

El intent afecta a toda la suite de tests del frontend (config de cobertura global), así que el comando unit-scoped es la suite de `angular-app` con cobertura, ejecutada desde el directorio de la app:

```bash
# desde angular-app/ (o en contenedor node:22.22.3):
npm ci
npx ng test --watch=false
```

`ng test` aplica la cobertura y los umbrales declarados en el target `test` de `angular.json` (una vez añadidos en el Step 5/8 del plan). No usar un comando de otra unidad; no hay otras unidades. Verificación de arranque (runner readiness) antes del primer spec sembrado: `npx ng test --watch=false` debe ejecutar los 2 specs existentes en verde.

## Objetivos de cobertura

- Por métrica (`lines`, `branches`, `functions`, `statements`) sobre `src/app/**` (denominador estable con `coverage.all: true`).
- Umbral inicial medido tras la siembra P0 y fijado ligeramente por debajo de la base (colchón 2–5 pts). Trinquete solo-arriba; nunca se baja para pasar el gate.

## Guía de mocking/stubbing

- Servicios HTTP (`core/services/*`): `TestBed.configureTestingModule` con `provideHttpClient(withInterceptors([...]))` + `provideHttpClientTesting()`; `HttpTestingController.expectOne(...).flush(...)` y `httpMock.verify()`.
- Guard `CanActivateFn` (`auth.guard`): invocar dentro de `TestBed.runInInjectionContext(...)`; dependencias mockeadas por `useValue` con `vi.fn()`.
- Interceptor (`auth.interceptor`): patrón ya establecido en `auth.interceptor.spec.ts` (Bearer, refresh en cola ante 401, `withCredentials` para `/auth/*`).
- Componente bid-dialog: standalone + signals + `HttpClient`; TestBed con `provideHttpClientTesting`.
- Timers: `vi.useFakeTimers()` donde aplique (patrón de `idle-preloading-strategy.spec.ts`).

## Gestión de datos de test

- Datos deterministas, sin red ni `sleep`. Tokens/payloads de auth **inventados** (fakes), nunca secretos ni tokens reales (gitleaks escanea `*.spec.ts`). Cada test crea y limpia su propio estado; sin estado mutable compartido.

## Aserciones significativas

- Verificar payload, headers, y estado esperados; nunca el anti-patrón `expect(true).toBe(true)`. `branches`/`functions` en el umbral detectan tests-espejo sin aserciones.
