# Code Generation Plan — Sync Domain Decomposition (zero-unit, scope `refactor`)

Implements the Functional Design (`construction/functional-design/`) for intent
`261002-sync-god-file-8`: extract the 7 inline sync domains of
`backend/app/services/data_sync_service.py` into the proven pilot triad
(orchestrator + consumer-owned domain port + infrastructure adapter wrapping
`DataManagerV2` verbatim), uniformise `sync_prizes`, with **strict functional
equivalence** and **without growing** `data_manager_v2.py`.

Methodology (from the embedded Testing Contract): **test-after**, strategy
**minimal**, scope **refactor** (characterization-first per team mandate; no
extra new-test floor; existing suite stays green). Brownfield: pytest runner
already exists.

## Scope and invariants (from functional-design)

- Pilot mold is FIXED (`sync/clauses/`, `sync/match_odds/`): `orchestrator.py` +
  `domain/ports.py` (`typing.Protocol`, no SQL/framework) +
  `infrastructure/<domain>_adapter.py` (sole `DataManagerV2` touch point,
  default `DataManagerV2(skip_init=True)`, kwargs-faithful) — BR1.1–BR1.3.
- Public surface FROZEN: 10 `sync_*` methods + `sync_all()` with 10 keys, fixed
  order, name↔key divergences (`players`↔`sync_players_full`,
  `dream_teams`↔`sync_dream_teams_mvps`, `team_standings`↔`sync_round_rankings`)
  — BR3.1/BR3.2/BR3.3.
- Raw SQL on `self.dm.db` wrapped VERBATIM in the domain adapter, never moved to
  `data_manager_v2.py`, never rewritten — BR4.1.
- `_find_championship()` stays in the facade, injected as a callable to
  `dream_teams_mvps`/`rosters` — BR4.2. `_find_price_at_date` (pure) → in
  `sync/transactions/domain/pricing.py` — BR4.3.
- `sync_transactions` `except Exception: pass` (idempotent ALTER) preserved
  verbatim as registered debt; NOT narrowed to a bare `except:` — BR5.3.
- No credentials in any error/log — BR7.1. No new deps; English identifiers,
  Spanish commits — BR7.3. Coverage floor `--cov-fail-under=27` not relaxed —
  NFR3. New files formatted surgically only (no mass `ruff format`) — BR7.2/NFR7.

## Reviewer carry-forward (functional-design R-01..R-04 — absorb here)

- **R-01**: characterize transactions' FULL observable throttle — `time.sleep(0.5)`
  (per API call) AND `time.sleep(5)` (per batch of 20) in `_enrich_market_values`,
  not just the paginated 0.3/etc. (Step for transactions characterization.)
- **R-03**: preserve the exact `except Exception:` + `pass` form; never a bare
  `except:` (E722).
- **R-02/R-04**: documentation/traceability precisions — handled in code-summary.

## Delivery order (BR6.2, Q1)

`transactions` → `punishments_bonuses` → `dream_teams_mvps` → `rosters` →
`round_rankings` → `player_performance` → `players_full`, then `prizes`
(uniformise). Each domain = characterize → extract (port+adapter+orchestrator) →
thin facade method → suite green.

## Plan steps

- [x] **Step 1 — Project structure / production configuration skeleton.** No new
  production config needed (brownfield). Confirm the `sync/` package layout
  matches the pilots; each new domain gets `sync/<domain>/__init__.py`,
  `orchestrator.py`, `domain/__init__.py`, `domain/ports.py`,
  `infrastructure/__init__.py`, `infrastructure/<domain>_adapter.py`.
- [x] **Step 2 — Verify the existing test runner and record the exact unit-scoped
  command.** Runner is pytest from `backend/`. Record in
  `unit-test-instructions.md` the exact per-domain scoped commands (e.g.
  `pytest backend/tests/services/sync/test_transactions_sync.py -q`). Runner
  readiness precedes the first test step. (test-after: tests follow each layer.)

### Domain extraction loop (per BR6.2 order) — layers per Testing Contract

For EACH domain in order, apply the test-after per-layer profile. Data-model and
API layers are N/A for this refactor (no schema change, no new endpoints — the
frozen facade methods are the only API surface and they stay); the testable
layers that apply are **repository/data-access** (the adapter) and **business
logic** (the orchestrator + any pure domain helper). Frontend behavior: N/A
(backend-only).

- [x] **Step 3 — transactions: implement** the triad. `domain/ports.py`
  (Protocol: `get_last_sync_metadata`, `save_transactions`/store ops,
  `update_sync_metadata`, plus the market-value/favorites ops it consumes);
  `domain/pricing.py` (pure `_find_price_at_date`, BR4.3);
  `infrastructure/transactions_adapter.py` wrapping `DataManagerV2` AND the raw
  SQL verbatim (ALTER with `except Exception: pass`, `_enrich_market_values`
  UPDATE, `_store_bids`); `orchestrator.py` (ingestion, `time.sleep(0.3)` page +
  `0.5`/`5` enrich throttles, error path). Thin `DataSyncService.sync_transactions`
  to delegation. (FR1.1–FR1.3, FR4.1, FR5.3, BR4.3; R-01, R-03.)
