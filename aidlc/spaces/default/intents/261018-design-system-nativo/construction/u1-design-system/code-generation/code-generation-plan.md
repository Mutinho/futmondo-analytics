# Code Generation Plan — U1 `u1-design-system`

> Fase: construcción. Idioma: identificadores/comentarios en INGLÉS; prosa en castellano. Tokens técnicos verbatim.

## Summary

- Builds: la librería del sistema de diseño SwiftUI (tokens de color claro/oscuro, tipografía Dynamic Type, espaciado, componentes base: PrimaryButton, TextInputField, Card, LoadingState, ErrorState) y la pantalla de catálogo; reproduce el tema de Angular Material 3.
- Touches: `ios/Sources/FutmondoKit/DesignSystem/` (lógica pura testeable), `ios/Sources/FutmondoApp/DesignSystem/` (vistas SwiftUI, guardadas `#if canImport(SwiftUI)`), `ios/Sources/FutmondoApp/Resources/Assets.xcassets` (Color Sets Any/Dark), `ios/Tests/FutmondoKitTests/`.
- Tests: XCTest sobre la lógica pura de los tokens en `FutmondoKit` (resolución de valores por modo, escala de espaciado, escala tipográfica base, cálculo de contraste), ~6–8 tests, test-after, piso 80% line sobre el código testeable nuevo de `FutmondoKit`.

## Encaje con la arquitectura de F1

- **Lógica pura y testeable** → `FutmondoKit/DesignSystem/` (compila en Linux/WSL; `swift test` la cubre). Incluye los valores de token (hex claro/oscuro por rol, pasos de espaciado, escala tipográfica) y helpers deterministas (p. ej. contraste WCAG, selección de valor por `ColorScheme`), sin depender de SwiftUI.
- **Vistas SwiftUI** (componentes + catálogo) → `FutmondoApp/DesignSystem/`, cada fichero guardado con `#if canImport(SwiftUI)` (patrón de F1); no se testean con `swift test` (se validan en dispositivo).
- **Color Assets** → `FutmondoApp/Resources/Assets.xcassets` con Color Sets Any/Dark Appearance.

## Pasos

- [x] Step 1 — Estructura: crear `Sources/FutmondoKit/DesignSystem/` y `Sources/FutmondoApp/DesignSystem/`; ajustar `Package.swift` si hace falta (resources del asset catalog en `FutmondoApp`). (US1.1–US3.1)
- [x] Step 2 — Verificar el runner existente y registrar el comando unit-scoped (`swift test --filter FutmondoKitTests.DesignSystem*`). (Testing Contract runner_step)
- [x] Step 3 — Lógica de tokens (impl): `DSColorValue` (hex claro/oscuro por rol + resolución por `ColorScheme`), `DSSpacing` (xs/sm/md/lg/xl), `DSTypographyScale` (tamaños base h1/h2/h3/body), `ContrastRatio` helper (WCAG). En `FutmondoKit/DesignSystem/`. (US1.1–US1.3, BR1.1, BR1.4)
- [x] Step 4 — Tests (test-after) de la lógica de tokens: resolución claro/oscuro, pasos de espaciado, escala tipográfica, contraste ≥4.5:1/≥3:1. XCTest en `Tests/FutmondoKitTests/`. (BR1.1, BR1.4; piso 80%)
- [x] Step 5 — Color Assets: `Assets.xcassets` con Color Sets (primary, tertiary, surface, onSurface, onSurfaceVariant, moneyPositive, moneyNegative, errorContainer) Any/Dark, derivados de `DSColorValue`. (FR1)
- [x] Step 6 — Accessors SwiftUI de tokens: `DSColor`, `DSFont` (Dynamic Type), `DSSpacing` en `FutmondoApp/DesignSystem/` (`#if canImport(SwiftUI)`). (FR1, FR2, BR1.2, BR1.3)
- [x] Step 7 — Componentes (impl): `PrimaryButton`, `TextInputField` (SecureField + toggle), `Card`, `LoadingState`, `ErrorState` en `FutmondoApp/DesignSystem/Components/` (`#if canImport(SwiftUI)`), con `accessibilityLabel`/rol y `data-testid`-equivalente (`accessibilityIdentifier`). (FR4, BR2.1, BR2.2, NFR1)
- [x] Step 8 — Catálogo: `CatalogView` + `ThemeToggle` + `TextSizeControl` + secciones, en `FutmondoApp/DesignSystem/Catalog/`. (FR5)
- [x] Step 9 — Build/config: asegurar que `swift build` compila `FutmondoKit` y `FutmondoApp`; que `swift test` sólo cubre `FutmondoKit`. (tech-stack)
- [x] Step 10 — Documentación inline + `traceability.json` + `source-manifest.json`. (trazabilidad)

