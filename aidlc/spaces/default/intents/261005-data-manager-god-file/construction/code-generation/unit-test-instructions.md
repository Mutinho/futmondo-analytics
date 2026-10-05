# Unit Test Instructions — `data_manager_v2` decomposition

Characterization-first safety net for the god-file decomposition. These tests
**freeze the current observable behavior** of `DataManagerV2` and must pass
**unchanged** before AND after each responsibility is extracted (BR2.2/BR3.1).
Minimal strategy: ≈1 happy-path per method plus the not-found/failure edge each
method actually exhibits (≈5–10 asserts per module, 14 modules).

## Framework setup & configuration

- Runner: existing `pytest` + `pytest-cov`, config `backend/pytest.ini`
  (`testpaths = tests`, `pythonpath = .`, `addopts = -ra --cov-fail-under=27`).
- **No new dependency or runner is introduced** (brownfield; runner exists).
  Any new tool would be OSS, pinned exactly — none is planned (NFR3).
- Fakes come from `backend/conftest.py`: `_FakeInMemoryDB` /`_FakeCursor`
  (shared in-memory SQLite `:memory:`, `db_type = "sqlite"`), the `fake_db`
  fixture (fresh per test), and `clean_jwt_env`. No network, no real DB, no real
  credentials/tokens (BR2.3/NFR6 — gitleaks scans tests too).

## R-01 — Exact command to run THIS unit's tests (runnable before the first test cycle)

Run from `backend/` (so `from app...` resolves and `conftest.py` loads).

- Verify runner readiness (collect-only, no execution):

  ```bash
  cd backend && python -m pytest tests/ --collect-only -q
  ```

- Run the characterization suite for this decomposition (exact file list — this
  is the unit-scoped command; it names only this unit's new test files, never a
  bare `pytest`/`backend/tests` sweep):

  ```bash
  cd backend && python -m pytest \
    tests/test_data_manager_match_odds_characterization.py \
    tests/test_data_manager_news_articles_characterization.py \
    tests/test_data_manager_performance_characterization.py \
    tests/test_data_manager_clauses_dm_characterization.py \
    tests/test_data_manager_punishments_bonuses_characterization.py \
    tests/test_data_manager_dream_teams_mvp_characterization.py \
    tests/test_data_manager_prizes_read_characterization.py \
    tests/test_data_manager_market_roster_characterization.py \
    tests/test_data_manager_transactions_characterization.py \
    tests/test_data_manager_teams_standings_characterization.py \
    tests/test_data_manager_players_characterization.py \
    tests/test_data_manager_users_stats_evolution_characterization.py \
    tests/test_data_manager_sync_metadata_cache_characterization.py \
    tests/test_data_manager_schema_lifecycle_characterization.py \
    -q
  ```

- Per-module (while extracting one responsibility), run only that file, e.g.:

  ```bash
  cd backend && python -m pytest tests/test_data_manager_match_odds_characterization.py -q
  ```

The green-pre run (unchanged god-file) and green-post run (after extraction) use
the **same** per-module command with the **same** assertions.

## Expected coverage targets

- The blocking floor `--cov-fail-under=27` (line-only) must **hold or rise**;
  it is never lowered to pass the gate (BR6.1/NFR2). New characterization tests
  only ratchet it up. Run the full-suite coverage check with the project's
  configured invocation (`--cov=app`) only at the Step 3 baseline and Step 21
  final gate; Build and Test owns the authoritative floor verification.

## Mocking / stubbing guidance

- Inject the fake, do not monkeypatch: construct the extracted service with its
  port stub (the `analytics` pattern — `AnalyticsService(data=stub_port)`), or
  drive the adapter directly with `fake_db`. For the facade, instantiate
  `DataManagerV2(skip_init=True)` and seed the fake's schema via the module's
  own `save_*`/`_init_database` path so the read methods observe real rows.
- Assert the **effect**: returned rows/payload, rows written to the fake, the
  exact `return None` on not-found, and the legacy failure mode where a method
  swallows an exception. Never `assert True`, never a mirror spec that captures
  without asserting (BR2.2).
- The engine branch: tests run on the SQLite fake (`db_type = "sqlite"`), so
  they exercise the `else` branch; the PostgreSQL branch is moved verbatim and
  covered by equivalence of the wrapped SQL (BR1.2) — do not fabricate a real
  Postgres connection.

## Test data management

- Build fixtures in-test from literals (championship/team/player ids as fake
  strings); never copy real Futmondo data, credentials, or tokens into tests.
- `fake_db` is fresh per test (no shared mutable state); seed exactly the rows a
  given assertion needs.
