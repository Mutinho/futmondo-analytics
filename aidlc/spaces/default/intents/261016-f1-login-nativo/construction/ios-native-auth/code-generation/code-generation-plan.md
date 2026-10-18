# Code Generation Plan — `ios-native-auth` (Bolt 3 de F1)

> Fase: construcción (code-generation). Auth nativa iOS. Idioma: castellano; identificadores/código
> en inglés. Artefacto sujeto a aprobación de plan y revisión adversarial.

## Verificación (opción A, como el Bolt 2)

`swift test` ejecutado por el propietario en WSL cubre la **lógica testeable sin dispositivo**:
`AuthService` (actor) con dobles de `NetworkClient` y `KeychainStore` in-memory, `TokenHolder`
(NSLock), DTOs. El `KeychainTokenStore` real (`SecItem`), las vistas SwiftUI y el flujo visual se
validan en el iPhone 13 Pro con `xtool dev build`. El Verification Command del checkpoint es
`cd ios && swift test` (ya fijado).

## Ficheros a crear/editar

| Fichero | Acción | Detalle |
|---------|--------|---------|
| `ios/Sources/FutmondoKit/Auth/KeychainStore.swift` | Crear | protocolo `KeychainStore`. |
| `ios/Sources/FutmondoKit/Auth/KeychainTokenStore.swift` | Crear | impl `SecItem` (AfterFirstUnlockThisDeviceOnly, upsert, OSStatus). |
| `ios/Sources/FutmondoKit/Auth/InMemoryKeychainStore.swift` | Crear | doble in-memory para `swift test`. |
| `ios/Sources/FutmondoKit/Auth/TokenHolder.swift` | Crear | snapshot con `NSLock` (portable Linux/Darwin). |
| `ios/Sources/FutmondoKit/Auth/AuthDTOs.swift` | Crear | Login/Refresh request/response (Codable). |
| `ios/Sources/FutmondoKit/Auth/AuthError.swift` | Crear | enum `AuthError` Equatable. |
| `ios/Sources/FutmondoKit/Auth/AuthService.swift` | Crear | `actor AuthService` (login/refresh/bootstrap/logout, reintento coalescido, borrado doble). |
| `ios/Sources/FutmondoApp/AuthViewModel.swift` | Crear | `@Observable`/`ObservableObject`: estado, submitLogin, logout; limpia password. |
| `ios/Sources/FutmondoApp/LoginView.swift` | Crear | SwiftUI según refined-mockups. |
| `ios/Sources/FutmondoApp/SplashView.swift` | Crear | SwiftUI (5 estados). |
| `ios/Sources/FutmondoApp/FutmondoApp.swift` | Crear | `@main` App que arranca en Splash. |
| `ios/Package.swift` | Editar | añadir target `FutmondoApp` (ejecutable/app) y mover el test target; `FutmondoKit` sigue como library testeable. |
| `ios/xtool.yml` | Editar | product apuntando a `FutmondoApp`. |
| `ios/Tests/FutmondoKitTests/AuthServiceTests.swift` | Crear | XCTest de `AuthService` con dobles (login OK/401, bootstrap 3 ramas, refresh+reintento+coalescing, logout+borrado doble+pendingLogoutRevocation, TokenHolder). |

## Enfoque

1. `FutmondoKit/Auth`: `KeychainStore` + `KeychainTokenStore` (real, `#if canImport(Security)`) +
   `InMemoryKeychainStore` (test) + `TokenHolder` (NSLock) + `AuthDTOs` + `AuthError`.
2. `AuthService` (actor): orquesta usando `NetworkClient` (Bolt 2) y `KeychainStore`; reintento
   coalescido; borrado doble (holder primero, actor después) en logout.
3. App target `FutmondoApp`: `AuthViewModel`, `LoginView`, `SplashView`, `FutmondoApp` (@main).
4. Tests `AuthServiceTests` (lógica sin dispositivo) para `swift test`.

## Invariantes y límites

