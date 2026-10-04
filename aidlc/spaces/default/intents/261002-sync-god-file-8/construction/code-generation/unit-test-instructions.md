# Unit Test Instructions — Sync Domain Decomposition

Scope `refactor`, strategy **minimal**, methodology **test-after** with the team
**characterization-first** mandate (freeze observable behaviour BEFORE extracting
each domain). Brownfield: the pytest runner already exists; no new dependency is
introduced.

## Test framework setup and configuration

- Runner: **pytest** + **pytest-cov**, run from `backend/`.
- Fixtures: the existing in-memory fakes in `backend/tests/conftest.py`
  (`_FakeInMemoryDB` / `_FakeCursor` on SQLite `:memory:`, `clean_jwt_env`,
  `fake_db`). **No network, no real DB, no real credentials** (gitleaks scans
  tests too) — NFR9/BR7.3.
- Futmondo client is injected into every orchestrator, so tests pass a **fake
  client** (no network).
- Config files (`pytest.ini`, `backend/ruff.toml`) are NOT modified. The
  coverage floor `--cov-fail-under=27` stays as-is (ratchet only rises) — NFR3.
- New test files are formatted surgically only (no mass `ruff format`) — BR7.2.

## Runner readiness (before the first test step)

Verify the runner is green before writing new characterization tests:

```bash
cd backend && python -m pytest -q
```

(For local repro when system Python > CI's 3.12, use an ephemeral venv excluding
`libsql-experimental` and set an ephemeral `JWT_SECRET`, per the project
correction learned 2026-09-16.)

## How to run THIS stage's tests (exact, per-domain scoped commands)

Each domain's characterization tests live under
`backend/tests/services/sync/`. Run **only** the file(s) for the domain being
worked, e.g.:

```bash
cd backend && python -m pytest tests/services/sync/test_transactions_sync.py -q
cd backend && python -m pytest tests/services/sync/test_punishments_bonuses_sync.py -q
cd backend && python -m pytest tests/services/sync/test_dream_teams_mvps_sync.py -q
cd backend && python -m pytest tests/services/sync/test_rosters_sync.py -q
cd backend && python -m pytest tests/services/sync/test_round_rankings_sync.py -q
cd backend && python -m pytest tests/services/sync/test_player_performance_sync.py -q
cd backend && python -m pytest tests/services/sync/test_players_full_sync.py -q
cd backend && python -m pytest tests/services/sync/test_prizes_sync.py -q
```

(Exact file names may be adjusted to match the existing test tree layout for the
pilots; keep each command scoped to the single domain under work. A bare
project-wide `pytest` is NOT the per-domain command — the full suite runs only
in the final verification step.)

Final verification (whole backend suite + coverage floor), run once at the end:

```bash
cd backend && python -m pytest -q --cov=app --cov-fail-under=27
```

## Expected coverage targets

- Minimal strategy: ~1 verifiable test per requirement at the narrowest level,
  plus a happy-path floor per new component (orchestrator, adapter, pure
  helper). Target per domain: payload equivalence + ingestion behaviour + error
  path, roughly 3–6 asserting tests.
- Global: the existing suite stays green and total line coverage stays **≥ 27**
  (never relaxed).

## Mocking / stubbing guidance

- Inject a **fake FutmondoClient** exposing only the methods the domain
  orchestrator calls (e.g. `get_locker_news`, `get_match_list`, the
  domain-specific endpoints), returning canned pages/items.
- Inject a **stub data port** (the domain's `Protocol`) to assert the exact
  persistence calls and the kwargs forwarded to `update_sync_metadata` (BR1.3) —
  OR use `DataManager<Domain>Adapter` over `fake_db` where the raw SQL path must
  be exercised (favorites, ALTER).
- Assert the **effect**: `SyncResult` keys/values, operation order, pagination
  stop conditions, and — for transactions — the observable throttle cadence
  (`time.sleep(0.5)` per call and `time.sleep(5)` per batch of 20; patch/spy
  `time.sleep` to assert the call pattern without real waiting). Never
  `assert True`, never mirror specs (BR7.3).
- For transactions, also assert the idempotent `ALTER` path swallows via
  `except Exception: pass` (R-03) without changing observable behaviour.

## Test data management

- Build minimal in-memory fixtures per domain (championship id, a couple of
  pages/items) in the test module or via `conftest.py` helpers.
- No shared mutable fixtures across tests; each test arranges its own doubles.
- No real ids, tokens, or credentials anywhere in test data.
