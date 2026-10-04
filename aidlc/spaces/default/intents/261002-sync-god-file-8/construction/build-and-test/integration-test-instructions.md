# Integration Test Instructions — Not Applicable (minimal strategy)

## Applicability

The active **Test Strategy is Minimal** and the scope is `refactor`. Per the
Build and Test stage (Steps 3–7), the Minimal strategy generates **no additional
integration test instruction files** — unit/characterization tests are covered
per domain by Code Generation.

This is a **strict functional-equivalence refactor**: no new cross-component
behaviour, no new integration surface, and no new external dependency is
introduced. The existing integration surface (`sync_all()` consumed by the
router worker `_run_sync_in_background`) is preserved byte-for-byte (BR3.1/BR3.2)
and is already exercised by the existing suite, which stays green.

## Coverage note

Cross-domain equivalence is verified at the **unit/characterization level** per
domain (each `SyncResult` payload, ingestion behaviour, and `update_sync_metadata`
kwargs frozen with in-memory fakes, no network/DB) and by the full backend suite
remaining green (329 passed). The `sync_all()` key set/order and the three
name↔key divergences are verified directly against the facade. No separate
integration run is warranted at this strategy/scope.
