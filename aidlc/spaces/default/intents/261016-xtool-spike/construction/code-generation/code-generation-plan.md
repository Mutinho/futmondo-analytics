# Code Generation Plan — Spike de la cadena `xtool` (B-01)

## Summary

- Builds: una app Swift/SwiftUI mínima empaquetada para `xtool` (SwiftPM + `xtool.yml`), más scripts de setup/smoke y un runbook, todo bajo `spikes/ios-xtool/` y `docs/spikes/ios-xtool.md`.
- Touches: crea `spikes/ios-xtool/` (código Swift + config + scripts) y `docs/spikes/ios-xtool.md` (runbook + nota de hallazgos); NO toca `backend/` ni `angular-app/`.
- Tests: sin suite automatizada nueva (la cadena build+firma+install se verifica a mano en el iPhone); 1 smoke test manual documentado + la suite existente del repo permanece verde (no se modifica código de app).

## Contexto y naturaleza del trabajo

Este es un **spike de toolchain**, zero-Unit, scope `bugfix` incremental. No hay
`units-generation` ni `requirements.md`; el trabajo se scopea desde el intent-statement y el
feasibility-assessment de este intent (ideación) y desde el workspace. El "código" es una app
Swift/SwiftUI trivial cuyo único fin es atravesar la cadena `xtool` (build → firma gratuita →
instalación → arranque en el iPhone 13 Pro desde WSL). [feasibility-assessment §3]

**Nota de testing honesta**: la verificación del DONE (la app arranca en el dispositivo físico)
es **manual en dispositivo** y no es automatizable como suite CI a coste 0 € (requiere USB
passthrough + firma + un iPhone conectado). Conforme al Testing Contract (`test-after`,
`minimal`), no se introduce piso de cobertura ni tests nuevos de app; la obligación de testing
es que **la suite existente del repo (backend `pytest`, frontend `ng test`) siga en verde**, lo
cual se cumple trivialmente porque este spike **no modifica** `backend/` ni `angular-app/`. El
"test" del spike es el **smoke manual** documentado en el runbook (reinstalar y abrir).

## Pasos de implementación

- [x] **Step 1 — Estructura del paquete SwiftPM del spike.** Crear `spikes/ios-xtool/` con
  `Package.swift` (producto ejecutable iOS mínimo) y la estructura de fuentes
  `Sources/XToolSpike/`.
- [x] **Step 2 — App SwiftUI trivial.** Implementar `App` + una única `ContentView` que muestre
  un texto trivial (p. ej. "xtool OK" + versión) como evidencia visual del arranque.
  [intent-capture Q1] [feasibility Q3]
- [x] **Step 3 — Config de `xtool` (`xtool.yml`).** Declarar `version`, `bundleID`, `product`
  (sin extensiones; widgets quedan fuera por scope). [feasibility §2]
- [x] **Step 4 — Script de setup del entorno (`scripts/setup-wsl.sh`).** Instalación idempotente
  y documentada de: toolchain Swift (con fallback `swiftly`/toolchain 24.04 por el riesgo R-02
  en Ubuntu 26.04), `usbmuxd`/libimobiledevice, y notas del lado Windows (`usbipd-win`). Mensajes
  de error claros si falta un prerequisito (sin fallos silenciosos). [RAID R-01, R-02]
- [x] **Step 5 — Script de smoke repetible (`scripts/smoke.sh`).** Secuencia documentada
  `xtool dev build` → firma → instalación → recordatorio de abrir en el dispositivo; pensado para
  repetir el ciclo tras la caducidad ~7 días. [feasibility Q3=B]
- [x] **Step 6 — Runbook + nota de hallazgos (`docs/spikes/ios-xtool.md`).** Guía paso a paso
  reproducible (prerequisitos, setup, build, firma, instalación, smoke) con secciones vacías de
  "Hallazgos" y "Bloqueos observados" a rellenar al ejecutar el spike en vivo. [intent-capture Q4/Q5]
- [ ] **Step 7 — Verificar que la suite existente del repo sigue verde.** Confirmar que no se ha
  tocado `backend/` ni `angular-app/`; (la ejecución efectiva de la suite es trabajo de la etapa
  Build and Test). [Testing Contract: existing suite green]
- [x] **Step 8 — Trazabilidad y README del spike.** `README.md` corto en `spikes/ios-xtool/`
  apuntando al runbook; cerrar `traceability.json`.

## Trazabilidad step → objetivo

| Step | Objetivo (fuente) |
|------|-------------------|
| 1-3 | DONE: app Swift/SwiftUI mínima construible por `xtool` [intent-capture Q1] |
| 4 | Montaje reproducible del toolchain WSL (D-02) [RAID R-02] |
| 5 | Receta de smoke repetible [feasibility Q3=B] |
| 6 | Runbook + nota de hallazgos [intent-capture Q4/Q5] |
| 7 | Suite existente verde [Testing Contract] |
| 8 | Documentación y trazabilidad |

