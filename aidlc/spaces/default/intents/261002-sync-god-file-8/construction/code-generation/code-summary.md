# Code Summary — Sync Domain Decomposition (zero-unit, scope `refactor`)

Strict-equivalence structural refactor of
`backend/app/services/data_sync_service.py`: the 7 inline sync domains were
extracted to the pilot triad and `sync_prizes` was uniformised. The 10 sync
domains now live under `backend/app/services/sync/<domain>/`, and the facade is a
thin coordinator.

## Files created / modified

**Modified (facade — only shrinks):**
- `backend/app/services/data_sync_service.py` — all 10 public `sync_*` methods
  are now thin delegations; `sync_all()` unchanged (10 keys, fixed order, name↔key
  divergences intact); `_find_championship()` kept and injected as a callable to
  `dream_teams_mvps`/`rosters`; dead imports removed. Net −1444 lines
  (159 insertions / 1603 deletions).

**Created — 8 domain packages** under `backend/app/services/sync/<domain>/`, each
with `__init__.py`, `orchestrator.py`, `domain/__init__.py`, `domain/ports.py`
(`typing.Protocol`, consumer-owned, no SQL/framework), `infrastructure/__init__.py`,
`infrastructure/<domain>_adapter.py` (sole `DataManagerV2` touch point, default
`DataManagerV2(skip_init=True)`, kwargs-faithful):
- `transactions` (+ pure `domain/pricing.py` for `_find_price_at_date`, BR4.3)
- `punishments_bonuses`
- `dream_teams_mvps`
- `rosters`
- `round_rankings`
- `player_performance`
- `players_full`
- `prizes` (uniformised; reuses `prizes/calculator.py` + `team_prizes_writer.py`)

**Created — 8 characterization test files** under `backend/tests/`
(`test_sync_<domain>_characterization.py`), 70 new tests.

**Modified — 3 pre-existing tests** (`test_prizes_characterization`,
`test_sync_clauses_characterization`, `test_sync_match_odds_characterization`):
their `dss.time.sleep` monkeypatch was retargeted to the extracted orchestrator
modules, because the `time.sleep` seam moved with the extracted code (the facade
no longer imports `time`). Minimal change to keep them green; no assertion weakened.

Full list in `source-manifest.json` (61 writes).

## Key implementation decisions

- **Raw SQL wrapped verbatim in domain adapters** (BR4.1), never moved to
  `data_manager_v2.py`:
  - transactions: `ALTER TABLE` block with `except Exception:` + `pass` preserved
    EXACTLY (R-03 — not a bare `except:`), `_store_bids`, and
    `_enrich_market_values`. The single-connection lifecycle was preserved via an
    `enrich_market_values(resolve_market_value)` callback so the client
    fetch + throttle + pure pricing stay in the orchestrator while the SQL stays
    in the adapter.
  - `_save_favorites` (incl. the Postgres `execute_values` branch) landed in the
    `players_full` adapter — its true call site.
  - prizes: the `get_db()` config SELECT in the adapter; the UNCHANGED
    `replace_team_prizes` writer and `prizes/calculator.py` reused as-is (BR2.1,
    BR3.3).
- **`_find_championship` injected as a callable** into `dream_teams_mvps` and
  `rosters` (BR4.2); not duplicated, not extracted to a shared module.
- **Observable throttles preserved exactly** (R-01 absorbed): transactions
  `time.sleep(0.5)` per API call AND `time.sleep(5)` per batch of 20 in the
  enrich path; per-domain page sleeps (0.3/0.1/0.05/0.2); pagination limits
  (50/1000/38) and stop conditions.
- **prizes error contract preserved verbatim**: `IntegrationBanError` fatal;
  `Timeout`/`Unparseable`/`Request` escalate-at-write and PROPAGATE; generic
  safety net unchanged.

## Test coverage summary

- `cd backend && python -m pytest -q --cov=app` → **329 passed, 3 xfailed**
  (up from 259 baseline), **coverage 43.19%** (≥ 27 floor; floor NOT relaxed —
  NFR3).
- Per-domain scoped runs all green. Transactions test spies `time.sleep` and
  proves the cadence: exactly 25×0.5s + 1×5s for 25 distinct players, plus
  per-player caching.
- Tests use in-memory fakes + injected fake `FutmondoClient`; no network, no real
  DB, no real credentials (NFR9/BR7.3).

## Deviations from plan

- None material. The plan's per-layer slots for data-model/API/frontend were N/A
  (declared in the plan); the applicable layers (repository/adapter + business
  logic/orchestrator) were implemented and tested per domain.
- The three pilot/prizes test monkeypatch retargets (above) were a necessary
  consequence of the `time.sleep` seam moving with the extracted code — a
  surgical, equivalence-preserving edit, not a behaviour change.

## Reviewer carry-forward resolution (functional-design R-01..R-04)

- **R-01 (throttle set)** — absorbed: transactions characterization asserts the
  full observable cadence incl. 0.5/call and 5/batch-of-20.
- **R-02 (NFR3 → BR mapping)** — the coverage floor is enforced here as a real
  obligation (suite green at 43.19% ≥ 27, floor untouched). Noted for the record;
  the functional-design traceability mapping of NFR3→BR5.2 remains as the
  design-stage view.
- **R-03 (`except Exception:` form)** — preserved exactly; verified no bare
  `except:` in the new package.
- **R-04 (8 vs 7 domains)** — reconciled: 7 inline domains extracted + prizes
  uniformised + 2 pilots already extracted = 10 sync domains behind the 10 public
  methods.

## Hard-invariant verification

- `git diff` on `data_manager_v2.py`: EMPTY (never grown/modified — NFR2).
- `pytest.ini`, `backend/ruff.toml`, `requirements.txt`, `prizes/`: unchanged
  (no new deps; floor stays 27 — NFR6/NFR3).
- Public surface intact: 10 `sync_*` + `sync_all()`; `sync_all()` keys/order/
  divergences byte-for-byte (FR3.1/FR3.2/FR3.3) — verified.
- `ruff check` on all new files + facade + edited tests: all checks passed. New
  files formatted surgically only; no mass `ruff format` (BR7.2/NFR7).
- No credentials in any error/log path (NFR5/BR7.1).