<!-- Testing Contract pasted verbatim below -->

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "este intent entrega **artefactos de diseño** (tokens y pantallas de referencia), no capas de software testeable, así que no introduce ningún piso de cobertura ni tests nuevos; la única obligación de testing es que la **suite existente siga en verde** (backend `pytest` + `pytest-cov` desde `backend/` con fixtures fake in-memory de `conftest.py`; frontend `ng test` con Vitest). Cuando SÍ se produzca código de UI, se implementa cada capa testeable y después se escriben y corren sus tests (test-after).",
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
      "text": "- **Methodology**: test-after\n- **Ordering**: este intent entrega **artefactos de diseño** (tokens y pantallas\n  de referencia), no capas de software testeable, así que no introduce ningún\n  piso de cobertura ni tests nuevos; la única obligación de testing es que la\n  **suite existente siga en verde** (backend `pytest` + `pytest-cov` desde\n  `backend/` con fixtures fake in-memory de `conftest.py`; frontend `ng test` con\n  Vitest). Cuando SÍ se produzca código de UI, se implementa cada capa testeable\n  y después se escriben y corren sus tests (test-after).\n- **Methodology evidence**: posture test-after afirmada y vigente en memoria del\n  equipo; la suite backend es **characterization-first** (~50+ `test_*.py`) y la\n  frontend es Vitest sobre `@angular/build:unit-test`; ambas preexisten a este\n  intent y no cambian por él.\n- Un intent de diseño no modifica código de aplicación, por lo que no debería\n  disparar fallos de la suite; pero el gate de CI corre igual en el PR y dentro de\n  `ng test` el enforcement de cobertura (`coverageThresholds` en `angular.json`,\n  `statements 19` / `branches 19` / `functions 17` / `lines 18`) es **bloqueante**:\n  si un rojo aparece por **flapping** ajeno al cambio, se **arregla el test\n  no-determinista**, NUNCA se baja un umbral/piso ni se añade `continue-on-error`\n  (invariante del trinquete: sólo sube).\n- **Matiz nativo iOS (riesgo a documentar en diseño, NO obligación de este\n  intent)**: el arnés de test del frontend Angular (Vitest `4.1.11` +\n  `@vitest/coverage-v8` + `jsdom`, specs que montan componentes Material/CDK) **no\n  porta 1:1** a un target SwiftUI: no hay DOM/`jsdom` ni runner Angular CLI de\n  Vitest, y una UI SwiftUI se verifica con el toolchain nativo de Apple\n  (XCTest / previews / snapshot), no con Vitest/jsdom. Una eventual capa de UI\n  nativa implicaría **rehacer el arnés de test de UI** y **re-basar** cualquier\n  umbral sobre un runner distinto (suelo nuevo bajo tooling distinto, no un\n  trinquete que suba), más una dimensión **E2E/dispositivo** (iPhone 13 Pro) hoy\n  inexistente. El **backend no cambia** por una capa de diseño nativa (ni\n  `pytest` ni el piso `--cov-fail-under=27`), para que nadie induzca trabajo\n  backend inexistente.\n- **No aplica en este intent**: los pisos de cobertura heredados (backend\n  `--cov-fail-under=27`; frontend `19/19/17/18`) son estado del repo que este\n  intent **no modifica**; no se induce trabajo de ratchet ni de paridad de señal."
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
  "input_sha256": "sha256:c73ede2e2c34f439407dde08a3c68eaef65b016c3c6c0382b7eaf8803ad8b964",
  "contract_sha256": "sha256:584ae365a0491882e55fc3521128fbf8cc5ea8035b1ac48796daeae5745ab90e"
}
```

## Nota sobre capas testeables

Las capas "data model / repository / API" de la Testing Contract NO aplican a una librería de UI sin datos ni red: se omiten por inaplicables sin cambiar la metodología test-after. La capa testeable real es la **lógica pura de tokens** (valores, resolución por modo, escala, contraste) en `FutmondoKit`, cubierta por XCTest; las vistas SwiftUI se validan en dispositivo (arnés de UI nativo diferido, por decisión de practices).
