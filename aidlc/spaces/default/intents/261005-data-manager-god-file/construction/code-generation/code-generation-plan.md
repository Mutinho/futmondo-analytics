# Code Generation Plan — Decomposition of `data_manager_v2.py`

Intent `261005-data-manager-god-file` · Scope `refactor` · Depth Minimal ·
Zero-Unit (stage-level) · Methodology **test-after / characterization-first**.

This plan decomposes the last untouched god-file,
`backend/app/services/data_manager_v2.py` (class `DataManagerV2`, ~166 KB /
3692 lines, **57 methods**, constructor `DataManagerV2(db_path=None,
skip_init=True)` at line 30), into the repo's proven DDD pattern
(`analytics/`, `sync/*`, `assistant/`, `prizes/`), **preserving the public
surface byte-for-byte** (BR1.1/FR1.2) and **observable behavior exactly**
(BR3.1). It is characterization-first (BR2.1): freeze behavior with
effect-asserting tests over the in-memory fakes, extract, re-run the same
tests green. The inventory and coupling order below are the **starting point
closed at Plan Approval** (BR5.1/FR5.1).

The surface counts in this plan were verified live against the workspace
file: 57 four-space methods, 43 engine-branch sites
(`db_type in [...]`/`postgresql`), 23 broad/bare `except`, 16 `return None`.
Legacy error handling and set-replacement corruption points move **verbatim**
as registered debt (BR3.2/BR3.3). Consumers and SQL-in-router are **untouched**
(BR4.1/BR4.2).

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "medir y congelar la señal de cobertura y el estado advisory del gate antes de subir cualquier umbral o promover un check a bloqueante; luego sanear/silenciar quirúrgicamente la deuda heredada que cada promoción reportaría, aplicar cada endurecimiento en su commit `chore(ci)` aislado con el trinquete fijado, y sólo al FINAL del escalón fijar el piso de cobertura backend (`--cov-fail-under`) al valor medido exacto sobre la suite ya estabilizada, verificando en verde en AMBOS gates (PR + job `verify`) sin escribir asserts espejo que pasen siempre.",
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
      "text": "- **Methodology**: test-after\n- **Ordering**: medir y congelar la señal de cobertura y el estado advisory del gate antes de subir cualquier umbral o promover un check a bloqueante; luego sanear/silenciar quirúrgicamente la deuda heredada que cada promoción reportaría, aplicar cada endurecimiento en su commit `chore(ci)` aislado con el trinquete fijado, y sólo al FINAL del escalón fijar el piso de cobertura backend (`--cov-fail-under`) al valor medido exacto sobre la suite ya estabilizada, verificando en verde en AMBOS gates (PR + job `verify`) sin escribir asserts espejo que pasen siempre.\n- **Cobertura backend (FR11)**: hoy `--cov=app` es **observability-only, sin\n  piso** (`ci.yml`; `pytest.ini` documenta cobertura como métrica informativa,\n  activable con `--cov=app`). Este intent introduce un **piso bloqueante único\n  `--cov-fail-under` en `pytest.ini`** (line-coverage total, dentro del mismo\n  `addopts` de `pytest` — config, no un paso extra), fijado al **valor medido\n  exacto SIN margen** (Q6; medición previa obligatoria) y que sube **sólo por\n  trinquete**; nunca se relaja para pasar el gate. Si aparece flapping, se\n  arregla el test no-determinista, NUNCA se baja el piso. El piso es\n  **line-only** en este intent (no se añade `--cov-branch`); una eventual paridad\n  de branch-coverage con el frontend queda fuera de alcance.\n- **Paridad de la señal backend (asimetría a CREAR — FR17.3)**: `ci.yml` mide\n  `--cov=app` mientras el job `verify` de `fly-deploy.yml` corre `pytest -q`\n  **sin `--cov`**. Este intent **cierra la asimetría** llevando la misma\n  invocación con cobertura y el mismo piso a `verify`, para que un rojo de\n  cobertura no pueda colarse por el push directo a `main`. Esta paridad aterriza\n  en el **mismo commit** que introduce el piso en `ci.yml`, o inmediatamente\n  después (Q4), para que no exista una ventana en la que el piso viva sólo en el\n  PR-gate.\n- **Cobertura frontend (SÓLO ratchet — ya tiene paridad de enforcement)**: el\n  enforcement vive DENTRO de `ng test` (builder `@angular/build:unit-test` +\n  `@vitest/coverage-v8` pin `4.1.11`), con umbrales por métrica en `angular.json`\n  (`coverageThresholds`: statements 15 / branches 15 / functions 13 / lines 14),\n  y **ambos** workflows (PR-gate y push-gate) ya corren `ng test`. Es decir, el\n  frontend **YA tiene paridad de enforcement** entre gates; su única tarea en\n  este intent es **subir el ratchet** de esos cuatro umbrales al valor medido. No\n  hay paridad frontend que crear (a diferencia del backend); no se debe inducir\n  ese trabajo inexistente. `angular.json` es la fuente única de umbral (sin pasos\n  extra ni `continue-on-error`).\n- **Tooling y coste 0 €**: backend `pytest` + `pytest-cov` desde `backend/` con\n  las fixtures fake in-memory de `conftest.py` (`_FakeInMemoryDB`/`_FakeCursor`\n  SQLite `:memory:`, `clean_jwt_env`, `fake_db`) — sin red, sin BD real, sin\n  credenciales/tokens reales (gitleaks escanea también los tests). No se prevén\n  dependencias nuevas de test; cualquiera sería OSS y **fijada a versión\n  exacta**. Un piso alto con aserciones débiles es peor que uno modesto con\n  aserciones reales: la posture test-after se mantiene con specs que aseveran el\n  efecto (payload/estado/modo de fallo), nunca `assert True` ni specs espejo.\n- **Sin bajar cobertura para pasar el gate**: el ratchet (backend y frontend)\n  **sólo sube**; nunca se relaja un umbral/piso existente para hacer pasar el\n  gate."
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
  "input_sha256": "sha256:ecea62614f79c3c11fff8e333f4a41f0f402a7ee7b2dd66004a56fac66c28f13",
  "contract_sha256": "sha256:5b6e8d0595fa2a9cbd528cb7fb86e8e9ab82badb56be52a2afd06cf869fa8cd3"
}
```

### How the contract maps to THIS refactor

The methodology is **test-after**, but the team mandate specializes it to
**characterization-first** for brownfield decomposition (affirmed ALWAYS rule):
freeze the current observable behavior with effect-asserting tests over the
in-memory fakes BEFORE touching the file, then extract, then re-run the same
tests green. The `plan_profile.testable_layers` collapse here to two real
layers — **Repository / data access** (the SQL the adapter wraps) and
**Business logic** (the thin orchestrator) — the god-file has no new data model,
no new API layer (routers are untouched, BR4.1), and no frontend. "Implement
then test its layer" becomes, per module: **characterize (test) → extract
(implement) → re-run same test green**, which satisfies both the test-after
ordering and the characterization-first mandate. No coverage floor is lowered
(BR6.1); new characterization tests only ratchet `--cov-fail-under` up.

## Target DDD shape (the proven reference, fixed by C1)

Each extracted responsibility instantiates the same four components the repo
already uses in `analytics/` and `sync/*`:

- `domain/ports.py` — a `typing.Protocol` consumer-owned port: ONLY the data
  the responsibility needs; **no SQL, no framework** (BR1.3).
- `application/<resp>.py` — the orchestrator/logic over the port; **no SQL**
  (BR1.3).
- `infrastructure/<resp>_adapter.py` — the **only** module with SQL (BR1.3),
  which **wraps the god-file SQL verbatim**, including the
  `if db_type in ["postgresql","postgres"]: ... else: (SQLite)` engine branch
  (BR1.2/FR1.4).
- The `DataManagerV2` method is **thinned to delegate** to the adapter/
  orchestrator, keeping its exact name and signature (facade, BR1.1).

The set-replacement atomic reference is `prizes/team_prizes_writer.py`
(`replace_team_prizes`); it is NOT applied to the god-file's own corruption
points in this intent (BR3.3, deferred OQ2) — those move verbatim.

New modules live under `backend/app/services/data_manager/<resp>/` (facade stays
`data_manager_v2.py`; it only loses method bodies, never gains methods — BR1.4).
Only new files are formatted (`ruff format` on new files only); the god-file is
touched surgically (NFR4). Identifiers/docstrings in English; commit text in
Spanish (NFR5).

## Responsibility inventory — the 57 methods partitioned (CLOSE AT PLAN APPROVAL)

Disjoint partition; the union covers all 57 methods (6 private shared helpers
`_init_database`, `_ensure_user`, `_get_or_create_user_id`,
`_ensure_championship_in_transaction`, `_ensure_schema_updates`,
`should_update_cache` land in the most-coupled modules extracted last).
`coupling_rank` 1 = lowest coupling (extract first).

| rank | module | methods (god-file names) |
|------|--------|--------------------------|
| 1 | `match-odds` | `save_match_odds`, `get_match_odds` |
| 2 | `news-articles` | `save_matchday_article`, `get_matchday_article`, `save_pressroom_news`, `get_matchday_data_for_news` |
| 3 | `performance` | `save_player_performance`, `save_player_performance_batch`, `get_player_performance_history` |
| 4 | `clauses` | `parse_clause_text`, `save_clauses`, `get_user_clauses_stats`, `get_clauses_raw`, `get_clausulable_player_stats` |
| 5 | `punishments-bonuses` | `save_punishments_bonuses`, `get_user_punishments_bonuses` |
| 6 | `dream-teams-mvp` | `save_dream_team_mvp`, `get_dream_team_bonus_stats` |
| 7 | `prizes` | `get_prizes_by_team` |
| 8 | `market-roster` | `save_market_players`, `save_team_roster`, `get_free_agent_candidates` |
| 9 | `transactions` | `save_player_transactions`, `save_pressroom_transactions`, `get_all_player_transactions`, `get_user_transactions`, `get_transactions_raw` |
| 10 | `teams-standings` | `save_team_standing`, `save_team`, `save_round_ranking`, `get_team_standings_history`, `get_latest_matchday`, `get_team_by_id`, `get_player_streak_data` |
| 11 | `players` | `save_player`, `save_players_batch`, `save_players`, `delete_orphan_players`, `get_all_players_with_points`, `get_player_by_id`, `save_player_championship_stats` |
| 12 | `users-stats-evolution` | `get_user_id_by_name`, `get_users_unique_players_stats`, `get_all_users_with_points`, `get_evolution_data_from_db`, `get_user_by_id`, `_ensure_user`, `_get_or_create_user_id` |
| 13 | `sync-metadata-cache` | `get_last_sync_metadata`, `update_sync_metadata`, `should_update_cache` |
| 14 | `schema-lifecycle` | `__init__`, `_init_database`, `reset_database`, `ensure_championship_exists`, `_ensure_championship_in_transaction`, `_ensure_schema_updates` |

Count check: 2+4+3+5+2+2+1+3+5+7+7+7+3+6 = **57** methods. `delete_orphan_players`
(the `DELETE ... NOT IN` corruption point) is in `players` (rank 11) and moves
**verbatim** (BR3.3, OQ2). The private helpers are concentrated in the
latest-extracted modules (`users-stats-evolution`, `schema-lifecycle`) because
every `save_*` touching a user/championship depends on them — hence highest
coupling, extracted last.

## Plan steps (execution order)

- [x] **Step 1 — Skeleton.** Create `backend/app/services/data_manager/`
  package (`__init__.py`) as the home for extracted responsibility sub-packages.
  No behavior change; no method moved yet.
- [x] **Step 2 — Runner readiness (test-after `runner_step`).** Verify the
  existing pytest runner from `backend/` resolves `from app...` and the fakes
  (`_FakeInMemoryDB`/`_FakeCursor`/`fake_db`) import. Record the exact
  unit-scoped command (see `unit-test-instructions.md`, R-01). No new runner or
  dependency is bootstrapped (brownfield; runner already exists).
- [x] **Step 3 — Baseline green.** Run the full `backend/tests/` suite once to
  confirm it is green and the coverage floor (`--cov-fail-under=27`) holds
  BEFORE any extraction (equivalence baseline, BR6.1).

Then, **per responsibility module in `coupling_rank` order (1→14)**, repeat the
characterization-first cycle (BR2.1/BR2.2, functional-design Workflow 1):

- [x] **Step 4 — `match-odds` (rank 1):** (a) characterize: write
  `tests/test_data_manager_match_odds_characterization.py` asserting the
  observable effect of `save_match_odds`/`get_match_odds` over `fake_db` (rows
  written / payload / `return None` on not-found) — never `assert True`
  (BR2.2/BR2.3); (b) green-pre against the unchanged god-file; (c) extract to
  `data_manager/match_odds/{domain/ports.py, application/match_odds.py,
  infrastructure/match_odds_adapter.py}` wrapping the SQL verbatim incl. the
  engine branch (BR1.2); thin the two god-file methods to delegate keeping
  name+signature (BR1.1); (d) green-post: SAME tests pass unchanged (BR3.1);
  (e) gate: full suite green + floor not lowered (BR6.1); (f) land isolated
  (own commit, C3).
- [x] **Step 5 — `news-articles` (rank 2):** same cycle; characterization test
  `tests/test_data_manager_news_articles_characterization.py`.
- [x] **Step 6 — `performance` (rank 3):** same cycle;
  `tests/test_data_manager_performance_characterization.py`.
- [x] **Step 7 — `clauses` (rank 4):** same cycle;
  `tests/test_data_manager_clauses_dm_characterization.py` (note: distinct from
  the existing `sync` clauses tests).
- [x] **Step 8 — `punishments-bonuses` (rank 5):** same cycle;
  `tests/test_data_manager_punishments_bonuses_characterization.py`.
- [x] **Step 9 — `dream-teams-mvp` (rank 6):** same cycle;
  `tests/test_data_manager_dream_teams_mvp_characterization.py`.
- [x] **Step 10 — `prizes` (rank 7):** same cycle;
  `tests/test_data_manager_prizes_read_characterization.py`.
- [x] **Step 11 — `market-roster` (rank 8):** same cycle;
  `tests/test_data_manager_market_roster_characterization.py`.
- [x] **Step 12 — `transactions` (rank 9):** same cycle;
  `tests/test_data_manager_transactions_characterization.py`.
- [x] **Step 13 — `teams-standings` (rank 10):** same cycle;
  `tests/test_data_manager_teams_standings_characterization.py`.
- [x] **Step 14 — `players` (rank 11):** same cycle; characterization MUST
  assert `delete_orphan_players`'s current `DELETE ... NOT IN` set-replacement
  effect and freeze it verbatim (BR3.3, OQ2 deferred);
  `tests/test_data_manager_players_characterization.py`.
- [x] **Step 15 — `users-stats-evolution` (rank 12):** same cycle; also move the
  `_ensure_user`/`_get_or_create_user_id` helpers it owns, preserving behavior;
  `tests/test_data_manager_users_stats_evolution_characterization.py`.
- [x] **Step 16 — `sync-metadata-cache` (rank 13):** same cycle;
  `tests/test_data_manager_sync_metadata_cache_characterization.py`.
- [x] **Step 17 — `schema-lifecycle` (rank 14):** same cycle; most-coupled
  (`__init__`/`_init_database`/`_ensure_schema_updates`); extract last;
  `tests/test_data_manager_schema_lifecycle_characterization.py`.
- [x] **Step 18 — Facade verification.** Confirm `DataManagerV2` still exposes
  all 57 names with identical signatures (BR1.1); the file now only delegates;
  no method added (BR1.4). Confirm the 8 consumer routers + the 4 DDD-wave
  adapters + `data_sync_service` + `data_initializer_v2` + `futmondo_service`
  import and invoke unchanged (BR4.1).
- [x] **Step 19 — Error-handling / corruption-point audit.** Grep-verify the 23
  broad/bare `except`, 16 `return None`, and the set-replacement DELETEs moved
  verbatim (no behavior change; BR3.2/BR3.3).
- [x] **Step 20 — Lint hygiene (surgical).** `ruff check` + `ruff format` on NEW
  files only; the god-file's registered `per-file-ignores` stay (NFR4). No mass
  reformat, no repo-wide `--fix`.
- [x] **Step 21 — Full-suite gate.** Run full `backend/tests/` green; confirm
  `--cov-fail-under` holds or ratchets up (BR6.1); no credential/token in tests
  (BR2.3/NFR6).
- [x] **Step 22 — Documentation & traceability.** English docstrings on new
  modules; write `code-summary.md`, `source-manifest.json`, `traceability.json`.

### Story-to-code-step traceability

| Plan step(s) | Requirement / rule |
|--------------|--------------------|
| 1, 20 | FR1.1 (DDD pattern), NFR4 (surgical format), BR1.4 (no god-file growth) |
| 4–17 (extract) | FR1.1/FR1.4 (facade→orchestrator→port→adapter; SQL verbatim), BR1.2/BR1.3 |
| 4–17 (characterize + green-pre/post) | FR2.1/FR2.2/FR2.3, BR2.1/BR2.2/BR2.3 (characterization-first, effect-asserting, fakes) |
| 4–17 (green-post), 18, 19 | FR3.1/FR3.2/FR3.3, BR3.1/BR3.2/BR3.3 (strict equivalence; legacy errors/corruption verbatim) |
| 18 | FR1.2 (surface byte-for-byte), FR4.1/FR4.2, BR1.1/BR4.1 (consumers + SQL-in-router untouched) |
| inventory table, this plan | FR5.1, BR5.1 (inventory + order closed at Plan Approval) |
| 3, 5–17 (gate), 21 | NFR1/NFR2, BR6.1 (suite green; coverage ratchet only) |
| 4–17 (tests) | NFR6, BR2.3 (no real credentials/network/DB) |

## Test files (MANDATORY — characterization suite)

One characterization test module per responsibility (14 files under
`backend/tests/`, named above). Each asserts the **observable effect** of its
methods over the in-memory fakes — payload shape, rows written, `return None`
on not-found, and the legacy failure mode where present — and is written to
pass **unchanged** before and after extraction. Volume follows the Minimal
strategy: at least one happy-path per method plus the not-found/failure edge
each method actually exhibits (≈5–10 asserts per module). No `vitest.config`/
`jest.config` applies (backend Python); the runner config is the existing
`backend/pytest.ini` (no change needed beyond the ratchet, which only rises).

## Deviations from the profile

- `plan_profile` lists API/endpoint and Frontend layers; both are **inapplicable**
  (routers untouched by BR4.1; no frontend in scope) and omitted — methodology
  unchanged.
- test-after is specialized to **characterization-first** per the affirmed team
  ALWAYS mandate for brownfield decomposition; this is a narrower explicit order
  that the resolver's `applicable_notes` already carry, not a methodology change.
