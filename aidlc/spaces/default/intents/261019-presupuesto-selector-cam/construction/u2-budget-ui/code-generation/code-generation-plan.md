# Code Generation Plan — U2 `u2-budget-ui`

> Fase: construcción. Unidad: `u2-budget-ui` (app `FutmondoApp`, SwiftUI). Idioma: castellano; tokens técnicos verbatim en inglés.
> Lenguaje: identificadores/comentarios en inglés; prosa en castellano. Todo bajo `#if canImport(SwiftUI)`.

## Re-trabajo de fidelidad visual (iteración 2 — tras validación en dispositivo)

La primera iteración cumplía funcionalmente pero no la fidelidad NFR3 ni el pulido iOS 26. Decisiones del propietario (2026-10-20):

- **D1 — `BudgetRow` como CARD** (no `List` plana): superficie elevada con esquinas redondeadas y **sombra suave** (nuevo token de elevación en el DesignSystem de F1, p. ej. `DSShadow`/`cardStyle`), padding generoso (`DSSpacing`), `team_name` en grande (DSFont h3); **saldo y rendimiento destacados** con color money, **rendimiento como badge**; **puja máxima / premios** en fila secundaria con etiquetas pequeñas en mayúsculas (`SALDO`/`RENDIMIENTO`/`PUJA MÁXIMA`/`PREMIOS`, como la web). La `List` usa fondo transparente/insets para que se vean las cards separadas.
- **D2 — Tab bar FLOTANTE Liquid Glass**: subir el **deployment target de `ios` a iOS 26** en `Package.swift` (hoy compila contra ios15, lo que impide el estilo flotante nativo) y usar el `TabView` nativo sin efecto propio (coste 0 €). App queda iOS 26+.
- **D3 — Selector de campeonato como CHIP** en la navigation bar: recuadro redondeado con **icono** (p. ej. `trophy`/`sportscourt`) + nombre del campeonato activo + chevron; el `Menu` desplegado marca el activo. No texto pelado.
- **D4 — Orden como CHIP "Ordenar por: X ▾" BAJO el título** (no flechas en la topbar): un control con etiqueta clara dentro del contenido; se quita el botón de flechas de la toolbar.
- **D5 — Logout en MENÚ DE AJUSTES (overflow ···)** en la navigation bar (icono `ellipsis`/`gearshape`), no un botón suelto; invoca el mismo `AuthViewModel.logout()` + `phase=.noSession`.

El resto de contratos (consumo de U1, seguridad, estados, integración en `SplashView.case .resumed`, sesión F1 intacta) se mantienen. Posible ampliación del DesignSystem de F1 (token de elevación/sombra y estilo de card) como componentes nuevos, coste 0 €, sin romper el catálogo existente.

## Alcance de código (nuevo, en `ios/Sources/FutmondoApp/Budget/`)

1. `RootTabView.swift` — `TabView` con pestaña "Presupuesto" (Liquid Glass automático) + `NavigationStack` con `BudgetView`; recibe el `BudgetViewModel` y un callback de logout; aloja "Cerrar sesión" (mismo `AuthViewModel.logout()` + `phase=.noSession`).
2. `BudgetView.swift` — pantalla con `.toolbar` (`ChampionshipMenu` en el título + `SortMenu`); cuerpo por `BudgetState`: `LoadingState` / `List` de `BudgetRow` / `emptyTeams` / `noChampionships` (selector deshabilitado) / `ErrorState` (foco en Reintentar).
3. `BudgetViewModel.swift` — `@MainActor @Observable`; inyecta `BudgetService`/`ChampionshipService`/`ActiveChampionshipStore` + `TeamBudgetSort`/`ActiveChampionshipResolver` (U1); `load()`/`selectChampionship()`/`setSort()` con la máquina de estados; `loading` síncrono antes del `await`; error verbatim de U1 sin interpolar.
4. `BudgetRow.swift` — fila: `team_name` (DSFont h3), `balance`/`performance` (DSColor money + `MoneyFormatter.format(signed:)`), `max_bid`/`prizes` secundarios; label VoiceOver compuesto; sin color como único portador.
5. `ChampionshipMenu.swift` — `Menu` en el título (activo con ✓; deshabilitado si vacío).
6. `SortMenu.swift` — `Menu` de orden (6 claves; activa con ✓).

Integración: sustituir el cuerpo de `SplashView.content` → `case .resumed` (hoy `authenticatedPlaceholder`) por `RootTabView`, dejando `runBootstrap`/`.onChange`/demás fases intactas; componer el `BudgetViewModel` con las impls de U1 (`HTTPBudgetService`/`HTTPChampionshipService` sobre el `NetworkClient` ya cableado en `FutmondoApp.swift`, `UserDefaultsActiveChampionshipStore`). Sin cambios de `Package.swift` ni de `Networking/Auth/DesignSystem`/`AuthViewModel`/`LoginView`.

## Pasos (test-after; capa testeable = lógica del VM que no dependa de SwiftUI)

1. Verificar runner: comando unit-scoped exacto `cd ios && swift build && swift test`.
2. Implementar los 6 componentes SwiftUI + la integración en `SplashView`.
3. Si hay lógica pura extraíble del VM (p. ej. mapear `BudgetState` desde un resultado, decidir si persistir el activo resuelto), colocarla donde sea testeable (preferible en `FutmondoKit` o en un helper `#if canImport` neutro) y añadir XCTest; las vistas y el VM-SwiftUI no se testean en WSL (cobertura no fiable).
4. `swift build` (+ `swift test` para no regresar U1/F1) como checkpoint ejecutable; validación de render/accesibilidad/fidelidad en iPhone 13 Pro.

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

### Nota de aplicación (capa SwiftUI)
Los `testable_layers` genéricos del contrato ("Frontend behavior") se cubren en U2 por **validación en dispositivo** (iPhone 13 Pro), no por XCTest en WSL (cobertura de UI no fiable, regla durable). La lógica pura ya vive en U1 y está testeada. Si surge lógica pura nueva extraíble del `BudgetViewModel`, se coloca donde sea testeable y se cubre con XCTest. El checkpoint ejecutable es `swift build` (+ `swift test` para no regresar U1/F1).

## Verificación (checkpoint)

`cd ios && swift build && swift test` verde (no regresión de los 82 tests de U1/F1) + validación de render/accesibilidad/fidelidad en iPhone 13 Pro.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/functional-design/{functional-spec.md,frontend-components.md}`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u2-budget-ui/nfr-design/{performance-design.md,security-design.md,logical-components.md}`
- `ios/Sources/FutmondoApp/{FutmondoApp,SplashView}.swift`, `ios/Sources/FutmondoKit/Budget/*` (U1), `ios/Sources/FutmondoApp/DesignSystem/*` (F1)

## Assumptions & Open Questions

None.
