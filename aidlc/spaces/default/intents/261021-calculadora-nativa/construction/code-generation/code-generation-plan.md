# Code Generation Plan — Calculadora nativa iOS

## Summary

- Builds: la pantalla nativa **Calculadora** (SwiftUI) — lógica pura en
  `FutmondoKit` (DTOs, servicio de roster/venta, `CalculatorMath`, sorter,
  preferencias) y vistas en `FutmondoApp` (cards estilo Mercado, resumen,
  proyección por fecha, venta/cancelación), como 3.ª pestaña.
- Touches: crea `ios/Sources/FutmondoKit/Calculator/*` y
  `ios/Sources/FutmondoApp/Calculator/*`, añade tests en
  `ios/Tests/FutmondoKitTests/*`, extiende `MarketUserInfo` (campo opcional) y
  `RootTabView` (3.ª pestaña) y `SplashView` (cross-invalidación).
- Tests: XCTest en `FutmondoKit` para `CalculatorMath` (invariantes FR7),
  `CalculatorSorter`, `CalculatorPreferences` y decode de DTOs (~12-16 tests);
  vistas SwiftUI validadas en dispositivo (fuera de cobertura, WSL).

## Trazabilidad plan → diseño

Cada paso referencia los artefactos de `construction/functional-design/`
(`entities.md`, `rules.md`, `functional-spec.md`, `frontend-components.md`) y
los FR de `requirements.md`.

## Pasos

- [ ] **Step 1 — Estructura y DTOs (FutmondoKit).** Crear `RosterPlayer`,
  `OnSalePlayer` (Codable, snake_case→camelCase) y el tipo-suma `SellOutcome`
  (`total(sold)`, `partial(sold,total)`, `none(total)`, `networkError(message)`).
  Entidades: entities.md. (FR5, FR8; BR7.1)
- [ ] **Step 2 — Extender `MarketUserInfo` con `activeBidsCount`.** Campo
  **opcional con default 0** (`decodeIfPresent ?? 0` + parámetro de init por
  defecto AL FINAL) para NO romper el decode de `market/today` ni los callers
  (R-02). (FR2.3; entities.md EconomySnapshot)
- [ ] **Step 3 — `RosterService` + `HTTPRosterService` (actor sobre
  `NetworkClient`).** `fetchRoster`, `fetchOnSale`, `sell` (→ `SellOutcome`),
  `cancelSale` (→ `MarketWriteOutcome`). Sin tocar backend; mismo patrón que
  `MarketService`/`BudgetService`. (FR1.1, FR8, FR9, C1)
- [ ] **Step 4 — `CalculatorMath` (struct puro).** `projectedValue(player,days)`,
  `selectedTotal(players,ids,days)`, `onSaleTotal(onSale)`,
  `futureBalance(...)`. (FR7; BR1.1–BR3.2)
- [ ] **Step 5 — `CalculatorSorter` + `CalculatorPreferences`.** Orden por
  projectedValue/value/change/profit; preferencias en `UserDefaults` (default
  toggle ON, BR5.1). (FR5.3, FR3.1)
- [ ] **Step 6 — Verificar el runner y registrar el comando unit-scoped.**
  `swift test --package-path ios` ya existe; registrar el comando exacto en
  `unit-test-instructions.md` (runner-ready antes de los tests).
- [ ] **Step 7 — Tests XCTest (FutmondoKit, test-after).** `CalculatorMathTests`
  (invariantes FR7: proyección, selectedTotal, onSaleTotal, futureBalance con
  toggle ON/OFF y activeBidsTotal siempre restado, anti-doble-conteo),
  `CalculatorSorterTests`, `CalculatorPreferencesTests`, decode de
  `RosterPlayer`/`OnSalePlayer` y de `active_bids_count` ausente/presente.
- [ ] **Step 8 — Vistas SwiftUI (FutmondoApp).** `CalculatorViewModel`
  (@MainActor), `CalculatorView`, `CalculatorHeader`, `OnSaleSection`,
  `CalculatorPlayerCard` (reutiliza estética/tiles de Mercado), `SellFloatingButton`,
  confirmaciones nativas. Bajo `#if canImport(SwiftUI)`. (FR2–FR9;
  frontend-components.md)
- [ ] **Step 9 — Integración de navegación y caché.** 3.ª pestaña en
  `RootTabView` (tinte verde, accesibilidad); `DataFreshness` +
  `loadIfNeeded()` + `.refreshable`; cross-invalidación en `SplashView`
  (`onWriteAccepted` → invalidar Presupuesto y Mercado). (FR1.4, FR10.1, FR11.1)
