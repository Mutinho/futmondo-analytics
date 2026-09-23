# Plan de generación de código — U1 sync-reliability

> Conversation language: Spanish. Unidad: sync-reliability. Backend-only, aditivo,
> coste 0 €. No amplía god-files. Fuente de verdad: `functional-design/` (FS1-FS4,
> BR1-BR5), `inception/contract-design/contract-summary.md` (CT1-CT4),
> `inception/requirements-analysis/requirements.md` (FR3.1/FR3.2/FR6).

## Metodología de Test (encuadre de la unidad)

Metodología resuelta **test-after** (ver el bloque `## Testing Contract`
autoritativo, emitido por el engine, más abajo). Aplicado a esta unidad
backend-only:

- Implementar el helper estrecho (`sync_step_status.record_degraded_step`) y el
  cableado en `sync.py`/`market.py`/`token_store.py`/`db_connection.py`, y luego
  escribir specs significativas adyacentes en `backend/tests/`.
- Capas testables presentes en el patch: **lógica de negocio** (helper de estado
  degradado) y **API / endpoint** (`place_bid` techo de `price`). No hay capa de
  data-model nueva ni frontend (la nota de `ordering` del contrato es la posture
  general del intent, centrada en frontend; ESTA unidad es el subconjunto backend
  y no toca `angular.json`/`ng test`).
- Aserciones reales: estado (`progress[step].status`), payload (`reason`,
  contadores), status code HTTP (422/200), y no-regresión (`done` sigue `done`,
  `price<=0` sigue 422). NUNCA `assert True`.
- La suite `pytest` existente permanece en verde.

<!-- Testing Contract emitido por `aidlc engine testing-posture render`, verbatim -->
## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "sembrar specs de la capa `core/` crítica (servicios + `auth.guard` + `auth.interceptor`) más el componente de puja del mercado -> configurar cobertura en el target `test` de `angular.json` con `coverage.all: true` + `coverage.include: src/app/**` + excludes y umbrales por métrica -> medir la línea base y fijar el umbral inicial por debajo -> cablear el gate corrigiendo el comando `ng test` en `ci.yml` Y en el job `verify`; la suite existente permanece en verde.",
  "scope": "feature",
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
      "Meet an 80% line-coverage floor.",
      "Run the selected tests in CI before merge."
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
  "input_sha256": "sha256:fa0e23b87b4d76e3c452c98be7b910ec565c7889a0347832975e9af0b1ca654d",
  "contract_sha256": "sha256:6b7a73c49d5d50cb33e9f8d2e8ef70a86786735e273f1e727a3ea2953f63b3a5"
}
```

## Ficheros tocados

### Código nuevo
- `backend/app/services/sync_step_status.py` (NUEVO) — FS1/CT1:
  - `StepStatus` (`RUNNING="running"`, `DONE="done"`, `DEGRADED="degraded"`).
  - `ProgressSink` (Protocol con `update_progress`).
  - `record_degraded_step(tm, task_id, step, reason, extra=None)`: escribe
    `progress[step]={status: "degraded", reason, **extra}` y emite
    `logger.warning` estructurado. No propaga.

### Código modificado (quirúrgico, aditivo)
- `backend/app/api/v1/endpoints/sync.py` (~143-164) — FS2/CT-C3/FR3.1.2:
  - Import de `record_degraded_step`.
  - Rama `except` de `prizes`: reemplazar el `update_progress` que hoy escribe
    `{"status":"done",...,"error":...}` por
    `record_degraded_step(tm, task_id, "prizes", str(pr_err), {"records_synced": 0})`.
  - Rama `except` de `phantoms`: ídem con `{"total_phantoms": 0}`.
  - Camino OK (sin excepción) conserva `status="done"` (BR2, sin regresión).
- `backend/app/api/v1/endpoints/market.py` — FS3/CT3/FR6:
  - Constante de módulo `PRICE_SANITY_CAP = 5_000_000_000` (comentario justificativo
    en inglés).
  - En `place_bid`, junto al `if price <= 0` existente (que se MANTIENE intacto),
    añadir `if price > PRICE_SANITY_CAP: raise HTTPException(422, "El precio de la
    puja excede el límite permitido")`, antes de proxyar a Futmondo.
- `backend/app/auth/token_store.py` (~108-109) — FS4/FR3.2:
  - `init_auth_tables`, bucle de migraciones: estrechar `except Exception: pass
    # Column already exists` a la excepción esperada de "ya existe"
    (`psycopg2.errors.DuplicateColumn`/`DuplicateObject` y `ProgrammingError`, más
    `sqlite3.OperationalError` para el backend SQLite) + `logger.debug`. Cualquier
    otra excepción se re-propaga (no se traga un fallo real de migración).
- `backend/app/services/db_connection.py` (~183-196) — FS4/FR3.2:
  - Añadir `logger.debug`/`logger.warning` de contexto a los dos `except
    Exception: pass` del reintento de pool (`putconn(close=True)` de conn muerta y
    `closeall()` al recrear el pool). No silencio mudo.

### Tests nuevos (adyacentes, `backend/tests/`)
- `test_sync_step_status.py` — helper `record_degraded_step` (FR3.1.1/BR1).
- `test_sync_degraded_steps.py` — prizes/phantoms degradado vs done (FR3.1.2/BR1/BR2).
- Extensión de la validación de bid: `test_market_bid_sanity_cap.py` — techo
  `PRICE_SANITY_CAP` (FR6/BR4), manteniendo `price<=0` y un `price` válido intermedio.

## Restricciones honradas
- Backend-only; sin tocar frontend. Aditivo. No reintroducir `except` mudos.
- No ampliar `data_sync_service.py`/`data_manager_v2.py`. No commit.
- Formateo brownfield quirúrgico (solo ficheros nuevos / cambios puntuales).

## Sources

- `functional-design/functional-spec.md` (FS1-FS4), `functional-design/rules.md`
  (BR1-BR5), `functional-design/entities.md`.
- `inception/contract-design/contract-summary.md` (CT1-CT4).
- `inception/requirements-analysis/requirements.md` (FR3.1/FR3.2/FR6, NFR1-NFR5).
- Código verificado: `sync.py:143-164`, `market.py::place_bid`,
  `auth/token_store.py::init_auth_tables`, `services/db_connection.py::get_connection`.

## Assumptions & Open Questions

None.
