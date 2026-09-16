# Code Generation Plan — Optimización del bundle inicial (frontend Angular)

> Stage 3.5 Code Generation · Intent `260914-bundle-optimization` · scope `refactor` · directiva zero-Unit · Test Strategy Minimal · brownfield.
> Fuente de verdad: `requirements.md` (FR1–FR4, NFR1–NFR4), `functional-spec.md` (WF1–WF5), `rules.md` (BR1.1–BR5.2), `entities.md`.
> Sin cambio funcional, coste 0 €. Se modifican ficheros in situ; NO se crean duplicados.

## Alcance del trabajo

Refactor de la composición del bundle inicial de `angular-app/` para bajar el chunk `initial` por debajo de 1 MB y restaurar `maximumError: 1MB` en `angular.json`, sin cambio funcional y sin dependencias nuevas. Cuatro palancas, en este orden obligatorio (BR4.3 / FR4.4 — recortar ANTES de restaurar el budget):

1. Sacar `provideCharts`/`ng2-charts`/`chart.js` del arranque eager → registro lazy en las rutas/componentes consumidoras (`evolution`, `stats`). (FR1, BR1.*)
2. Diferir `AssistantChatComponent` y `marked` con `@defer` en `AssistantFabComponent`. (FR2, BR2.*)
3. Sustituir `PreloadAllModules` por una `PreloadingStrategy` propia con retardo por inactividad. (FR3, BR3.*)
4. Restaurar el budget `initial` a `maximumError: 1MB` + `maximumWarning: 900kB`. (FR4, BR4.*)

## Ficheros afectados (referencia)

