# Code Generation Plan — Optimización de latencia (read-from-sync)

## Summary

- Builds: una capa de lectura estrecha `backend/app/services/sync_read/` (`favorites_read.py`, `market_read.py`) que sirve `favorites/my` desde Neon sincronizado (elimina la descarga viva `get_championship_players`) y deja `market/today` leyendo catálogo de caché + 1 llamada viva de pujas; los routers delegan en la capa.
- Touches: `backend/app/services/sync_read/` (nuevo), `backend/app/api/v1/endpoints/favorites.py` y `market.py` (delegan), y tests nuevos en `backend/tests/`.
- Tests: characterization-first (congelar el shape actual ANTES de cambiar la fuente) + tests de la capa nueva con el fake in-memory de `conftest.py`; ~10-14 tests. Suite existente en verde.

## Decisión a validar contigo (mapeo campo→tabla) — ACTUALIZADA

Tras revisar el código real (incluida la tabla `market_today`), **casi todos**
los campos de `favorites/my` SÍ están sincronizados. Clave: los favoritos son
**agentes libres** → están en `market_today`, que persiste `change`, `average`,
`home_average`, `away_average`, `matches_played`, `points` y el `raw_json`
completo de cada jugador.

| Campo del contrato | ¿Sincronizado? | Fuente en sync |
|---|---|---|
| `name`, `slug`, `position`(role), `position2`(role2), `value` | ✅ | `players` / `market_today` |
| `team`, `team_logo` | ✅ | `players`/`market_today` + fallback `LALIGA_TEAMS` |
| `average`, `home_average`, `away_average`, `matches` | ✅ | **`market_today`** (lookup por `player_id`) |
| `change` | ✅ | **`market_today.change`** |
| `points` | ✅ | `market_today.points` / `player_performance` |
| `sofascore_rating`, `sofascore_url`, `starter_pct` | ✅ | `sofascore_cache` (`_sofascore_helpers`) |
| free-agent (owner nulo) | ✅ | `player_championship_stats.owner_team_id` |
| `rating` (plano), `status` | ⚠️ sin fuente clara | el front **no los pinta** (la card usa `sofascore_rating`); default actual `0`/`''` |

**Propuesta (⭐):** el reader de favoritos lee los jugadores desde los datos
sincronizados y hace un **lookup por `player_id` contra `market_today`** para
`change`/averages/`matches`/`points`. Resultado: en el caso normal (favorito en
el mercado de hoy) **todos los campos visibles salen correctos**, idénticos a
hoy. Solo si un favorito no estuviera en el `market_today` del día, esos pocos
numéricos caen al mismo default que el contrato ya produce (`change=0`,
averages `None`, `matches=0`) — y el front ya lo renderiza con elegancia
(muestra `-` o no pinta el detalle, nunca un "null" crudo). `rating`(plano) y
`status` mantienen su default actual porque el front no los muestra.

Esto **no toca la ruta de sync** (solo lee tablas ya sincronizadas) y mantiene
el **shape del contrato byte-identical**. Tests de caracterización congelan que
los valores servidos coinciden con los de hoy cuando el jugador está en
`market_today`, y que los defaults coinciden cuando no lo está.

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

Metodología **test-after**, estrategia **minimal**, scope **refactor**
(characterization-first; la suite existente se mantiene en verde; no se baja
ningún piso). Las capas testeables aplicables aquí son **Repository/data access**
(la capa `sync_read`) y **API/endpoint** (los routers); no hay capa frontend.

## Implementation Steps

- [x] **Step 1 — Estructura.** Crear el paquete `backend/app/services/sync_read/`
  con `__init__.py`. (Skeleton de producción; sin lógica aún.) → FR5.1/BR1.1
- [x] **Step 2 — Runner.** Verificar el runner existente y registrar el comando
  unit-scoped exacto en `unit-test-instructions.md` (pytest desde `backend/`,
  filtrando los ficheros nuevos). No se baja `--cov-fail-under=27`. → NFR4
- [x] **Step 3 — Caracterización PRIMERO (data/endpoint actual).** Escribir tests
  que **congelan el shape actual** de `favorites/my` (claves exactas, orden
  `position_order` asc + `value` desc, defaults ante campos ausentes) y de
  `market/today` (claves de `players[]` incl. `current_bid`/`current_bid_id`, y
  `user_info` con `available_for_bids = max_bid − active_bids_total`), usando
  dobles en memoria. Estos tests deben pasar contra el código ACTUAL antes de
  tocarlo. → NFR4, BR6.1