- Access token en memoria (actor + holder); refresh token solo en Keychain; password del form
  limpiado tras login/logout; solo SDK de Apple; Face ID diferido; sin pantallas de datos (F2).
- `AuthService` es `actor`; `TokenHolder` usa `NSLock` para compilar en `swift test` (Linux).

## Progreso (code-generation)

- [x] `ios/Sources/FutmondoKit/Auth/KeychainStore.swift` — protocolo creado.
- [x] `ios/Sources/FutmondoKit/Auth/KeychainTokenStore.swift` — impl `SecItem` bajo `#if canImport(Security)`.
- [x] `ios/Sources/FutmondoKit/Auth/InMemoryKeychainStore.swift` — doble in-memory (NSLock), compila en Linux.
- [x] `ios/Sources/FutmondoKit/Auth/TokenHolder.swift` — snapshot `Sendable` con `NSLock`.
- [x] `ios/Sources/FutmondoKit/Auth/AuthDTOs.swift` — DTOs `Codable`/`Sendable` snake_case (incl. `refresh_token`, D-01).
- [x] `ios/Sources/FutmondoKit/Auth/AuthError.swift` — enum `AuthError` + conformidades `Sendable` locales de tipos Bolt 2.
- [x] `ios/Sources/FutmondoKit/Auth/Session.swift` — `Session` + `SessionState` (no en la tabla original; separado para claridad).
- [x] `ios/Sources/FutmondoKit/Auth/AuthService.swift` — `actor` (login/refresh/bootstrap/logout, coalescing, borrado doble).
- [x] `ios/Sources/FutmondoKit/Auth/LogoutFlagStore.swift` — abstracción `Sendable` del booleano `pendingLogoutRevocation` (añadido para desacoplar el actor de `UserDefaults`, no `Sendable`).
- [x] `ios/Sources/FutmondoApp/AuthViewModel.swift` — `@Observable`, limpia password.
- [x] `ios/Sources/FutmondoApp/LoginView.swift` — SwiftUI según refined-mockups.
- [x] `ios/Sources/FutmondoApp/SplashView.swift` — SwiftUI (estados de bootstrap).
- [x] `ios/Sources/FutmondoApp/FutmondoApp.swift` — `@main` App arranca en Splash.
- [x] `ios/Sources/FutmondoApp/main.swift` — entry point no-op solo en Linux (aislamiento de `swift test`; añadido).
- [x] `ios/Package.swift` — añadido target ejecutable `FutmondoApp`; test target solo depende de `FutmondoKit`.
- [x] `ios/xtool.yml` — `product: FutmondoApp`.
- [x] `ios/Tests/FutmondoKitTests/AuthServiceTests.swift` — 14 XCTest (login OK/401, bootstrap 4 ramas, refresh+coalescing, logout+borrado doble+pendingLogoutRevocation, TokenHolder).
- [x] Documentación y trazabilidad — `code-summary.md`, `traceability.json`.

> Chequeo de compilación/efecto del agente: `swift test` → 28 tests en verde (14 nuevos + 14 de
> Bolt 2, sin regresión), incl. coalescing (2 refresh concurrentes → 1 llamada de red). La
> **verificación oficial del bolt** la corre el propietario en WSL: `cd ios && swift test` y
> `cd ios && xtool dev build` en el iPhone 13 Pro.

## Sources

- [consumes] functional-spec.md, entities.md, rules.md, security-design.md, logical-components.md,
  contract-summary.md, requirements.md (FR-1,2,3,5,6,8; NFR-1,2,3), refined-mockups.

## Assumptions & Open Questions