- `angular-app/src/app/app.config.ts` — quitar `provideCharts(...)`; cambiar `withPreloading(PreloadAllModules)` por la estrategia propia.
- `angular-app/src/app/features/evolution/evolution.component.ts` — añadir `providers: [provideCharts(withDefaultRegisterables())]`.
- `angular-app/src/app/features/stats/stats.component.ts` — añadir `providers: [provideCharts(withDefaultRegisterables())]`.
- `angular-app/src/app/shared/components/assistant-fab.component.ts` — diferir `AssistantChatComponent` con `@defer (on interaction/…)`.
- `angular-app/src/app/core/preloading/idle-preloading-strategy.ts` — NUEVO: estrategia de precarga con retardo por inactividad.
- `angular-app/angular.json` — budget `initial`: `maximumError 1.2MB→1MB`, `maximumWarning 1MB→900kB`.
- Tests: specs nuevos junto a los ficheros de lógica pura (estrategia de preloading), más verificación de suite verde.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "org",
  "ordering": "implement each applicable testable layer, then write and run",
  "scope": "refactor",
  "test_strategy": "minimal",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
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
  "input_sha256": "sha256:06c12367ad8c44802c849bfad1d351bad9312bf5dfa96742a3ea92f337cd806c",
  "contract_sha256": "sha256:7af67a82762c8fd34307f7f4649e88d0c70caf872dadb3179ed5c4eee0d7e237"
}
```

**Interpretación del contrato para este refactor.** Metodología `test-after`, orden: implementar cada capa testable aplicable y luego escribir/ejecutar sus tests. Este refactor no toca modelo de datos, repositorio ni API: las únicas capas aplicables son **Business logic** (la nueva `IdlePreloadingStrategy`, lógica pura y testeable en unit) y **Frontend behavior** (composición del bundle: providers de charts a nivel de componente lazy, `@defer` del chat, budget). El resto de capas del `plan_profile` se omiten por inaplicables sin cambiar la metodología. La verificación de no regresión (suite existente verde) es la piedra angular de NFR2/BR5.1; la comprobación de que las librerías salen del chunk `initial` (NFR1/BR1.2/BR2.2) se hace por inspección del desglose del build de producción en Build and Test.

## Pasos de implementación

- [x] **Step 1 — Skeleton y verificación de configuración de producción.** Confirmar la estructura actual (`app.config.ts`, `app.routes.ts`, componentes lazy, `angular.json`). No se crea proyecto nuevo (brownfield). Confirmar builder `@angular/build:application` y config `production`. _Sin cambio de código; base para los siguientes pasos._ (WF5)

- [x] **Step 2 — Verificar el runner de tests y registrar el comando exacto scoped.** Confirmar que `test` usa `@angular/build:unit-test` con `runner: vitest`. Registrar en `unit-test-instructions.md` el comando exacto scoped a los specs de esta unidad (no `npm test` a secas). El runner debe estar operativo ANTES del primer paso de test. (BR5.1, NFR2)

- [x] **Step 3 — Business logic: implementar `IdlePreloadingStrategy`.** Crear `angular-app/src/app/core/preloading/idle-preloading-strategy.ts`: una `PreloadingStrategy` propia que difiere el `load()` de cada ruta hasta detectar inactividad tras el arranque (p. ej. `requestIdleCallback` con fallback a `setTimeout`, y un `idleDelay` configurable). Sin dependencias nuevas (solo APIs del navegador + RxJS ya presentes). El valor concreto de `idleDelay` se fija aquí con criterio conservador (open question de requirements). (FR3.1, FR3.2, BR3.1, BR3.2, NFR3, NFR4, WF4)

- [x] **Step 4 — Business logic: tests de `IdlePreloadingStrategy` (test-after).** Escribir `angular-app/src/app/core/preloading/idle-preloading-strategy.spec.ts` con Vitest: (a) happy-path — precarga la ruta tras el retardo/inactividad; (b) edge — no precarga inmediatamente (antes del idle); (c) edge — respeta `data.preload === false` o rutas sin `loadChildren/loadComponent` devolviendo `EMPTY`/`of(null)` sin cargar. Usar fake timers. Ejecutar y dejar verde. (BR3.1, BR3.3, NFR4)

- [x] **Step 5 — Frontend behavior: registro lazy de Chart.js en los consumidores.** En `evolution.component.ts` y `stats.component.ts` añadir `providers: [provideCharts(withDefaultRegisterables())]` a nivel de componente e importar `provideCharts`/`withDefaultRegisterables` desde `ng2-charts` en esos ficheros. Quitar `provideCharts(withDefaultRegisterables())` de `app.config.ts` y su import. Como `evolution` y `stats` ya son rutas lazy (`loadComponent`), el registro y `chart.js`/`ng2-charts` quedan en sus chunks lazy y fuera del `initial`. (FR1.1, FR1.3, BR1.1, BR1.3, WF3)

- [x] **Step 6 — Frontend behavior: diferir el chat y `marked` con `@defer`.** En `assistant-fab.component.ts` sustituir el import estático de `AssistantChatComponent` por un bloque `@defer` en la plantilla, disparado al abrir el chat (`@defer (when chatOpen())` o `on interaction`), con `@placeholder`/`@loading` mínimos. Así `AssistantChatComponent` y su dependencia `marked` salen del chunk `initial` y se cargan bajo demanda (WF2). Mantener el mismo comportamiento observable del chat (BR2.3). (FR2.1, FR2.3, BR2.1, BR2.3, WF2)

- [x] **Step 7 — Frontend behavior: aplicar la estrategia de preloading en el arranque.** En `app.config.ts` cambiar `withPreloading(PreloadAllModules)` por `withPreloading(IdlePreloadingStrategy)` (registrada como provider). Verificar que todas las rutas lazy siguen navegables. (FR3.1, FR3.3, BR3.1, BR3.3, WF1, WF4)

- [x] **Step 8 — Frontend behavior: verificación de no regresión (suite existente).** Ejecutar la suite de tests existente del frontend (incluye `auth.interceptor.spec.ts` y el nuevo spec) y dejarla verde. No se añaden tests de componente nuevos más allá del spec de la estrategia (scope refactor no añade floor; los componentes tienen `skipTests` por convención del proyecto y su verificación funcional es manual — BR5.1). (NFR2, BR5.1, BR5.2)

- [x] **Step 9 — Environment/build config: restaurar el budget.** SOLO tras Steps 5–7 (recorte hecho): en `angular.json` config `production`, budget `type: initial` → `maximumError: "1MB"`, `maximumWarning: "900kB"`. (FR4.1, FR4.2, FR4.4, BR4.1, BR4.3)

- [x] **Step 10 — Documentación y trazabilidad.** Comentarios inline en la estrategia de preloading; actualizar `code-summary.md`, `source-manifest.json` y `traceability.json`. La verificación del build de producción con el budget de 1 MB (FR4.3/BR4.2/NFR1) y la comprobación de que charts/marked no están en `initial` (BR1.2/BR2.2) se ejecutan y validan en Build and Test. (FR4.3, BR4.2, NFR1)

## Trazabilidad requisito/regla → step

| ID | Descripción | Step(s) |
|----|-------------|---------|
| FR1.1 / BR1.1 | Charts no eager, registro lazy por ruta | Step 5 |
| FR1.2 / BR1.2 | charts fuera del chunk initial | Step 5 (efecto), Step 10 (verificación en B&T) |
| FR1.3 / BR1.3 | Gráficos siguen renderizando | Step 5, Step 8 (manual) |
| FR2.1 / BR2.1 | Chat cargado bajo demanda | Step 6 |
| FR2.2 / BR2.2 | marked fuera del initial | Step 6 (efecto), Step 10 (verificación en B&T) |
| FR2.3 / BR2.3 | Chat sigue funcionando (lazy) | Step 6, Step 8 (manual) |
| FR3.1 / BR3.1 | Precarga con retardo tras inactividad | Step 3, Step 7 |
| FR3.2 / BR3.2 | Precarga sin dependencias de pago | Step 3 |
| FR3.3 / BR3.3 | Navegación lazy sigue funcionando | Step 4, Step 7 |
| FR4.1 / BR4.1 | Restaurar maximumError 1MB + warning <1MB | Step 9 |
| FR4.3 / BR4.2 | Build de producción pasa | Step 10 (B&T) |
| FR4.4 / BR4.3 | Recortar antes de restaurar budget | Orden Steps 5–7 → Step 9 |
| NFR1 | Chunk initial < 1 MB | Step 9, Step 10 (B&T) |
| NFR2 / BR5.1 | Suite verde + verificación manual | Step 4, Step 8 |
| NFR3 / BR5.2 | Coste 0 €, no sustituir librerías | Step 3, Step 5, Step 6 |
| NFR4 | Menor pico de transferencia tras arranque | Step 3, Step 7 |

## Plan Approval

¿Apruebas este plan de Code Generation, su Testing Contract incrustado y las `unit-test-instructions.md`?

- "Approve Plan" — proceder a la generación de código
- "Request Changes" — revisar el plan

[Answer]:
