# Code Generation Plan — calculator-toggle (frontend-only)

Mejora: toggle "Incorporar jugadores en venta" en `/calculator`
(`angular-app/src/app/features/calculator/`). Cambio brownfield, in-place, sin
backend. Posture: test-after; estrategia Minimal; scope refactor (sin piso de
cobertura nuevo; la suite existente debe seguir verde; el ratchet de cobertura
frontend solo sube).

## Pasos de implementación

- [x] **Step 1 — Verificar runner de tests y registrar el comando unit-scoped.**
  Confirmar el runner Angular/Vitest existente (builder `@angular/build:unit-test`
  + `@vitest/coverage-v8` pin `4.1.11`). Registrar el comando exacto que ejecuta
  SOLO el spec de este componente en `unit-test-instructions.md`. (Runner listo
  antes del primer test.)
- [x] **Step 2 — Characterization-first del comportamiento actual.** Congelar en
  `calculator.component.spec.ts` el `futureBalance` actual (equivalente a toggle
  ON) y la composición actual de la lista seleccionable (hoy excluye los jugadores
  en venta). (NFR4, mandato characterization-first.)
- [x] **Step 3 — Frontend behavior: toggle + cálculo condicional.**
  En `calculator.component.ts`: `includeOnSale: WritableSignal<boolean>` desde
  `localStorage['futmondo_calc_include_onsale']` con fallback a ON (BR3.2/BR3.3/BR3.4);
  `futureBalance` suma `onSaleTotal` solo si `includeOnSale()` (BR1.1/BR1.2),
  `activeBidsTotal` siempre resta (BR2.1); `setIncludeOnSale(v)` persiste en
  `localStorage` (BR3.1). Importar `MatSlideToggleModule`.
- [x] **Step 3b — FR5: lista seleccionable condicional + reconstrucción.**
  La composición de la lista seleccionable depende de `includeOnSale` (BR5.1):
  con ON excluir los jugadores en venta (comportamiento actual), con OFF
  incluirlos deseleccionados (BR5.2). En `setIncludeOnSale`, al pasar a ON,
  re-excluir los jugadores en venta y limpiar de `selectedIds` cualquiera de ellos
  previamente marcado (BR5.3). Respetar la invariante anti-doble-conteo (BR5.4):
  un jugador en venta aporta por una sola vía.
- [x] **Step 4 — Frontend behavior: UI (toggle + visibilidad del bloque).** En
  `calculator.component.html`: `mat-slide-toggle` "Incorporar jugadores en venta"
  en `.calc-header` enlazado a `includeOnSale`/`setIncludeOnSale`; **ocultar** la
  sección de tarjetas "En venta" con `@if (includeOnSale())` cuando el toggle está
  OFF (BR4.1). Ajuste mínimo de estilo si procede.
- [x] **Step 5 — Frontend behavior: escribir y correr los tests tras implementar.**
  Ampliar `calculator.component.spec.ts` para aseverar el EFECTO: (a) ON incluye
  `onSaleTotal` y excluye los jugadores en venta de la lista; (b) OFF excluye
  `onSaleTotal`, incluye esos jugadores en la lista deseleccionados y oculta el
  bloque; (c) `activeBidsTotal` resta en ambos; (d) seleccionar un ex-onSale con
  OFF suma a `selectedTotal` (invariante BR5.4, nunca doble); (e) transición
  OFF→ON re-excluye y limpia la selección (BR5.3); (f) persistencia y
  restauración/fallback de `localStorage`. Correr el comando unit-scoped en verde.
- [x] **Step 6 — Documentación y trazabilidad.** Comentarios inline en inglés;
  actualizar `code-summary.md`, `source-manifest.json` y `traceability.json`.

## Mapeo paso → requisito

| Step | Cubre |
|------|-------|
| 1 | NFR3 (runner/gate), NFR4 (comando testeable) |
| 2 | NFR4 (characterization-first) |
| 3 | FR1.2, FR1.3, FR1.4, FR2.1, FR3.1–FR3.4 |
| 3b | FR5.1, FR5.2, FR5.3, FR5.4, FR5.5 (BR5.1–BR5.4) |
| 4 | FR1.1, FR5.1/FR5.2 (BR4.1), NFR2 (toggle Material accesible) |
| 5 | FR1.2/FR1.3/FR2.1/FR3.x/FR5.x (aserción de efecto), NFR4 |
| 6 | trazabilidad |

## Restricciones aplicadas

