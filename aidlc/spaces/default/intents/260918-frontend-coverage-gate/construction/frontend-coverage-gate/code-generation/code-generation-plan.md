# Plan de Generación de Código — frontend-coverage-gate

Unidad `U1` `frontend-coverage-gate` (kind `packaging`). Intervención acotada y aditiva sobre `angular-app/` y los workflows de CI. Metodología **test-after** (ver Testing Contract embebido). Orden interno obligado FR10 → FR17.1. NO se reescriben componentes/servicios de negocio; se formatea SOLO lo nuevo (nunca reformateo en masa). Node `22.22.3`; verificar `npm ci` + `ng test` en `node:22.22.3` antes de pushear.

## Pasos de implementación

- [x] **Step 1 — Spike de cableado/medición (valida A2/A3).** En un contenedor `node:22.22.3` con volumen anónimo para `node_modules`: `npm ci` en `angular-app/`, confirmar la sintaxis exacta de las opciones `coverage.*` del builder `@angular/build:unit-test` en el target `test` de `angular.json` (A2) y que `ng test --watch=false` con cobertura ejerce el umbral (A3). Registrar el comando exacto. (Riesgo R-01/R-03; risk-first.) → FR10.2, FR17.1
- [x] **Step 2 — Runner readiness.** Verificar el runner Vitest existente (`architect.test.runner: vitest`, `tsConfig: tsconfig.spec.json`) y registrar el comando unit-scoped exacto en `unit-test-instructions.md`. → contrato (runner antes del primer test)
- [x] **Step 3 — FR10.1: retirar `skipTests`.** En `angular-app/angular.json`, retirar `skipTests: true` de los schematics `service`, `guard`, `interceptor`, `class`, `component`; **mantenerlo** en `pipe`, `resolver`, `directive`. No genera specs retroactivos. → FR10.1
- [x] **Step 4 — FR10.2: proveedor de cobertura.** Añadir `@vitest/coverage-v8` a `devDependencies` de `angular-app/package.json` a **versión exacta** casada en major con `vitest ^4.0.8` (p. ej. `4.0.8`); regenerar `package-lock.json` con `npm install`. Verificar con `npm ci` + `ng test` en `node:22.22.3`. → FR10.2, NFR1.1, NFR5
- [x] **Step 5 — FR10.2.1: denominador estable.** En el target `test` de `angular.json` (opciones del builder), declarar `coverage.all: true`, `coverage.include: ["src/app/**"]`, `coverage.exclude` explícito (`**/*.spec.ts`, `src/main.ts`, `**/*.config.ts`, `src/environments/**`, `**/*.d.ts`, mocks, barrels). Fuente única de umbral. → FR10.2.1
- [x] **Step 6 — FR10.3.1 (P0 duro): sembrar specs P0.** Escribir `core/guards/auth.guard.ts` spec (invocado con `TestBed.runInInjectionContext`) y `core/services/auth.service.ts` spec (`provideHttpClient(withInterceptors)` + `provideHttpClientTesting`, `HttpTestingController`), con aserciones reales (payload/headers/estado), fakes/dobles, sin secretos reales. Adyacentes a su fuente. → FR10.3.1, NFR4
- [x] **Step 7 — FR10.3.2 (P1/P2 guía): sembrar specs de fase 1 restantes.** Replicar el patrón en los demás `core/services/*` (P1: CRUD con `HttpTestingController`; P2: `assistant.service` posible no-determinismo), `core/interceptors/auth.interceptor` (ya tiene spec — verificar), y el componente bid-dialog del mercado (standalone + signals + `HttpClient`). Aserciones significativas. → FR10.3.2
- [x] **Step 8 — Medir base y fijar umbral (FR10.2.2/2.3).** Ejecutar `ng test` con cobertura, medir la línea base por métrica sobre `src/app/**`, y declarar `coverage.thresholds` por métrica (`lines`, `branches`, `functions`, `statements`) **ligeramente por debajo** de la base medida (colchón 2–5 pts, redondeo hacia abajo). Trinquete solo-arriba. → FR10.2.2, FR10.2.3, NFR3
- [x] **Step 9 — FR17.1: cablear el gate en CI.** Corregir el comando `ng test --watch=false` en `.github/workflows/ci.yml` (job `quality`) y en el job `verify` de `.github/workflows/fly-deploy.yml` para que ejerza la cobertura (flag del builder o default del target `test`). Mantener bloqueante; sin `continue-on-error` sustitutivo; sin cambiar la cadena `needs:`. → FR17.1, FR17.1.2
- [x] **Step 10 — Verificación local (NFR5).** `npm ci` + `ng test --watch=false` (con cobertura) en `node:22.22.3`; confirmar que la suite existente sigue en verde y que el umbral pasa contra la base. → NFR3, NFR5
- [x] **Step 11 — Documentación y trazabilidad.** `code-summary.md`, `source-manifest.json` (todo path tocado en `angular-app/` y `.github/workflows/`), `traceability.json`.

