# Build Instructions — Backend (futmondo-analytics)

Scope `refactor`, strategy **minimal**, brownfield. This intent is a
Python-backend-only structural refactor; the Angular frontend and the deploy
pipeline are untouched (Out of Scope). Build verification here is the backend
test suite — there is no separate compile/bundle step for the Python backend.

## Sources

- `construction/code-generation/code-generation-plan.md`, `code-summary.md`,
  `unit-test-instructions.md`
- Project: `backend/requirements.txt`, `backend/pytest.ini`, `backend/ruff.toml`,
  `backend/tests/conftest.py`

## Dependency installation

```bash
cd backend
python -m pip install -r requirements.txt
```

Coste-0 local-repro note (learned 2026-09-16): when the system Python is newer
than CI's 3.12, create an ephemeral venv EXCLUDING `libsql-experimental` (it does
not build outside 3.12 and the tests use the fake SQLite, never it):

```bash
python -m venv /tmp/ftm-venv && source /tmp/ftm-venv/bin/activate
grep -v '^libsql-experimental' backend/requirements.txt | pip install -r /dev/stdin
```

## Environment setup

- `JWT_SECRET` must be a non-default value at web-service startup (NFR1.1). For
  tests, an ephemeral non-productive value is sufficient:
  ```bash
  export JWT_SECRET=ci-ephemeral-secret-not-a-real-one
  ```
- No real `DATABASE_URL`, no network, no real Futmondo/Sofascore credentials are
  needed: the test suite uses the in-memory fakes in `backend/tests/conftest.py`
  (`_FakeInMemoryDB`/`_FakeCursor` on SQLite `:memory:`, `clean_jwt_env`,
  `fake_db`) and an injected fake `FutmondoClient`.

## Build commands

The Python backend is interpreted; "build" = install deps + import-check +
lint + run the test suite.

```bash
cd backend
ruff check --config ruff.toml app          # lint (advisory in this intent's gate scope)
JWT_SECRET=ci-ephemeral-secret-not-a-real-one python -m pytest -q --cov=app --cov-fail-under=27
```

## Build verification steps

1. Dependencies install without error.
2. `ruff check` passes on the new `sync/<domain>/` packages (surgical formatting
   only; no mass `ruff format` of brownfield files — BR7.2/NFR7).
3. The backend test suite passes and total line coverage stays ≥ 27 (NFR3).
4. `git diff --stat backend/app/services/data_manager_v2.py` is EMPTY (the
   god-file was not grown/modified — NFR2).

## Troubleshooting

- **`libsql-experimental` build failure on Python > 3.12**: exclude it from the
  venv (see above); tests never exercise it.
- **`JWT_SECRET` startup error**: export a non-default ephemeral value.
- **Coverage below 27**: do NOT lower the floor (NFR3). Investigate the dropped
  lines; the floor only rises by ratchet.
