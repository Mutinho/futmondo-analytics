# Security Test Instructions — Minimal (no new security test files; checks recorded)

## Applicability

The active **Test Strategy is Minimal** and the scope is `refactor`. Per the
Build and Test stage, dedicated security test instruction files are generated at
Comprehensive strategy when security NFRs exist. This intent introduces **no new
attack surface, no new endpoint, no new authentication/authorization path, and no
new dependency** — it relocates existing code with strict functional equivalence.
So no new security test suite is generated here.

The security engineer did, however, verify the relevant NFR5/BR7.1 guarantee as
part of this stage, because the refactor moves error/log paths into the extracted
adapters and orchestrators.

## Security checks performed (this stage)

- **No credentials in errors/logs (NFR5, BR7.1)** — verified that the extracted
  orchestrators' failure paths log only `str(e)` / `error_message` and preserve
  the existing `_log_integration_failure` behaviour; no password or
  Futmondo/Sofascore token reaches any exception message, `repr`, `exc_info`, or
  log. STRIDE: Information Disclosure mitigation preserved, not weakened.
- **Secret scanning posture** — tests use in-memory fakes with no real tokens or
  ids (gitleaks scans `*.py` tests too); no secret is introduced into source or
  tests.
- **No new dependency (supply chain)** — `requirements.txt` unchanged; no new
  OSS/transitive package to audit (NFR6). STRIDE: no new Vulnerable-Components
  surface.
- **`JWT_SECRET` non-default at startup (NFR1.1)** — unchanged by this refactor;
  the web-service startup guard remains intact.
- **Lint/bare-except** — confirmed no bare `except:` was introduced (the
  `except Exception: pass` of the idempotent ALTER is preserved verbatim, not
  narrowed), so no new silent-swallow of unexpected errors (STRIDE: avoids a new
  Repudiation/Information-Disclosure gap).

## Coverage note

Dedicated SAST/DAST/injection testing is out of scope at this strategy and is
owned by the existing CI gate (gitleaks + pytest) and later CI-pipeline hardening
intents, not by this equivalence refactor.