- [ ] **Step 10 — Build + tests verdes.** `swift build --package-path ios` y
  `swift test --package-path ios`; corregir issues Swift 6 device-strict
  (`static let`, no `static var` de estado).
- [ ] **Step 11 — Documentación y trazabilidad.** `code-summary.md`,
  `traceability.json` (AC/BR/FR → ficheros).

- [ ] **Step 12 — Ajustes de UX tras prueba en dispositivo (revisión).**
  Feedback del propietario probando en el iPhone:
  1. **Fecha de venta → botón flotante en la toolbar** a la derecha del de
     ordenar, con **icono de calendario** (`DSGlassIcon` "calendar"), que abre
     el `DatePicker` gráfico en un `popover`/`Menu`. Se elimina la card de
     proyección del scroll (el "N días a futuro" se muestra junto al botón o en
     la píldora). (FR4.1)
  2. **Píldora flotante al hacer scroll** con el resumen esencial (Saldo
     futuro · Seleccionadas · Saldo actual), replicando el patrón de Mercado
     (`ScrollOffsetReader` + `CompactEconomyPill` con `onScrollGeometryChange`,
     umbral de histéresis, solo un `Bool` de estado). (NFR4, NFR5)
  3. **Eliminar el label "Quitar selección"** del `countLabel` (sobra y no
     aportaba acción clara). La deselección total sigue disponible desde el
     propio flujo de selección.
  4. **Botón "Vender (N)" más sutil y nativo**: en vez de la cápsula sólida
     grande centrada abajo (que queda "pegote" junto a la tab bar), una
     **píldora compacta flotante alineada a la derecha** con material glass +
     borde neón, coherente con la estética; mantiene el texto "Vender (N)" y la
     confirmación. (FR8.1)
  Mantiene invariantes (FR7), build verde y los 204 tests; solo vistas SwiftUI.

- [ ] **Step 13 — Más ajustes de UX tras prueba en dispositivo (revisión 2).**
  1. **Icono de la pestaña Calculadora**: cambiar el SF Symbol `function` por un
     icono de **calculadora** real en `RootTabView` (p. ej.
     `squareroot`→NO; usar `plusminus.circle` NO; usar `candybarphone` NO) →
     usar el símbolo de calculadora de Apple (`platter.filled.bottom.iphone` NO):
     el SF Symbol correcto es **`calculator`** (o su relleno si existe en el
     target). (FR11.1)
  2. **Bloque "En venta" como carrusel horizontal compacto**: `OnSaleSection`
     deja de ser filas a ancho completo y pasa a un **ScrollView horizontal** de
     tarjetas compactas (`OnSaleCard`): foto del jugador (hero circular/redondeada),
     nombre, **precio actual**, y una forma elegante y nativa de **quitar de la
     venta** (p. ej. botón-chip "Quitar" con icono, o `swipeActions`/overlay con
     confirmación). Estética nativa coherente con las tiles de Mercado.
     (FR9; BR9.1)
  Mantiene invariantes (FR7), build verde y los 204 tests; solo vistas SwiftUI.

- [ ] **Step 14 — Bug de recarga por campeonato + 2 ajustes UX (revisión 3).**
  1. **BUG (prioritario): cambiar de campeonato no recarga la Calculadora.** El
     `onChange(of: viewModel.activeChampionshipId)` observa
     `activeStore.activeId` (getter de `UserDefaults`, NO observable por
     SwiftUI), así que no dispara. Fix: observar la propiedad **observable**
     `budgetViewModel.activeChampionship?.championshipId` (el `BudgetViewModel`
     es `@Observable` y `selectChampionship` la muta) y forzar
     `viewModel.load()` al cambiar. (FR1.3)
  2. **Icono de la pestaña**: `calculator` no se renderiza en dispositivo;
     elegir un SF Symbol NATIVO válido parecido a calculadora/matemáticas
     (candidatos: `plusminus`, `x.squareroot`, `plus.forwardslash.minus`,
     `plusminus.circle`). (FR11.1)
  3. **Confirmaciones de vender/retirar**: el `confirmationDialog` se percibe
     "cutre"; sustituir por una confirmación más elegante y nativa (sheet con
     detente o diseño propio con botones DS), manteniendo semántica y
     accesibilidad. (FR8.2, FR9.1)
  Mantiene invariantes (FR7), build verde y los 204 tests; solo vistas SwiftUI.

