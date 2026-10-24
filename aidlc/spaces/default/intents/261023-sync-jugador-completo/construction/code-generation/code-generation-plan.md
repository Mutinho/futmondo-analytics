# Code Generation Plan — Enriquecimiento del sync de jugadores

## Summary

- Builds: amplía `players` con 6 columnas (`points`, `change`, `home_average`, `away_average`, `matches`, `status`), hace que `PlayersFullSyncOrchestrator` las extraiga del objeto vivo y que `favorites_read` las sirva desde el sync (equipo/escudo por `teamId` con `LALIGA_TEAMS`), sin tocar god-files ni SQL-en-router ni el contrato.
- Touches: `schema_lifecycle_adapter.py` (ALTER idempotente), `players_adapter.py` (upsert +columnas), `players_full/orchestrator.py` (extracción), `sync_read/favorites_read.py` (lectura), y tests en `backend/tests/`.
- Tests: characterization-first (congela origen actual de points/status + forma del contrato) + tests de las capas nuevas con fakes in-memory; ~12-16 tests. Suite existente en verde, piso de cobertura no baja.

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
(characterization-first; suite en verde; piso de cobertura no baja). Capas
aplicables: data-model/DB (migración + upsert), business logic (extracción del
orquestador), API/endpoint (favorites_read). No hay capa frontend.

## Implementation Steps

- [x] **Step 1 — Caracterización PRIMERO.** Tests que congelan el comportamiento
  ACTUAL antes de tocar nada (deben pasar contra el código actual): (a) campos que
  `PlayersFullSyncOrchestrator` pone en `player_records`/`stats_payload`; (b)
  selección de favoritos (`fav` True AND no `userteamId`); (c) forma del contrato
  de `favorites/my` (20 claves/orden); (d) **origen actual de `points`
  (SUM(player_performance), 0 para free agents) y de `status` (hardcoded '')**;
  (e) no-leak de credenciales en la ruta de error del sync. → BR5.1
- [x] **Step 2 — Runner.** Registrar el comando unit-scoped en
  `unit-test-instructions.md` (pytest desde `backend/`, ficheros nuevos). No baja
  `--cov-fail-under=27`. → NFR2
- [x] **Step 3 — Migración de esquema (data-model) implementar.** En
  `schema_lifecycle_adapter.py` (`_ensure_schema_updates`, junto al ALTER de
  `team_prizes`), añadir `ALTER TABLE players ADD COLUMN IF NOT EXISTS` para
  `points INTEGER DEFAULT 0`, `change INTEGER DEFAULT 0`, `home_average REAL`,
  `away_average REAL`, `matches INTEGER DEFAULT 0`, `status TEXT DEFAULT ''`
  (idempotente, no destructivo). → BR2.1/BR2.2/NFR6
- [x] **Step 4 — Tests de la migración (test-after).** Verificar que tras
  `_ensure_schema_updates` las columnas existen y son idempotentes (correr dos
  veces no falla). → BR2.1
- [x] **Step 5 — Repository/upsert implementar.** En `players_adapter.py`
  (`save_players_batch` y, si aplica, el single-insert), incluir las 6 columnas
  nuevas en el INSERT y en el `ON CONFLICT ... DO UPDATE SET`. → BR2.1
- [x] **Step 6 — Tests del upsert (test-after).** Sembrar y verificar que los 6
  campos se persisten y se actualizan en conflicto. → BR2.1
- [x] **Step 7 — Business logic (orquestador) implementar.** En
  `players_full/orchestrator.py`, añadir a `player_records` los 6 campos del
  objeto vivo; `home_average`/`away_average` normalizados con `clean_float`
  (NaN/vacío/null/no-parseable → None); `points`/`change`/`matches` default 0;
  `status` default ''. El resto (stats, orphan, favorites, metadata, SyncResult)
  intacto. → BR1.1/BR1.2
- [x] **Step 8 — Tests del orquestador (test-after).** Congelar+extender: los 6
  campos llegan a `player_records`; normalización de "NaN"/vacío; `SyncResult`
  byte-identical. → BR1.1/BR1.2
- [x] **Step 9 — API/endpoint (favorites_read) implementar.** SELECT + mapeo de
  `points`/`change`/`home_average`/`away_average`/`matches`/`status` desde
  `players`; `team`/`team_logo` por `real_team_id` con `LALIGA_TEAMS` (fallback
  `real_team_name`; peor caso ''/''); defaults BR5.2 cuando columna nula; orden y
  20 claves intactos. → BR3.1/BR4.1/BR4.2/BR5.2
- [x] **Step 10 — Tests de favorites_read (test-after).** Favorito con columnas
  pobladas → campos reales; con columnas nulas → defaults; team por LALIGA_TEAMS;
  peor caso ''/''; orden preservado; contrato de 20 claves. → BR3.1/BR4.x/BR5.2
- [x] **Step 11 — Config/entorno.** Sin dependencias nuevas; confirmar imports. → tech-stack
- [x] **Step 12 — Documentación y trazabilidad.** `code-summary.md`,
  `traceability.json` (BR/FR → fichero).

## Rule → code-step traceability

| Paso | Cubre |
|---|---|
| 1 | BR5.1 (characterization-first, incl. origen points/status) |
| 2 | NFR2 |
| 3, 4 | BR2.1, BR2.2, NFR6 |
| 5, 6 | BR2.1 |
| 7, 8 | BR1.1, BR1.2 |
| 9, 10 | BR3.1, BR4.1, BR4.2, BR5.2 |
| 11, 12 | tech-stack, trazabilidad |