- [x] **Step 4 — transactions: write and run its tests after implementation.**
  Characterization tests (fakes, no network/DB) asserting `SyncResult`
  payload/keys/values, pagination/stop conditions, operation order, AND the
  observable throttle cadence (0.5 per call, 5 per batch of 20 — R-01), and the
  idempotent-ALTER swallow (R-03). Suite green.
- [x] **Step 5 — punishments_bonuses: implement** triad + thin facade. (FR1.*)
- [x] **Step 6 — punishments_bonuses: write and run its tests.** Characterize
  `SyncResult` + ingestion; suite green.
- [x] **Step 7 — dream_teams_mvps: implement** triad + thin facade; inject
  `_find_championship` callable from facade (BR4.2).
- [x] **Step 8 — dream_teams_mvps: write and run its tests.** Characterize
  payload + the injected-`_find_championship` path; suite green.
- [x] **Step 9 — rosters: implement** triad + thin facade; inject
  `_find_championship`; wrap `_save_favorites` raw SQL (incl. Postgres
  `execute_values` branch) verbatim in the adapter (BR4.1, BR4.2).
- [x] **Step 10 — rosters: write and run its tests.** Characterize payload +
  favorites persistence (both SQLite and the Postgres branch where feasible with
  fakes); suite green.
- [x] **Step 11 — round_rankings: implement** triad + thin facade (key
  `team_standings` in `sync_all()`).
- [x] **Step 12 — round_rankings: write and run its tests.** Characterize
  payload + `team_standings` key mapping; suite green.
- [x] **Step 13 — player_performance: implement** triad + thin facade.
- [x] **Step 14 — player_performance: write and run its tests.** suite green.
- [x] **Step 15 — players_full: implement** triad + thin facade (key `players`
  in `sync_all()`).
- [x] **Step 16 — players_full: write and run its tests.** Characterize payload +
  `players` key mapping; suite green.
- [x] **Step 17 — prizes: uniformise** — move orchestration to
  `sync/prizes/orchestrator.py`, reuse `prizes/calculator.py` +
  `prizes/team_prizes_writer.replace_team_prizes` unchanged; wrap the `get_db()`
  raw SQL verbatim in a prizes adapter; thin `DataSyncService.sync_prizes`.
  (FR2.1/FR2.2, BR2.1, BR3.3, BR4.1.)
- [x] **Step 18 — prizes: write and run its tests.** Characterize the `sync_prizes`
  payload and the atomic set-replacement path (no change to calc/writer); suite
  green.
- [x] **Step 19 — `sync_all()` equivalence check.** Confirm/characterize that
  `sync_all()` still returns the 10 keys in fixed order with the name↔key
  divergences intact (BR3.2). No code change expected beyond the thinned methods.

### Finalization

- [x] **Step 20 — Environment/build configuration.** None expected (no new deps,
  coverage floor unchanged at 27). Confirm `pytest.ini`/`ruff.toml` untouched
  except as surgical necessity; new files formatted surgically.
- [x] **Step 21 — Documentation and traceability.** `code-summary.md`
  (files, decisions, deviations, R-02/R-04 notes), `traceability.json`
  (FR/NFR/BR → implementation/test files), `source-manifest.json` (every
  created/modified source path). Full backend suite green; coverage ≥ 27.

## Step → requirement traceability

| Step(s) | Requirements / BR |
|---------|-------------------|
| 1–2 | FR1.1 (layout), BR5.1 (runner-ready for characterization) |
| 3–4 | FR1.1–1.3, FR4.1, FR5.1–5.3, BR4.3; R-01, R-03 |
| 5–6 | FR1.1–1.3, FR5.1–5.2 |
| 7–8 | FR1.1–1.3, FR4.2, FR5.1–5.2 |
| 9–10 | FR1.1–1.3, FR4.1, FR4.2, FR5.1–5.2 |
| 11–12 | FR1.1–1.3, FR3.2 (team_standings), FR5.1–5.2 |
| 13–14 | FR1.1–1.3, FR5.1–5.2 |
| 15–16 | FR1.1–1.3, FR3.2 (players), FR5.1–5.2 |
| 17–18 | FR2.1, FR2.2, BR2.1, BR3.3, FR4.1, FR5.1–5.2 |
| 19 | FR3.1, FR3.2, FR3.3 |
| 20 | NFR3, NFR6, NFR7 |
| 21 | NFR8, NFR9, traceability; R-02, R-04 |

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
