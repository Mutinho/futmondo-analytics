# Code Generation Plan — U2 `u2-login-theming`

> Fase: construcción. Idioma: identificadores/comentarios en INGLÉS; prosa en castellano.

## Summary

- Builds: el revestimiento del login de F1 — `LoginView.swift` pasa a usar los componentes y tokens de la librería `DesignSystem` (U1): `TextInputField`, `PrimaryButton`, `ErrorState`, `Card`, `DSColor`, `DSFont`, `DSSpacing`.
- Touches: `ios/Sources/FutmondoApp/LoginView.swift` (modificado in-place); posible ajuste menor de imports. NO toca `AuthViewModel`, `AuthService` ni `KeychainTokenStore` (F1).
- Tests: sin tests nuevos de lógica (U2 es puramente visual; `AuthViewModel` ya está cubierto por F1). La verificación es que `swift build` compile y `swift test` (43 tests de F1+U1) siga en verde (sin regresión) + validación visual manual en dispositivo.

## Encaje

`LoginView` vive en `FutmondoApp` (guardado `#if canImport(SwiftUI)`), que no entra en `swift test` (sólo compila). Revestir = sustituir las vistas ad-hoc por los componentes de U1 preservando la API pública (`init(viewModel:logoNamespace:)`), el estado local `isPasswordVisible`, `ShakeEffect`, `sensoryFeedback`, focus y bindings a `AuthViewModel`.

## Pasos

- [x] Step 1 — Verificar el runner existente y registrar el comando unit-scoped (sin tests nuevos; la Unit es UI y se valida con build + suite existente verde). (Testing Contract runner_step)
- [x] Step 2 — Revestir el email field: sustituir `TextField("Email")` por `TextInputField` de U1 (label, icono email, teclado email, autofill), binding a `viewModel.email`. (FR6.1)
- [x] Step 3 — Revestir el password field: campo F1 (`SecureField`↔`TextField` + botón ojo local `isPasswordVisible`) re-skinned con tokens U1; NO se usa `TextInputField(isSecure:)` porque encapsula focus/toggle internos que F1 debe poseer (nota de contrato en code-summary); binding a `viewModel.password`. (FR6.1, NFR2.4)
- [x] Step 4 — Revestir el botón: sustituir `.borderedProminent` por `PrimaryButton` de U1 (`isEnabled=canSubmit`, `isLoading=(state==.loading)`, acción `submitLogin`). (FR6.1, BR2.1)
- [x] Step 5 — Revestir el error: sustituir el banner `.red` por `ErrorState` de U1. (FR6.1)
- [x] Step 6 — Revestir la card: sustituir `.ultraThinMaterial` por `Card`/superficie con token `surface`; aplicar `DSFont.h1` al título y tokens de color/espaciado. (FR6.1, FR1, FR2)
- [x] Step 7 — Preservar: NO tocar `AuthViewModel`/`AuthService`/Keychain; conservar `matchedGeometryEffect`, `ShakeEffect` (Reduce Motion), `sensoryFeedback`, focus, labels de accesibilidad. (FR6.2, NFR2.5)
- [x] Step 8 — Verificar `swift build` compila y `swift test` sigue en verde (43 tests, sin regresión). (verificación)
- [x] Step 9 — Documentación inline + `code-summary.md` + `traceability.json` + `source-manifest.json`. (trazabilidad)

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

U2 reviste una pantalla SwiftUI (frontend behavior) que no se testea con `swift test` en WSL (se valida en dispositivo). No añade lógica testeable nueva; `AuthViewModel` ya está cubierto por F1. Obligación de testing: la suite existente (43 tests) sigue en verde tras el revestimiento. Coherente con el aprendizaje durable (cobertura llvm-cov no medible en WSL; vistas SwiftUI validadas en dispositivo).
