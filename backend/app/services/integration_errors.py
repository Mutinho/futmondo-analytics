"""Integration error hierarchy — U1 `u1-error-layer` (FR4.1, NFR3).

A leaf, dependency-free types module: it declares the common root
``IntegrationError`` and one subtype per failure mode. The *type* encodes the
recoverable/fatal classification; whoever catches it (the sync route, in U2)
decides the action. There is no decision logic here (classification lives at the
capture point, which has the step context — see domain-design "Alternatives
Rejected").

Security by construction (BR1.4 / NFR3): the constructor accepts ONLY
non-sensitive fields (``failure_mode`` and optional ``status`` / ``endpoint``).
It never receives the request object, a password, or a token, so a credential
cannot reach ``str(exc)``, ``repr(exc)`` or ``exc.args`` — leakage is impossible
by construction, not by after-the-fact redaction that could fail on a new token
format.

Messages are in English (developer diagnostics), per the team Code Style rule;
user-facing text (``HTTPException.detail``) stays in Spanish and is produced at
the HTTP boundary, not here.

Classification map (see functional-design rules.md):
- ``IntegrationBanError``          — fatal       (BR1.1)
- ``IntegrationTimeoutError``      — recoverable (BR1.2)
- ``IntegrationUnparseableError``  — recoverable (BR1.3)
- ``IntegrationRequestError``      — recoverable by default (U2, BR2.1); the
  capture point may escalate it to fatal at a write point (BR2.3 / EC-CTX).
"""

from typing import Optional


class IntegrationError(Exception):
    """Common root of external-integration failures (FR4.1, BR1.4).

    Consumers (the sync route) catch this root and route on the concrete
    subtype. It is not raised directly; its subtypes are. The message is composed
    ONLY from non-sensitive fields, so no credential can appear in ``str(exc)``,
    ``repr(exc)`` or ``exc.args`` (NFR3).

    Args:
        failure_mode: Non-sensitive failure-mode tag (e.g. ``"ban"``,
            ``"timeout"``, ``"unparseable"``). Base of the recoverable/fatal
            classification (the concrete subtype fixes it).
        status: Optional HTTP status code when applicable (e.g. ``403``). Never
            credential material.
        endpoint: Optional non-sensitive endpoint/path. NEVER a token or
            password (NFR3, BR1.4).
    """

    def __init__(
        self,
        failure_mode: str,
        *,
        status: Optional[int] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        # Only non-sensitive fields are stored; a credential is never a
        # parameter of this constructor, so it cannot be captured here.
        self.failure_mode = failure_mode
        self.status = status
        self.endpoint = endpoint
        super().__init__(
            f"integration {failure_mode} failure (status={status}, endpoint={endpoint})"
        )


class IntegrationBanError(IntegrationError):
    """Integration ban (e.g. Sofascore HTTP 403). Classification: FATAL (BR1.1).

    A ban is propagated, never swallowed: the sync route aborts cleanly without
    writing partial data. ``failure_mode`` defaults to ``"ban"``.
    """

    def __init__(
        self,
        failure_mode: str = "ban",
        *,
        status: Optional[int] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        super().__init__(failure_mode, status=status, endpoint=endpoint)


class IntegrationTimeoutError(IntegrationError):
    """One-off integration timeout. Classification: RECOVERABLE (BR1.2).

    The consumer degrades the step (``DEGRADED``) and continues; it does not
    abort the whole sync. ``failure_mode`` defaults to ``"timeout"``.
    """

    def __init__(
        self,
        failure_mode: str = "timeout",
        *,
        status: Optional[int] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        super().__init__(failure_mode, status=status, endpoint=endpoint)


class IntegrationUnparseableError(IntegrationError):
    """Heterogeneous / unparseable response. Classification: RECOVERABLE (BR1.3).

    Invalid JSON or an unexpected shape is a recoverable failure: the consumer
    degrades the step instead of masking it with a silent ``None``.
    ``failure_mode`` defaults to ``"unparseable"``.
    """

    def __init__(
        self,
        failure_mode: str = "unparseable",
        *,
        status: Optional[int] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        super().__init__(failure_mode, status=status, endpoint=endpoint)


class IntegrationRequestError(IntegrationError):
    """Connection/request failure not classifiable as timeout, ban or
    unparseable response — the ``requests.RequestException`` that
    ``FutmondoClient._make_request`` used to swallow as ``None`` (U2, FR4.2).

    Classification: RECOVERABLE BY DEFAULT (BR2.1). Like the other recoverable
    subtypes, the *type* only encodes the default; the sync capture point can
    escalate it to FATAL when it reaches a write point that could corrupt data
    (BR2.3 / EC-CTX). ``failure_mode`` defaults to ``"request_exception"``.

    Same construction contract as the rest of the hierarchy: only non-sensitive
    fields (``failure_mode`` / ``status`` / ``endpoint``); never a credential
    (NFR3, BR4.2).
    """

    def __init__(
        self,
        failure_mode: str = "request_exception",
        *,
        status: Optional[int] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        super().__init__(failure_mode, status=status, endpoint=endpoint)
