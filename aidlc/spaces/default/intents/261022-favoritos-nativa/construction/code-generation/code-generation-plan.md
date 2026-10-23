# Code Generation Plan — Favoritos nativa iOS

## Summary

- Builds: la pantalla nativa **Favoritos** (SwiftUI) — lógica en `FutmondoKit`
  (DTO `FavoritePlayer`, `FavoritesService`, `FavoritesSorter`,
  `FavoritesPreferences`) y vistas en `FutmondoApp` (cards estilo Mercado,
  quitar de favoritos con confirmación, menú Sofascore), como 4.ª pestaña.
- Touches: crea `ios/Sources/FutmondoKit/Favorites/*` y
  `ios/Sources/FutmondoApp/Favorites/*`, añade tests en
  `ios/Tests/FutmondoKitTests/*`, y añade la 4.ª pestaña en `RootTabView` +
  cableado en `SplashView`.
- Tests: XCTest en `FutmondoKit` (`FavoritePlayer` decode incl. nulos/cero,
  `FavoritesSorter`, `FavoritesPreferences`, endpoints exactos del servicio,
  ~10-14 tests); vistas SwiftUI validadas en dispositivo (fuera de cobertura).

## Trazabilidad plan → diseño

Cada paso referencia `construction/functional-design/` (entities, rules BR*,
functional-spec, frontend-components) y los FR de `requirements.md`.

## Pasos

- [ ] **Step 1 — DTO (FutmondoKit).** `FavoritePlayer` (Codable
  snake_case→camelCase, tolerante array/wrapped como `RosterResponse`): incluye
  `rating` (decodeIfPresent, no se muestra) y `sofascore_rating` (badge/orden),
  `home_average`/`away_average`/`matches`. (FR3.2; BR3.3, entities.md)
- [ ] **Step 2 — `FavoritesService` + `HTTPFavoritesService`.** Actor sobre
  `NetworkClient`: `fetchFavorites` = `GET /api/v1/favorites/my?championship_id=<id>`;
  `unfollow` = `POST /api/v1/favorites/unfollow?championship_id=<id>&player_id=<id>`
  con **body vacío y ambos ids como query params** → `MarketWriteOutcome`
  (OJO: query params, NO body — BR8.1). Sin tocar backend. (FR1.1, FR5; C1)
- [ ] **Step 3 — `FavoritesSorter` + `FavoritesPreferences`.** Orden
  value/change/sofascoreRating/starterPct/points descendente, nils al final
  (patrón `CalculatorSorter`); preferencia de orden en `UserDefaults`
  (`KeyValueStore`). (FR4; BR4.1)
- [ ] **Step 4 — Verificar runner + registrar comando unit-scoped.**
  `swift test --package-path ios` ya existe.
- [ ] **Step 5 — Tests XCTest (FutmondoKit, test-after).** `FavoritePlayerTests`
  (decode, nulos/cero, dos ratings), `FavoritesSorterTests`,
  `FavoritesPreferencesTests`, endpoints exactos del servicio (query params de
  unfollow, no body — regresión de BR8.1).
- [ ] **Step 6 — Vistas SwiftUI (FutmondoApp).** `FavoritesViewModel`
  (@MainActor @Observable; carga reactiva al campeonato vía
  `budgetViewModel.activeChampionship` — BR1.2; unfollow con guardia + lista
  intacta en fallo — BR5.3/BR5.4), `FavoritesView`, `FavoritePlayerCard`
  (estética tiles de Mercado; nulos/cero "-" — BR3.1; media con casa/fuera/
  partidos — BR3.2; menú "…" Sofascore reutilizado), estado vacío. Reutiliza
  `ConfirmSheet` y `SofascoreDetailSheet`. Bajo `#if canImport(SwiftUI)`.
- [ ] **Step 7 — Navegación + caché.** 4.ª pestaña "Favoritos" en `RootTabView`
  (icono `star`/`star.fill`, tinte verde, accesible); `DataFreshness` +
  `loadIfNeeded` + `.refreshable`; cableado en `SplashView`. (FR8.1, FR1.4)
- [ ] **Step 8 — Build + tests verdes.** `swift build` + `swift test`; corregir
  Swift 6 device-strict (`static let`).
- [ ] **Step 9 — Documentación y trazabilidad.** `code-summary.md`,
  `traceability.json` (BR/FR → ficheros).

- [ ] **Step 10 — Eliminación local + reflow animado al quitar (revisión 1).**
  Tras un `unfollow` ACEPTADO, NO recargar (sin nueva petición al backend):
  eliminar el jugador de la lista en memoria del `FavoritesViewModel` (quitar
  por `playerId`), y animar la recolocación de las tarjetas restantes con
  `withAnimation` fluida (p. ej. `.spring`), respetando Reduce Motion. Ajustar
  BR5.2 (reemplazar `reload()` por eliminación optimista local). En fallo, la
  lista sigue intacta (BR5.4). Añadir/ajustar un test de `FavoritesViewModel`
  no aplica (lógica de VM es capa de app/vista); si la eliminación se extrae a
  una función pura testeable en FutmondoKit, cubrirla con XCTest. Solo vistas/
  VM; build verde y suite en verde.