None.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "este intent entrega **documentos de análisis** (no capas de software testeable), así que no introduce ningún piso de cobertura ni tests nuevos; la única obligación de testing es que la **suite existente siga en verde** (backend `pytest` + `pytest-cov` desde `backend/` con fixtures fake in-memory de `conftest.py`; frontend `ng test` con Vitest). Un intent de análisis no modifica código de aplicación, por lo que no debería disparar fallos de la suite; pero el gate de CI corre igual en el PR documental y dentro de `ng test` el enforcement de cobertura (`coverageThresholds` en `angular.json`) es **bloqueante**: si un rojo aparece por **flapping** de cobertura ajeno al cambio, se **arregla el test no-determinista**, NUNCA se baja un umbral/piso ni se añade `continue-on-error` (coherente con el invariante del trinquete). Se conserva la metodología test-after del equipo para cuando se produzca código.",
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
      "text": "- **Methodology**: test-after\n- **Ordering**: este intent entrega **documentos de análisis** (no capas de\n  software testeable), así que no introduce ningún piso de cobertura ni tests\n  nuevos; la única obligación de testing es que la **suite existente siga en\n  verde** (backend `pytest` + `pytest-cov` desde `backend/` con fixtures fake\n  in-memory de `conftest.py`; frontend `ng test` con Vitest). Un intent de\n  análisis no modifica código de aplicación, por lo que no debería disparar\n  fallos de la suite; pero el gate de CI corre igual en el PR documental y dentro\n  de `ng test` el enforcement de cobertura (`coverageThresholds` en\n  `angular.json`) es **bloqueante**: si un rojo aparece por **flapping** de\n  cobertura ajeno al cambio, se **arregla el test no-determinista**, NUNCA se baja\n  un umbral/piso ni se añade `continue-on-error` (coherente con el invariante del\n  trinquete). Se conserva la metodología test-after del equipo para cuando se\n  produzca código.\n- **Línea base durable (para cuando SÍ haya código)**: posture **test-after**;\n  tests como entregable de primera clase que **aseveran el efecto**\n  (payload/estado/modo de fallo), nunca `assert True` ni specs espejo; fixtures\n  fake in-memory sin red, sin BD real y sin credenciales/tokens reales (gitleaks\n  escanea también los tests). El trinquete de cobertura (backend\n  `--cov-fail-under` en `pytest.ini`; frontend `coverageThresholds` en\n  `angular.json`) **sólo sube**, nunca se relaja para pasar el gate; el flapping\n  se arregla en el test no-determinista, no bajando el piso.\n- **Portabilidad de la posture al target nativo (riesgo a documentar en\n  feasibility, no obligación de este intent)**: la suite frontend actual (15\n  `*.spec.ts` sobre `@angular/build:unit-test`, builder Vitest `4.1.11` +\n  `@vitest/coverage-v8` + `jsdom`) **no porta tal cual** a NativeScript: no hay\n  DOM/`jsdom`, el runner Angular CLI de Vitest no aplica y los specs que montan\n  componentes Material/CDK no portan; los specs de servicios/RxJS/signals son\n  portables casi 1:1. Una migración nativa implicaría **rehacer el arnés de test\n  de frontend** y **re-basar** el umbral de cobertura sobre un runner distinto\n  (suelo nuevo bajo tooling distinto, no un trinquete que suba), y añade una\n  dimensión **E2E/dispositivo** (iPhone 13 Pro / Samsung A17) hoy inexistente. El\n  **backend no cambia** por una migración de UI nativa (ni `pytest` ni el piso\n  `--cov-fail-under`), para que nadie induzca trabajo backend inexistente.\n- **No aplica en este intent**: los valores concretos de piso de cobertura\n  medidos en intents previos (backend `--cov-fail-under=27`; frontend\n  statements 19 / branches 19 / functions 17 / lines 18) son estado heredado del\n  repo que este intent **no modifica**; no se induce trabajo de ratchet ni de\n  paridad de señal, propio de los intents de CI gate-hardening."
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
  "input_sha256": "sha256:6e98b9132ba8e79b749d53a7ae6f4c3550076e12c3d4bdd6a030894edf88c922",
  "contract_sha256": "sha256:04402ba7dc2f6e501642e188ae320b55cd00cbf22273eea37052c7026cb53b03"
}
```