## Nota de aplicabilidad del contrato a esta unidad packaging

Las capas testables genéricas del `plan_profile` (data model, repository, API endpoint) son N/A para esta unidad de tooling: no hay backend nuevo. La capa aplicable es **Frontend behavior** — pero test-after aquí significa que el "código" que se prueba es el **existente** (servicios/guard/interceptor/componente ya implementados), y lo que se genera es la **infraestructura de cobertura + los specs sembrados**. El orden efectivo es el del `ordering` del contrato (siembra P0 → config/umbral → gate), no la secuencia por-capa genérica. La suite existente permanece en verde (obligación de scope).

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "sembrar specs de la capa `core/` crítica (servicios + `auth.guard` + `auth.interceptor`) más el componente de puja del mercado -> configurar cobertura en el target `test` de `angular.json` con `coverage.all: true` + `coverage.include: src/app/**` + excludes y umbrales por métrica -> medir la línea base y fijar el umbral inicial por debajo -> cablear el gate corrigiendo el comando `ng test` en `ci.yml` Y en el job `verify`; la suite existente permanece en verde.",
  "scope": "classic",
  "test_strategy": "standard",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "- **Methodology**: test-after\n- **Ordering**: sembrar specs de la capa `core/` crítica (servicios + `auth.guard` + `auth.interceptor`) más el componente de puja del mercado -> configurar cobertura en el target `test` de `angular.json` con `coverage.all: true` + `coverage.include: src/app/**` + excludes y umbrales por métrica -> medir la línea base y fijar el umbral inicial por debajo -> cablear el gate corrigiendo el comando `ng test` en `ci.yml` Y en el job `verify`; la suite existente permanece en verde.\n\nDetalle del orden y del encuadre para este intent (aditivo sobre la posture afirmada):\n\n1. **Encuadre — NO es characterization-first.** La posture afirmada previa era\n   backend/`sync_prizes`-específica (congelar la producción del premio de un god-file).\n   ESTE intent es distinto: **añadir infraestructura de cobertura** a un frontend que\n   hoy casi no tiene specs (**2 specs sobre 71 fuentes `*.ts`**, cifra medida por la\n   revisión de calidad), no congelar el comportamiento de un artefacto único. El marco\n   es **test-after** con un orden seguro de siembra.\n\n2. **Denominador de cobertura (Q1=A — resuelve la objeción principal de calidad).**\n   El `tsconfig.spec.json` actual solo incluye `*.spec.ts`, así que la cobertura V8 por\n   defecto mediría **únicamente los ficheros ya probados**: un umbral así es\n   engañosamente alto y **caería** al sembrar más specs (crece el denominador),\n   rompiendo el trinquete. Fijamos el universo de cobertura desde el día 1 en el target\n   `test` de `angular.json`:\n   - `coverage.all: true`\n   - `coverage.include: src/app/**`\n   - `coverage.exclude` explícito: `*.spec.ts`, `main.ts`, `*.config.ts`, `environments/*`,\n     `*.d.ts`, mocks y barrels.\n   El umbral mide el código de la app **completo** desde el principio, para que el\n   ratchet sea honesto y no descienda al añadir specs.\n\n3. **Fase siembra (Q4=B — antes de activar el umbral bloqueante).** Escribir specs para\n   las piezas transversales críticas primero, replicando el patrón Vitest +\n   `@angular/*/testing` ya establecido por los 2 specs existentes\n   (`core/interceptors/auth.interceptor.spec.ts`,\n   `core/preloading/idle-preloading-strategy.spec.ts`). Alcance de fase 1:\n   - **`core/` crítica**: los 10 servicios HTTP de `core/services/*`\n     (`analytics`, `assistant`, `auth`, `budget`, `championship`, `evolution`,\n     `favorites`, `roster`, `stats`, `sync`), el guard `core/guards/auth.guard.ts`\n     (hoy SIN spec) y el interceptor `core/interceptors/auth.interceptor.ts`.\n   - **más un componente `features/*` de alto valor**: el **diálogo de puja del mercado**\n     (bid-dialog), para validar el patrón de test de componente standalone + signals +\n     `HttpClient` antes de que el trinquete empuje a más componentes.\n   Prioridad fina (por valor/coste, determinista y sin red): P0 `auth.guard.ts` y\n   `auth.service.ts`; P1 servicios HTTP CRUD (`HttpTestingController`); P2\n   `assistant.service.ts` (posible no-determinismo por streaming). El resto de\n   `features/*` y `shared/*` entra en rondas posteriores del trinquete.\n\n4. **Fase infraestructura + umbral (Q2=A, Q3=A, ratcheting).** Añadir\n   `@vitest/coverage-v8` como devDependency **a versión fijada** (cambio de\n   `package.json`/`package-lock.json`), declarar `coverage.provider` y\n   `coverage.thresholds` en el target `test` de `angular.json`, y fijar un umbral\n   **por métrica** (`lines`, `branches`, `functions`, `statements`), NO un único número\n   global. El valor inicial se **mide tras la siembra** y se fija **ligeramente por\n   debajo** de la línea base medida (colchón de 2–5 puntos para absorber la variabilidad\n   de la instrumentación V8), redondeando hacia abajo. `branches`/`functions` detectan\n   los tests-espejo sin aserciones (la propia brecha de meaningfulness de FR17.1). El\n   umbral es **trinquete manual por MR** (Q3=A): solo sube, revisado a mano cuando la\n   cobertura real lo supera; nunca se baja para hacer pasar el gate.\n\n5. **Fase gate (Q5=A — FR17.1, significatividad).** La cobertura **no se hereda sola**:\n   hoy `ci.yml` (PR) y el job `verify` de `fly-deploy.yml` (push→`main`) corren\n   `ng test --watch=false` **sin** flag de cobertura. Hay que **fijar el comando exacto\n   en ambos** para que ejerciten el umbral (p. ej. el flag de cobertura del builder o su\n   default en el target `test`), con una **única fuente de umbral** en `angular.json`.\n   La brecha de FR17.1 es de **meaningfulness**, no de ejecución: hoy los tests corren\n   pero no imponen cobertura ni verifican aserciones significativas. Orden obligado:\n   **FR10 → FR17.1**. Los specs sembrados deben tener aserciones reales (payload,\n   headers, estado), nunca el anti-patrón `expect(true).toBe(true)`.\n\nNotas y evidencia:\n\n- **Herramientas**: frontend `ng test` con **Vitest** (`^4.0.8`) + `jsdom` (`^25.0.1`)\n  vía el builder `@angular/build:unit-test` (`angular.json` → `architect.test.runner:\n  vitest`). Proveedor de cobertura a añadir: `@vitest/coverage-v8` (OSS, coste 0 €),\n  **fijado a versión exacta y casado en major con `vitest` 4.x** (un mismatch de major\n  rompe la instrumentación). Node `22.22.3` (`.nvmrc`, alineado con la línea Node 22 de\n  CI). Backend inalterado: `pytest` + `pytest-cov` desde `backend/`.\n- **La config de cobertura vive en `angular.json`, no en un `vitest.config` suelto**\n  (corrección mecánica de developer O1): el builder `@angular/build:unit-test` lee la\n  cobertura y sus umbrales de las `options` del target `test`; un `vitest.config` a mano\n  podría quedar fuera del flujo del builder. Fuente única de umbral.\n- **Umbral inicial (valor exacto → implementación).** El valor de arranque\n  (líneas/ramas/funciones/statements) NO se afirma aquí; se mide tras la siembra de la\n  fase 1 y se fija por debajo de la línea base real. Debe ser un piso que la línea base\n  ya supere para no romper el gate bloqueante de inmediato.\n- **Sin `cov-fail-under` heredado.** Como en backend, no existe piso de cobertura\n  bloqueante hoy; el umbral del frontend se introduce como trinquete consciente.\n- **Definición mínima de \"hecho\" (testing) del intent**: `angular.json` deja de nacer\n  código de lógica sin spec (`skipTests` retirado de los schematics relevantes),\n  `ng test` mide y exige cobertura por métrica contra un umbral con denominador estable,\n  y ese umbral bloquea en `ci.yml` y en `verify`; los specs llevan aserciones\n  significativas.\n- **Gate**: `pytest`, `ng test` (ahora **con cobertura por métrica**) y el escaneo de\n  secretos (gitleaks) son **BLOQUEANTES** en CI (PR→`main`) y en `verify` (push→`main`);\n  lint (ruff/ESLint) y auditorías de dependencias (pip-audit/npm audit) siguen\n  **advisory**. Cualquier paso adicional de reporte de cobertura es **solo\n  observabilidad** y nunca lleva `continue-on-error` que sustituya al enforcement dentro\n  de `ng test` (guardarraíl de devsecops).\n- **Deuda de pipeline DIFERIDA (Q8=A — no cerrada por omisión).** Dos huecos quedan\n  fuera del alcance de este intent y se registran como deuda:\n  (1) la paridad de la señal de cobertura de **backend** (`--cov`) en el job `verify`\n  (hoy `pytest -q` sin `--cov`, mientras `ci.yml` mide con `--cov=app`);\n  (2) **SAST/DAST del frontend** (no hay análisis estático de seguridad más allá de\n  ESLint advisory). Ambos son preexistentes y se difieren a un futuro diseño de\n  pipeline. OJO: la paridad de cobertura del **frontend** SÍ queda cerrada por este\n  intent, porque el umbral vive dentro de `ng test` y ese comando corre en ambos\n  caminos; la paridad de secretos ya está cerrada (gitleaks bloqueante `@v3` en PR y\n  `@v2` en `verify`, sin `continue-on-error`)."
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "test-after",
    "runner_step": "Verify the existing test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Verify the existing test runner/configuration and record the exact unit-scoped command.",
      "Data model / database behavior - implement.",
      "Data model / database behavior - write and run its tests after implementation.",
      "Repository / data access - implement.",
      "Repository / data access - write and run its tests after implementation.",
      "Business logic - implement.",
      "Business logic - write and run its tests after implementation.",
      "API / endpoint - implement.",
      "API / endpoint - write and run its tests after implementation.",
      "Frontend behavior - implement.",
      "Frontend behavior - write and run its tests after implementation.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:a54e9620d5f81599e49b530742a9d633bdd43f500decde041aa78dbb325fef16",
  "contract_sha256": "sha256:9efd6121f2ec126b4bd7d976ca8e8cd620bbce6f8b012a4a5206770664dc7ff6"
}
```

## Assumptions & Open Questions

- El valor numérico exacto del umbral por métrica se fija en el Step 8 tras medir la base (no se afirma aquí).
- La sintaxis exacta de `coverage.*` del builder se confirma en el Step 1 (spike).