- [x] **Step 4 — Repository (`favorites_read.py`) implementar.** Función
  `read_favorites(db, championship_id, user_id) -> list[dict]` que: SELECT
  `player_id` de `player_favorites`; si vacío → `[]`; SELECT jugadores desde
  `players` JOIN `player_championship_stats` (free-agent: `owner_team_id` NULL)
  filtrado por los fav_ids; **lookup por `player_id` contra `market_today`** para
  `change`/`average`/`home_average`/`away_average`/`matches`/`points`; enriquecer
  con `_sofascore_helpers` (rating/url/starter_pct); mapear al contrato (defaults
  del front solo si el favorito no está en `market_today`); ordenar
  `position_order` asc, `value` desc. SQL parametrizado (`db.adapt_params`).
  Devuelve señal `has_synced=False` cuando 0 filas sincronizadas. → BR2.1/BR2.2/NFR5.3
- [x] **Step 5 — Repository tests (test-after).** Tests de `favorites_read` con
  `fake_db`: favoritos free-agent mapeados, orden preservado, 0 filas → señal de
  fallback, defaults de campos no sincronizados, exclusión de no-favoritos y de
  owned. → BR2.x, BR3.1
- [x] **Step 6 — Repository (`market_read.py`) implementar.** Función
  `read_market_catalog(db, championship_id) -> list[dict] | None` (catálogo desde
  `market_today`; `None`/vacío → señal de fallback). La llamada viva de pujas y
  el ensamblado de `user_info` quedan en el router (usan el cliente), pero el
  cálculo puro `available_for_bids = max_bid − active_bids_total` se extrae a una
  función testeable. → BR4.1/BR5.1
- [x] **Step 7 — Repository tests (test-after).** Tests de `market_read`:
  catálogo desde caché, 0 filas → señal de fallback, y el cálculo de `user_info`
  (incl. degradación de pujas a cero si la llamada falla, BR3.2). → BR4.x, BR3.2
- [x] **Step 8 — API/endpoint `favorites.py` (modificar in-place).** El handler
  `/my` llama a `read_favorites`; si `has_synced` → sirve desde sync (sin
  `get_championship_players`); si no → **fallback** a la ruta viva actual +
  `logger.info` sync-miss. El contrato de respuesta no cambia. → BR2.1/BR3.1/BR6.1
- [x] **Step 9 — API/endpoint `market.py` (modificar in-place).** El handler usa
  `read_market_catalog` para el catálogo (fallback vivo si vacío) y mantiene la
  llamada viva de pujas; degradación a cero + `logger.warning` si falla. → BR4.1/BR3.2
- [x] **Step 10 — API tests (test-after).** Tests de endpoint con dobles: sirve
  desde sync cuando hay datos; fallback cuando no; contrato intacto; logs sin
  credenciales. → BR3.1/BR6.1/NFR5.4
- [x] **Step 11 — Errores sin credenciales.** Verificar que el fallback y el fallo
  de pujas propagan/loguean sin password/token (excepción tipada, `exc_info`
  limpio). → NFR5.4
- [x] **Step 12 — Config/entorno.** Ninguna dependencia nueva; confirmar imports y
  que el paquete se descubre. → tech-stack-decisions
- [ ] **Step 13 — Documentación y trazabilidad.** `code-summary.md`,
  `traceability.json` (AC/BR/NFR → fichero), `source-manifest.json` si aplica.

## Story / rule → code-step traceability

| Paso | Cubre |
|---|---|
| 1, 2 | FR5.1, BR1.1, NFR4 |
| 3 | BR6.1, NFR4 (characterization-first) |
| 4, 5 | BR2.1, BR2.2, BR3.1, NFR5.3 |
| 6, 7 | BR4.1, BR4.2, BR5.1, BR3.2 |
| 8, 9 | BR2.1, BR3.1, BR4.1, BR6.1 |
| 10, 11 | BR3.1, BR3.2, BR6.1, NFR5.4 |
| 12, 13 | tech-stack, trazabilidad |
