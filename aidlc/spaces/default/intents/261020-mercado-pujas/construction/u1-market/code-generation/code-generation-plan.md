# Code Generation Plan — u1-market (pantalla de Mercado)

## Summary

- Builds: la pantalla de Mercado nativa (2ª pestaña) — lógica testeable en `FutmondoKit` (modelos, `MarketService`/`SofascoreService` actors, `MarketSorter`, `BidAmountValidator`, mapeo `MarketWriteOutcome`) y vistas SwiftUI en `FutmondoApp` (lista, banner, cards, sheets de puja/cancelación/Sofascore, 2ª pestaña del `RootTabView`).
- Touches: `ios/Sources/FutmondoKit/Market/*`, `ios/Sources/FutmondoApp/Market/*`, `ios/Sources/FutmondoApp/RootTabView.swift` (si existe; si no, el shell de pestañas), `ios/Tests/FutmondoKitTests/Market*Tests.swift`.
- Tests: XCTest sobre `FutmondoKit` (≈5–8 por componente testeable: `MarketSorter`, `BidAmountValidator`, mapeo de `MarketWriteOutcome`, decodificación de DTOs, `MarketService`/`SofascoreService` con doble de `NetworkClient`); las vistas SwiftUI se validan en dispositivo (fuera del cómputo de cobertura, WSL).

## Trazabilidad plan → historia

Cada paso referencia las US/FR que implementa (US1–US7, FR1–FR8).

## Pasos

- [x] **Step 1 — Estructura y esqueleto de configuración**: crear
  `ios/Sources/FutmondoKit/Market/` y `ios/Sources/FutmondoApp/Market/`; confirmar
  que `Package.swift` sigue con `dependencies: []` (sin cambios de dependencias).
  (Infra de la Unit.)
- [x] **Step 2 — Verificar runner y comando de test**: confirmar que
  `swift test --package-path ios` corre en el entorno (runner existente); registrar
  el comando exacto scoped a esta Unit en `unit-test-instructions.md`. (Runner-ready
  antes del primer test.)
- [x] **Step 3 — Modelos de dominio (implementar)**: `MarketPlayer` (Codable,
  Equatable, Sendable), `MarketUserInfo` (+ `balanceMinusBids`),
  `MarketTodayResponse`, `MarketWriteOutcome` (enum .accepted/.rejected/.networkError),
  `SofascoreDetail`, `MarketSortField`. (FR2/FR3/FR4/FR8; C1–C4, C8.)
- [x] **Step 4 — Tests de modelos (test-after)**: decodificación de DTOs desde
  JSON de ejemplo del backend; `balanceMinusBids`; igualdad/opcionales. (5–8 tests.)
- [x] **Step 5 — Lógica pura (implementar)**: `MarketSorter` (orden desc, nulos al
  final, default `value`) y `BidAmountValidator` (`[market_price,
  available_for_bids]`, `>0` → .valid/.tooLow/.tooHigh/.nonPositive). (FR5/FR6.2;
  C6, C7.)
- [x] **Step 6 — Tests de lógica pura (test-after)**: `MarketSorter` por cada campo
  + nulos al final + default; `BidAmountValidator` por cada caso de borde. (5–8
  tests cada uno.)
- [x] **Step 7 — Servicios de red (implementar)**: `MarketService` (actor:
  `loadToday`, `placeBid`, `cancelBid` → mapeo a `MarketWriteOutcome`) y
  `SofascoreService` (actor dedicado: `loadDetail` → resultado tipado), ambos sobre
  el `NetworkClient` reutilizado (Bearer); endpoints y params de query exactos
  (`is_clause=false`, `championship_id`, etc.). (FR2/FR6/FR7/FR8; C5, C8.)
- [x] **Step 8 — Tests de servicios (test-after)**: con un doble in-memory de
  `NetworkClient`, aseverar: `loadToday` OK/empty/error; `placeBid`/`cancelBid`
  mapeando 2xx-true/2xx-false/4xx/5xx a los 3 desenlaces; `SofascoreService`
  loaded/failed/404; aislamiento (un fallo del detalle no muta estado de Mercado).
  (5–8 tests.)
- [x] **Step 9 — ViewModel (implementar)**: `MarketViewModel` (@MainActor,
  ObservableObject): `load/reload/setSort/placeBid/cancelBid`; `isWriting` global;
  recarga sólo en `.accepted`; aplica `MarketSorter`; expone `lastWriteNotice`.
  (FR2/FR5/FR6/FR7; V2.)
- [x] **Step 10 — Tests del ViewModel (test-after, lógica observable)**: transición
  de estados loading→data/empty/error; `isWriting` on/off; recarga sólo en
  `.accepted`; reordenado sin red. (Donde la lógica sea testeable en `FutmondoKit`;
  la parte @MainActor puramente de UI se valida en dispositivo.)
- [x] **Step 11 — Vistas SwiftUI (implementar, validadas en dispositivo)**:
  `MarketView` (banner + barra de orden + lista + estados), `MarketPlayerCard`,
  `BidSheet` (validación inline), `CancelBidConfirmation`, `SofascoreDetailSheet`
  (estado local aislado), e integración de la 2ª pestaña en `RootTabView`. Reutiliza
  `DesignSystem` (Card/PrimaryButton/TextInputField/estados) y tokens de F1/F2.
  `data-testid`/accessibility identifiers en elementos interactivos. (FR1–FR8;
  V1, V3–V7.)
- [ ] **Step 12 — Validación de vistas en dispositivo**: `xtool dev build`
  (iPhone 13 Pro) para verificar render y flujos; fuera del cómputo de cobertura
  (llvm-cov no fiable en WSL). (NFR5.)
- [x] **Step 13 — Configuración de entorno/build**: sin cambios de dependencias;
  verificar que el target `FutmondoKit`/`FutmondoApp` compila y que los nuevos
  ficheros están en el layout SwiftPM esperado.
- [ ] **Step 14 — Documentación y trazabilidad**: `code-summary.md`,
  `source-manifest.json` (todas las rutas creadas/modificadas) y `traceability.json`
  (AC/FR/NFRx.y/BR-UI → fichero).

## Notas de calidad

- Piso de cobertura (feature, 80% línea) **se mide sobre la lógica testeable de
  `FutmondoKit`** vía `swift test`; las vistas SwiftUI quedan fuera del cómputo de
  cobertura (llvm-cov no fiable en WSL — aprendizaje durable). NUNCA se baja ni se
  desactiva un umbral para pasar; si no es medible en WSL, se documenta, no se
  relaja.
- Idioma: identificadores/comentarios en inglés; strings de UI en castellano.
- Seguridad: Bearer en memoria, refresh en Keychain, sin material de credencial en
  logs/avisos; tests con dobles, sin tokens reales.
- Sin dependencias nuevas (coste 0 €); no ampliar god-files del backend (no aplica:
  sin cambios backend).

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
