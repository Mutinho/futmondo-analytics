# Code Generation Plan — U1 `u1-budget-data`

> Fase: construcción. Unidad: `u1-budget-data` (library `FutmondoKit`). Idioma: castellano; tokens técnicos verbatim en inglés.
> Lenguaje: identificadores/comentarios en inglés; prosa en castellano.

## Alcance de código (nuevo, en `ios/Sources/FutmondoKit/Budget/`)

1. `TeamBudget.swift` — DTO `Codable`/`Sendable`/`Identifiable` (12 props, `CodingKeys` snake_case, `ops` derivado).
2. `BalancesResponse.swift` — DTO.
3. `Championship.swift` — DTO (extras opcionales).
4. `ChampionshipsResponse.swift` — DTO.
5. `SortKey.swift` — enum.
6. `MoneyFormatter.swift` — formato M/K determinista (separador `,` fijo, signo ASCII `-`, half-away-from-zero por aritmética entera, sin `NumberFormatter`).
7. `TeamBudgetSort.swift` — orden descendente estable por `SortKey`.
8. `BudgetService.swift` — protocolo + `HTTPBudgetService` sobre el `NetworkClient` de F1 (GET `analytics/balances?championship_id=`).
9. `ChampionshipService.swift` — protocolo + `HTTPChampionshipService` con fallback `user/championships`→`championships`.
10. `ActiveChampionshipStore.swift` — protocolo + `UserDefaultsActiveChampionshipStore` (clave `futmondo_active_championship`).
11. `ActiveChampionshipResolver.swift` — función pura `resolve(activeId:in:)`.

No se tocan `Networking/`, `Auth/`, `DesignSystem/` salvo para **consumir** `NetworkClient`/`APIRequest`. `Package.swift` sin cambios de dependencias (`dependencies: []`).

## Pasos (test-after)

1. Verificar el runner: comando unit-scoped exacto `cd ios && swift build && swift test`.
2. Implementar DTOs + `SortKey`; luego sus tests (decode, CodingKeys, `ops`).
3. Implementar `MoneyFormatter`; luego su tabla de casos determinista.
4. Implementar `TeamBudgetSort`; luego tests de orden/estabilidad/inmutabilidad.
5. Implementar `BudgetService`/`ChampionshipService` con un `NetworkClient` fake (patrón F1); tests de decode, fallback (incl. decode-error) y propagación de error sin fuga de credenciales (NetworkError y DecodingError).
6. Implementar `ActiveChampionshipStore` + `ActiveChampionshipResolver`; tests con `UserDefaults` de suite de test y los 4 casos de resolución.
7. Correr `swift build && swift test` (checkpoint).

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

### Nota de aplicación (lógica pura iOS, no backend/frontend)
Los `testable_layers` del contrato son genéricos; en U1 la capa testeable es **lógica pura Swift en `FutmondoKit`** (DTOs, `MoneyFormatter`, `TeamBudgetSort`, servicios con fake, store/resolver). No hay DB, repo, endpoint ni frontend que implementar aquí. El volumen de la estrategia (5-8 tests por componente, happy-path + ≥2 bordes) se aplica a esos componentes.

### Nota sobre cobertura (regla durable del proyecto)
El piso de 80% line-coverage del contrato **no se verifica numéricamente** para código iOS en WSL (llvm-cov no fiable, aprendizaje durable). En su lugar: la lógica pura de U1 va a `FutmondoKit` y se cubre con XCTest ejecutable (`swift test`), apuntando a 5-8 tests por componente que ejerciten happy-path + ≥2 casos de error/borde. La suite existente (backend `pytest` / frontend `ng test`) debe seguir en verde; U1 no la toca.

## Verificación (checkpoint)

`cd ios && swift build && swift test` en verde. Validación en dispositivo NO-APLICA a U1 (sin UI).

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/functional-design/{functional-spec.md,rules.md,entities.md}`
- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/construction/u1-budget-data/nfr-design/{security-design.md,logical-components.md}`

## Assumptions & Open Questions

None.
