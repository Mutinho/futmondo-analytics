# Performance Test Instructions — Not Applicable (minimal strategy, no perf NFR)

## Applicability

The active **Test Strategy is Minimal** and there is **no performance NFR** in
`requirements.md` for this intent. Per the Build and Test stage, performance test
instructions are generated only at Comprehensive strategy when performance NFRs
exist. Neither condition holds.

This is a **strict functional-equivalence refactor** (NFR1): observable timing
behaviour — the per-domain `time.sleep` throttles (transactions `0.5` per call
and `5` per batch of 20; page sleeps `0.3`/`0.1`/`0.05`/`0.2`) and pagination
limits (50/1000) — is preserved verbatim and asserted in the per-domain
characterization tests (transactions spies `time.sleep` to prove the cadence).

## Coverage note

No load/stress/soak testing applies: the refactor relocates code without
changing runtime cost characteristics, and the project runs on free-tier Fly.io
+ Neon (coste 0 €), where paid load-testing infrastructure is out of scope.
Observable throttle equivalence is the only performance-relevant property and it
is covered at the unit level.