- [x] **Step 15 — Haptics de selección (revisión 4).** Añadir respuesta háptica
  al **seleccionar/deseleccionar** un jugador en la Calculadora: en el `onTap`
  de la card (o en `toggleSelection`), disparar un
  `UISelectionFeedbackGenerator().selectionChanged()` bajo
  `#if canImport(UIKit)`, respetando Reduce Motion. Patrón ya documentado en
  `native-ios-ui-patterns.md`. Solo vistas SwiftUI; build verde y 204 tests.

## Estrategia de test (del Testing Contract)

Metodología **test-after**, estrategia **minimal**: implementar cada capa
testeable y después escribir y correr sus tests. La lógica pura testeable va en
`FutmondoKit` (XCTest ejecutable en WSL); las vistas SwiftUI se validan en
dispositivo y quedan fuera del cómputo de cobertura (llvm-cov no fiable en WSL).
La suite existente (168 tests) debe seguir en verde; este scope `refactor` no
añade piso de cobertura nuevo.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "este intent entrega **artefactos de diseño** (tokens y pantallas de referencia), no capas de software testeable, así que no introduce ningún piso de cobertura ni tests nuevos; la única obligación de testing es que la **suite existente siga en verde** (backend `pytest` + `pytest-cov` desde `backend/` con fixtures fake in-memory de `conftest.py`; frontend `ng test` con Vitest). Cuando SÍ se produzca código de UI, se implementa cada capa testeable y después se escriben y corren sus tests (test-after).",
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
      "text": "- **Methodology**: test-after\n- **Ordering**: este intent entrega **artefactos de diseño** (tokens y pantallas\n  de referencia), no capas de software testeable, así que no introduce ningún\n  piso de cobertura ni tests nuevos; la única obligación de testing es que la\n  **suite existente siga en verde** (backend `pytest` + `pytest-cov` desde\n  `backend/` con fixtures fake in-memory de `conftest.py`; frontend `ng test` con\n  Vitest). Cuando SÍ se produzca código de UI, se implementa cada capa testeable\n  y después se escriben y corren sus tests (test-after).\n- **Methodology evidence**: posture test-after afirmada y vigente en memoria del\n  equipo; la suite backend es **characterization-first** (~50+ `test_*.py`) y la\n  frontend es Vitest sobre `@angular/build:unit-test`; ambas preexisten a este\n  intent y no cambian por él.\n- Un intent de diseño no modifica código de aplicación, por lo que no debería\n  disparar fallos de la suite; pero el gate de CI corre igual en el PR y dentro de\n  `ng test` el enforcement de cobertura (`coverageThresholds` en `angular.json`,\n  `statements 19` / `branches 19` / `functions 17` / `lines 18`) es **bloqueante**:\n  si un rojo aparece por **flapping** ajeno al cambio, se **arregla el test\n  no-determinista**, NUNCA se baja un umbral/piso ni se añade `continue-on-error`\n  (invariante del trinquete: sólo sube).\n- **Matiz nativo iOS (riesgo a documentar en diseño, NO obligación de este\n  intent)**: el arnés de test del frontend Angular (Vitest `4.1.11` +\n  `@vitest/coverage-v8` + `jsdom`, specs que montan componentes Material/CDK) **no\n  porta 1:1** a un target SwiftUI: no hay DOM/`jsdom` ni runner Angular CLI de\n  Vitest, y una UI SwiftUI se verifica con el toolchain nativo de Apple\n  (XCTest / previews / snapshot), no con Vitest/jsdom. Una eventual capa de UI\n  nativa implicaría **rehacer el arnés de test de UI** y **re-basar** cualquier\n  umbral sobre un runner distinto (suelo nuevo bajo tooling distinto, no un\n  trinquete que suba), más una dimensión **E2E/dispositivo** (iPhone 13 Pro) hoy\n  inexistente. El **backend no cambia** por una capa de diseño nativa (ni\n  `pytest` ni el piso `--cov-fail-under=27`), para que nadie induzca trabajo\n  backend inexistente.\n- **No aplica en este intent**: los pisos de cobertura heredados (backend\n  `--cov-fail-under=27`; frontend `19/19/17/18`) son estado del repo que este\n  intent **no modifica**; no se induce trabajo de ratchet ni de paridad de señal."
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
  "input_sha256": "sha256:bc969b4899cbd00407406542682513c10c83142b7bcba4ede89512af9b53648d",
  "contract_sha256": "sha256:93a2890923ed7ee93674a1684b56d1846e71aac5bf9349afac336529ad74a295"
}
```