## Nota sobre la ejecución en vivo

La **ejecución real** de la cadena (correr `setup-wsl.sh`, `xtool dev build`, firmar, instalar y
abrir en el iPhone) y el **registro de hallazgos** se harán de forma interactiva contigo durante
la etapa Build and Test / al correr el spike, porque requieren tu dispositivo físico, tu Apple ID
y el USB passthrough. Esta etapa produce los **artefactos** (código, config, scripts, runbook)
listos para esa ejecución.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "este intent entrega **documentos de análisis** (no capas de software testeable), así que no introduce ningún piso de cobertura ni tests nuevos; la única obligación de testing es que la **suite existente siga en verde** (backend `pytest` + `pytest-cov` desde `backend/` con fixtures fake in-memory de `conftest.py`; frontend `ng test` con Vitest). Un intent de análisis no modifica código de aplicación, por lo que no debería disparar fallos de la suite; pero el gate de CI corre igual en el PR documental y dentro de `ng test` el enforcement de cobertura (`coverageThresholds` en `angular.json`) es **bloqueante**: si un rojo aparece por **flapping** de cobertura ajeno al cambio, se **arregla el test no-determinista**, NUNCA se baja un umbral/piso ni se añade `continue-on-error` (coherente con el invariante del trinquete). Se conserva la metodología test-after del equipo para cuando se produzca código.",
  "scope": "bugfix",
  "test_strategy": "minimal",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "- **Methodology**: test-after\n- **Ordering**: este intent entrega **documentos de análisis** (no capas de\n  software testeable), así que no introduce ningún piso de cobertura ni tests\n  nuevos; la única obligación de testing es que la **suite existente siga en\n  verde** (backend `pytest` + `pytest-cov` desde `backend/` con fixtures fake\n  in-memory de `conftest.py`; frontend `ng test` con Vitest). Un intent de\n  análisis no modifica código de aplicación, por lo que no debería disparar\n  fallos de la suite; pero el gate de CI corre igual en el PR documental y dentro\n  de `ng test` el enforcement de cobertura (`coverageThresholds` en\n  `angular.json`) es **bloqueante**: si un rojo aparece por **flapping** de\n  cobertura ajeno al cambio, se **arregla el test no-determinista**, NUNCA se baja\n  un umbral/piso ni se añade `continue-on-error` (coherente con el invariante del\n  trinquete). Se conserva la metodología test-after del equipo para cuando se\n  produzca código.\n- **Línea base durable (para cuando SÍ haya código)**: posture **test-after**;\n  tests como entregable de primera clase que **aseveran el efecto**\n  (payload/estado/modo de fallo), nunca `assert True` ni specs espejo; fixtures\n  fake in-memory sin red, sin BD real y sin credenciales/tokens reales (gitleaks\n  escanea también los tests). El trinquete de cobertura (backend\n  `--cov-fail-under` en `pytest.ini`; frontend `coverageThresholds` en\n  `angular.json`) **sólo sube**, nunca se relaja para pasar el gate; el flapping\n  se arregla en el test no-determinista, no bajando el piso.\n- **Portabilidad de la posture al target nativo (riesgo a documentar en\n  feasibility, no obligación de este intent)**: la suite frontend actual (15\n  `*.spec.ts` sobre `@angular/build:unit-test`, builder Vitest `4.1.11` +\n  `@vitest/coverage-v8` + `jsdom`) **no porta tal cual** a NativeScript: no hay\n  DOM/`jsdom`, el runner Angular CLI de Vitest no aplica y los specs que montan\n  componentes Material/CDK no portan; los specs de servicios/RxJS/signals son\n  portables casi 1:1. Una migración nativa implicaría **rehacer el arnés de test\n  de frontend** y **re-basar** el umbral de cobertura sobre un runner distinto\n  (suelo nuevo bajo tooling distinto, no un trinquete que suba), y añade una\n  dimensión **E2E/dispositivo** (iPhone 13 Pro / Samsung A17) hoy inexistente. El\n  **backend no cambia** por una migración de UI nativa (ni `pytest` ni el piso\n  `--cov-fail-under`), para que nadie induzca trabajo backend inexistente.\n- **No aplica en este intent**: los valores concretos de piso de cobertura\n  medidos en intents previos (backend `--cov-fail-under=27`; frontend\n  statements 19 / branches 19 / functions 17 / lines 18) son estado heredado del\n  repo que este intent **no modifica**; no se induce trabajo de ratchet ni de\n  paridad de señal, propio de los intents de CI gate-hardening."
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
      "Include a targeted regression for the bug or vulnerability.",
      "Keep the existing test suite green."
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
  "input_sha256": "sha256:b6e34a53c381da31f372d2b1a90423ea8ff8c85097c1692d236fa81a6dbedee9",
  "contract_sha256": "sha256:e4cb7a4775fec20e1af5b544f32e5a65b1b5e71c4c5ee6d18b2f953e95f3354a"
}
```