- [ ] **Step 11 — Quitar alert de éxito + skeletons de carga (revisión 2).**
  1. **Sin alert de éxito**: al quitar de favoritos ya se ve desaparecer la
     card (animación), así que NO mostrar el aviso de éxito; mantener solo el
     aviso de ERROR (rejected/networkError). El `FavoritesNotice.success` deja
     de emitirse en el camino aceptado.
  2. **Skeletons nativos en carga**: reemplazar el estado `.loading`
     (spinner + "Cargando...") por una rejilla de **cards skeleton** que imitan
     la forma real de `FavoritePlayerCard`, usando el modificador nativo
     `.redacted(reason: .placeholder)` + un **efecto shimmer** (gradiente
     animado que recorre el placeholder), respetando Reduce Motion (sin shimmer
     si está activo). Crear un componente reutilizable (p. ej.
     `SkeletonCard` + un `ShimmerModifier` en `FutmondoApp`) pensado para
     reutilizarse en las demás pantallas después. Solo vistas; build + suite en
     verde.

- [ ] **Step 12 — Rollout del skeleton a TODAS las pantallas (ampliación de
  alcance aceptada por el propietario).** Reemplazar el estado de carga
  (spinner + "Cargando…") por el skeleton nativo en **Mercado**, **Presupuesto**
  y **Calculadora**, reutilizando `SkeletonCard`/`ShimmerModifier`/`SkeletonGrid`.
  Añadir un **`SkeletonHeader`** reutilizable (banda que imita la card de
  resumen/banner) porque Mercado (banner económico), Presupuesto (resumen) y
  Calculadora (cabecera) muestran una card de información ANTES de la lista:
  su estado de carga = `SkeletonHeader` + `SkeletonGrid`. Favoritos (sin
  cabecera) se queda solo con `SkeletonGrid`. Respetar Reduce Motion. NO cambiar
  lógica ni contratos; solo el estado `.loading`/`.idle` de cada vista. Nota:
  toca ficheros de intents ya cerrados (Mercado/Calculadora/Presupuesto) como
  cambio de UI consentido. Build verde, suite (232) en verde.

- [ ] **Step 13 — Skeleton WOW (aurora + crossfade) + SkeletonRow para
  Presupuesto (revisión 4).**
  1. **Aurora en movimiento**: el relleno de las piezas skeleton pasa de gris a
     un **gradiente de marca** (verde→violeta del design system, sutil) que se
     **desplaza** (animación continua, p. ej. `phaseAnimator`/stops en
     movimiento), sustituyendo/ampliando el shimmer. Entrada **escalonada** de
     las piezas. Respetar Reduce Motion (sin movimiento → gradiente estático).
  2. **Crossfade al contenido**: al llegar los datos, el skeleton funde
     suavemente hacia el contenido real (crossfade en el switch de estado) en
     vez de corte seco.
  3. **SkeletonRow para Presupuesto**: Presupuesto NO usa la rejilla de cards;
     muestra FILAS de equipo (`BudgetRow`: nombre + divider + SALDO/RENDIMIENTO
     + PUJA MÁXIMA/PREMIOS). Crear `SkeletonRow` fiel a esa estructura +
     `SkeletonListScreen` (columna de filas); Presupuesto lo usa en vez de
     `SkeletonScreen`/`SkeletonGrid`. Mercado/Calculadora/Favoritos siguen con
     el grid de tiles (con la aurora aplicada).
  Reutilizable; solo vistas; build verde, suite (232) en verde.

- [ ] **Step 14 — Completar el crossfade en la rama de contenido (revisión 5).**
  El skeleton se desvanece pero el contenido real entra de golpe porque solo la
  rama de carga tenía `.transition`. Añadir `.transition(.opacity)` (fade; o fade
  + leve desplazamiento) a la rama **`.data`/`.loaded`** de las 4 vistas
  (Mercado, Presupuesto, Calculadora, Favoritos), de modo que el contenido real
  **entre con fundido** mientras el skeleton se desvanece — crossfade completo.
  Respetar Reduce Motion (la `.animation(value:)` del body ya es nil con Reduce
  Motion). Solo vistas; build verde, suite (232) en verde.

- [x] **Step 15 — Crossfade REAL skeleton↔contenido (revisión 6).** El
  `.transition(.opacity)` por rama de `switch` NO cruza fiablemente en SwiftUI
  (trata el cambio como reemplazo) y las cards tienen su propia entrada que
  compite → aparecen de golpe. Rehacer con un **cross-dissolve por opacidad**:
  en cada una de las 4 vistas, montar carga y contenido en un **`ZStack`** donde
  ambas capas existen y se cruzan por `opacity` según `isLoading` (skeleton
  `opacity(isLoading ? 1 : 0)`, contenido `opacity(isLoading ? 0 : 1)`),
  animado con `.animation(value:)` (nil bajo Reduce Motion). Quitar los
  `.transition(.opacity)` por rama. Evitar que la entrada escalonada/
  `scrollTransition` de las cards compita con el fundido. Validar en
  dispositivo. Solo vistas; build verde, suite (232) en verde.

## Estrategia de test (del Testing Contract)

Metodología **test-after**, estrategia **minimal**: lógica testeable en
`FutmondoKit` con XCTest; vistas SwiftUI validadas en dispositivo (fuera de
cobertura, llvm-cov no fiable en WSL). La suite existente (204 tests) debe
seguir en verde; scope `refactor` no añade piso nuevo.

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
