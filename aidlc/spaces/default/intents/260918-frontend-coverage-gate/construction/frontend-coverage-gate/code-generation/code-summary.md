# Code Summary — frontend-coverage-gate (U1, packaging)

Intervención acotada y aditiva sobre `angular-app/` y los workflows de CI.
Metodología **test-after**, orden FR10 → FR17.1. No se reescribió ningún
componente ni servicio de negocio; solo se añadió infraestructura de cobertura
y specs sembrados. Verificado en contenedor `node:22.22.3`.

## Ficheros creados

Specs sembrados (co-located `*.spec.ts`, patrón Vitest + `@angular/*/testing`):

- `angular-app/src/app/core/guards/auth.guard.spec.ts` (P0, 5 tests)
- `angular-app/src/app/core/services/auth.service.spec.ts` (P0, 6 tests)
- `angular-app/src/app/core/services/budget.service.spec.ts` (P1, 4 tests)
- `angular-app/src/app/core/services/roster.service.spec.ts` (P1, 4 tests)
- `angular-app/src/app/core/services/favorites.service.spec.ts` (P1, 2 tests)
- `angular-app/src/app/core/services/championship.service.spec.ts` (P1, 3 tests)
- `angular-app/src/app/core/services/evolution.service.spec.ts` (P1, 2 tests)
- `angular-app/src/app/core/services/stats.service.spec.ts` (P1, 3 tests)
- `angular-app/src/app/core/services/sync.service.spec.ts` (P1, 5 tests)
- `angular-app/src/app/core/services/analytics.service.spec.ts` (P1, 5 tests)
- `angular-app/src/app/core/services/assistant.service.spec.ts` (P2, 5 tests)
- `angular-app/src/app/features/market/bid-dialog.component.spec.ts` (7 tests)

## Ficheros modificados

- `angular-app/angular.json` — schematics (`skipTests` retirado de
  service/guard/interceptor/class/component; mantenido en pipe/resolver/directive);
  target `test` con config de cobertura + umbrales.
- `angular-app/package.json` — `@vitest/coverage-v8` `4.1.11` en devDependencies.
- `angular-app/package-lock.json` — regenerado (bloqueo del proveedor de cobertura).
- `.github/workflows/ci.yml` — job `quality`, paso frontend documentado como
  bloqueante-con-cobertura (comando sin cambios).
- `.github/workflows/fly-deploy.yml` — job `verify`, ídem (comando sin cambios;
  cadena `needs:` intacta).

## Decisiones clave

### Corrección dirigida por el spike (Step 1) — claves de config exactas

El builder `@angular/build:unit-test` (schema con `additionalProperties: false`)
**NO** acepta un objeto anidado `coverage.*` (`coverage.all`, `coverage.include`,
`coverage.thresholds`) ni `codeCoverage`, como sugería la redacción del plan.
Las claves reales son **planas y de primer nivel**:

- `coverage: true` — activa la instrumentación (equivalente al `codeCoverage`/`coverage.all`
  del plan; no existe una clave `all` separada).
- `coverageInclude: ["src/app/**/*.ts"]` — denominador estable sobre TODO el
  código de la app. Se restringió a `*.ts` porque incluir `**` arrastra `.html`/`.scss`
  y el proveedor V8 lanza `PARSE_ERROR` (ruido no fatal) al intentar parsearlos como JS.
- `coverageExclude` — `**/*.spec.ts`, `**/*.test.ts`, `src/main.ts`, `**/*.config.ts`,
  `src/environments/**`, `**/*.d.ts`, `**/*.model.ts` (interfaces), `**/*.routes.ts`,
  `**/index.ts` (barrels).
- `coverageThresholds: { statements, branches, functions, lines }` — objeto plano.
- `coverageReporters: ["text-summary", "lcovonly"]`.

Se respeta la **intención** del plan (denominador estable, umbral por métrica,
fuente única en `angular.json`) con los nombres de clave que el builder realmente
acepta. Es una corrección mecánica de nomenclatura, no un cambio de alcance.

### Proveedor de cobertura

`@vitest/coverage-v8` fijado a **`4.1.11`** (versión exacta, sin rango), casada
con la `vitest` resuelta (`4.1.11`, de `^4.0.8`) para evitar mismatch de
instrumentación. Coste 0 € (OSS).

### Línea base medida y umbrales elegidos (Step 8)

Base medida sobre `src/app/**/*.ts` tras la siembra:

| Métrica     | Base medida | Umbral fijado | Colchón |
|-------------|-------------|---------------|---------|
| statements  | 19.2%       | **15**        | ~4.2    |
| branches    | 19.53%      | **15**        | ~4.5    |
| functions   | 17.26%      | **13**        | ~4.3    |
| lines       | 18.05%      | **14**        | ~4.1    |

Umbrales ~2–5 pts por debajo de la base, redondeados hacia abajo. Trinquete
**solo-arriba**: nunca se baja para pasar el gate.

## Cobertura de tests

62 tests en 14 ficheros, todos en verde en `node:22.22.3`. La suite existente
(`auth.interceptor.spec.ts`, `idle-preloading-strategy.spec.ts`) permanece
verde. Aserciones significativas (payload/headers/estado/URLs/params), fakes y
tokens inventados; sin secretos reales. El streaming SSE de `assistant.service`
se prueba con `fetch` mockeado por un `ReadableStream` determinista (elimina el
no-determinismo P2).

## Verificación (NFR5)

- `npm ci` + `npx ng test --watch=false` en `node:22.22.3` (volumen anónimo para
  `node_modules`): **exit 0**, 62/62, cobertura por encima de umbral.
- Fail-closed demostrado: con umbrales al 95% el builder sale **exit 1** con
  `ERROR: Coverage ... does not meet global threshold`. El enforcement vive
  DENTRO de `ng test`, sin pasos extra ni `continue-on-error`.
- JSON válido (`angular.json`, `package.json`, `package-lock.json`); YAML válido
  (ambos workflows).

## Trazabilidad

FR10.1 (skipTests), FR10.2/2.1/2.2/2.3 (proveedor + denominador + umbral),
FR10.3.1 (P0), FR10.3.2 (P1/P2), FR17.1 (gate en ci.yml + verify), NFR5 (verif.
en contenedor). Deuda diferida (Q8=A): paridad `--cov` de backend en `verify` y
SAST/DAST de frontend — fuera de alcance.