- Solo frontend; sin tocar backend, god-files ni SQL-en-router.
- No `ruff format`/Prettier masivo; formateo solo quirúrgico de los ficheros tocados.
- Coste 0 €; sin dependencias nuevas (`MatSlideToggleModule` ya está en Angular Material 22, ya dependencia del proyecto).
- Idioma: identificadores/comentarios en inglés; etiqueta de UI en castellano.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "medir y congelar la señal de cobertura y el estado advisory del gate antes de subir cualquier umbral o promover un check a bloqueante; luego sanear/silenciar quirúrgicamente la deuda heredada que cada promoción reportaría, aplicar cada endurecimiento en su commit `chore(ci)` aislado con el trinquete fijado, y sólo al FINAL del escalón fijar el piso de cobertura backend (`--cov-fail-under`) al valor medido exacto sobre la suite ya estabilizada, verificando en verde en AMBOS gates (PR + job `verify`) sin escribir asserts espejo que pasen siempre.",
  "scope": "refactor",
  "test_strategy": "minimal",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "- **Methodology**: test-after\n- **Ordering**: medir y congelar la señal de cobertura y el estado advisory del gate antes de subir cualquier umbral o promover un check a bloqueante; luego sanear/silenciar quirúrgicamente la deuda heredada que cada promoción reportaría, aplicar cada endurecimiento en su commit `chore(ci)` aislado con el trinquete fijado, y sólo al FINAL del escalón fijar el piso de cobertura backend (`--cov-fail-under`) al valor medido exacto sobre la suite ya estabilizada, verificando en verde en AMBOS gates (PR + job `verify`) sin escribir asserts espejo que pasen siempre.\n- **Cobertura backend (FR11)**: hoy `--cov=app` es **observability-only, sin\n  piso** (`ci.yml`; `pytest.ini` documenta cobertura como métrica informativa,\n  activable con `--cov=app`). Este intent introduce un **piso bloqueante único\n  `--cov-fail-under` en `pytest.ini`** (line-coverage total, dentro del mismo\n  `addopts` de `pytest` — config, no un paso extra), fijado al **valor medido\n  exacto SIN margen** (Q6; medición previa obligatoria) y que sube **sólo por\n  trinquete**; nunca se relaja para pasar el gate. Si aparece flapping, se\n  arregla el test no-determinista, NUNCA se baja el piso. El piso es\n  **line-only** en este intent (no se añade `--cov-branch`); una eventual paridad\n  de branch-coverage con el frontend queda fuera de alcance.\n- **Paridad de la señal backend (asimetría a CREAR — FR17.3)**: `ci.yml` mide\n  `--cov=app` mientras el job `verify` de `fly-deploy.yml` corre `pytest -q`\n  **sin `--cov`**. Este intent **cierra la asimetría** llevando la misma\n  invocación con cobertura y el mismo piso a `verify`, para que un rojo de\n  cobertura no pueda colarse por el push directo a `main`. Esta paridad aterriza\n  en el **mismo commit** que introduce el piso en `ci.yml`, o inmediatamente\n  después (Q4), para que no exista una ventana en la que el piso viva sólo en el\n  PR-gate.\n- **Cobertura frontend (SÓLO ratchet — ya tiene paridad de enforcement)**: el\n  enforcement vive DENTRO de `ng test` (builder `@angular/build:unit-test` +\n  `@vitest/coverage-v8` pin `4.1.11`), con umbrales por métrica en `angular.json`\n  (`coverageThresholds`: statements 15 / branches 15 / functions 13 / lines 14),\n  y **ambos** workflows (PR-gate y push-gate) ya corren `ng test`. Es decir, el\n  frontend **YA tiene paridad de enforcement** entre gates; su única tarea en\n  este intent es **subir el ratchet** de esos cuatro umbrales al valor medido. No\n  hay paridad frontend que crear (a diferencia del backend); no se debe inducir\n  ese trabajo inexistente. `angular.json` es la fuente única de umbral (sin pasos\n  extra ni `continue-on-error`).\n- **Tooling y coste 0 €**: backend `pytest` + `pytest-cov` desde `backend/` con\n  las fixtures fake in-memory de `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`\n  SQLite `:memory:`, `clean_jwt_env`, `fake_db`) — sin red, sin BD real, sin\n  credenciales/tokens reales (gitleaks escanea también los tests). No se prevén\n  dependencias nuevas de test; cualquiera sería OSS y **fijada a versión\n  exacta**. Un piso alto con aserciones débiles es peor que uno modesto con\n  aserciones reales: la posture test-after se mantiene con specs que aseveran el\n  efecto (payload/estado/modo de fallo), nunca `assert True` ni specs espejo.\n- **Sin bajar cobertura para pasar el gate**: el ratchet (backend y frontend)\n  **sólo sube**; nunca se relaja un umbral/piso existente para hacer pasar el\n  gate."
    }
  ],
  "obligations": {
    "strategy": "minimal",
    "strategy_volume": [
      "One verifiable test per requirement at the narrowest effective level.",
      "At least one happy-path unit test per component.",
      "Unit tests are the default; a bugfix/security scope floor may require an integration or E2E regression when that is the narrowest level that reproduces the defect."
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
  "input_sha256": "sha256:ecea62614f79c3c11fff8e333f4a41f0f402a7ee7b2dd66004a56fac66c28f13",
  "contract_sha256": "sha256:5b6e8d0595fa2a9cbd528cb7fb86e8e9ab82badb56be52a2afd06cf869fa8cd3"
}
```

Nota: de los cinco `testable_layers` del contrato, solo **Frontend behavior**
aplica a esta unidad (cambio puramente de UI); las capas data-model/repository/
business-logic/API no se tocan y se omiten por inaplicables, sin cambiar la
metodología test-after.

## Sources

- `requirements.md` (FR1–FR4, NFR2–NFR4), `functional-design/*` (BR1.1–BR4.1, entities, spec).
- Código: `calculator.component.ts` / `.html` / `.scss`.
- Testing Contract vía `aidlc engine testing-posture render`.

## Plan Approval

<!-- Rellenado tras generar el fingerprint -->
