# Test Results — Build and Test (sync domain decomposition)

Executed on the backend test suite for the strict-equivalence refactor. All
commands were run from `backend/` with the in-memory fakes (no network, no real
DB, no real credentials).

## Build status

**Success.** Python backend is interpreted; "build" = dependency install +
lint + test suite.

- Dependencies: installed from `requirements.txt` (ephemeral venv excluding
  `libsql-experimental` per the coste-0 local-repro practice).
- Lint: `ruff check --config ruff.toml` on the 8 new `sync/<domain>/` packages
  → **All checks passed!** (surgical formatting only; no mass `ruff format`).

## Test results

Command: `JWT_SECRET=ci-ephemeral-secret-not-a-real-one python -m pytest -q --cov=app --cov-fail-under=27`

- **Total: 329 passed, 3 xfailed** (0 failed), 3 warnings, in ~5.9s.
- Baseline before this intent: 259 passed → **+70 new tests** (8 per-domain
  characterization files).
- The 3 `xfail` are pre-existing `test_futmondo_client_characterization.py`
  LEGACY markers for a DIFFERENT intent (FR4.2 typed-exception migration); they
  are expected-fail and not introduced or changed here.

## Coverage report

- **Total line coverage: 43.19%** — `Required test coverage of 27% reached.`
- Floor `--cov-fail-under=27` **not relaxed** (NFR3); it remains exactly 27.
- New domain modules are well covered at the orchestrator/port layer
  (orchestrators ~91–93%, ports 100%); adapters show lower line coverage (17–35%)
  because they are thin verbatim-SQL wrappers exercised indirectly — acceptable
  under the Minimal strategy and the strict-equivalence posture (the adapters
  delegate to `DataManagerV2`, which this refactor does not test anew).

## Failure details

None. No build or test command failed.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| COV-BACKEND-FLOOR | NFR3 / `pytest.ini` `--cov-fail-under` | line coverage ≥ 27, floor unchanged | 43.19%, floor = 27 | pytest run above | build-and-test | Met |
| SUITE-GREEN | NFR4 / team CI gate (`pytest`) | existing suite stays green | 329 passed, 0 failed | pytest run above | build-and-test | Met |
| EQUIVALENCE-PUBLIC-SURFACE | FR3.1/FR3.2/FR3.3 | 10 `sync_*` + `sync_all()` keys/order/divergences unchanged | verified identical | `grep` on `data_sync_service.py` (10 methods; 10 keys fixed order; 3 divergences) | build-and-test | Met |
| GODFILE-UNCHANGED | NFR2 | `data_manager_v2.py` not grown/modified | empty diff | `git diff --stat` empty | build-and-test | Met |
| NO-CREDENTIAL-LEAK | NFR5/BR7.1 | no credential in error/log | preserved `_log_integration_failure`; failure paths log `str(e)` only | code review (security engineer) | build-and-test | Met |
| NO-BARE-EXCEPT | FR5.3/BR5.3 | `except Exception: pass` preserved, no bare `except:` | no bare except introduced | `grep` + ruff (no E722) | build-and-test | Met |
| NO-NEW-DEPS | NFR6 | no new dependency, cost 0 € | `requirements.txt` unchanged | file diff | build-and-test | Met |
| THROTTLE-EQUIVALENCE | FR5.2 / Constraints | observable `time.sleep` cadence preserved (incl. transactions 0.5+5) | transactions test spies `time.sleep`: 25×0.5 + 1×5 | `test_sync_transactions_characterization.py` | build-and-test | Met |

No `Pending` verdicts remain. No applicable target is `Not Met` or `Unverified`.
