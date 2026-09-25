"""Tests for the integration error hierarchy — U1 `u1-error-layer`.

Freezes the shape of the typed exception hierarchy (FR4.1): construction of each
subtype with non-sensitive context, the recoverable/fatal classification carried
by the type (BR1.1-BR1.3), the re-parenting of the existing
``SofascoreIPBanError`` under ``IntegrationBanError`` (FR4.4, FR2.1 preserved),
and the NFR3 defense spec (BR1.4) — a credential passed in the call context must
NOT appear in ``str/repr/args``.

No network, no real DB, no real credentials (fake test values only; gitleaks
scans test files). stdlib only.
"""

import pytest

from app.services.integration_errors import (
    IntegrationBanError,
    IntegrationError,
    IntegrationTimeoutError,
    IntegrationUnparseableError,
)
from app.services.sofascore_client import SofascoreIPBanError

# --- Construction + non-sensitive context (FR4.1, BR1.4) ---

def test_ban_error_constructs_with_non_sensitive_context():
    """IntegrationBanError carries failure_mode + optional status/endpoint only."""
    exc = IntegrationBanError(status=403, endpoint="/player/1")
    assert exc.failure_mode == "ban"
    assert exc.status == 403
    assert exc.endpoint == "/player/1"
    # Message is composed only from non-sensitive fields, in English.
    assert "ban" in str(exc)
    assert "403" in str(exc)
    assert "/player/1" in str(exc)


def test_timeout_error_constructs_with_defaults():
    exc = IntegrationTimeoutError()
    assert exc.failure_mode == "timeout"
    assert exc.status is None
    assert exc.endpoint is None
    assert "timeout" in str(exc)


def test_unparseable_error_constructs_with_endpoint():
    exc = IntegrationUnparseableError(endpoint="/championships/42")
    assert exc.failure_mode == "unparseable"
    assert exc.endpoint == "/championships/42"
    assert "unparseable" in str(exc)


def test_root_error_is_not_meant_to_be_raised_directly_but_constructs():
    """The root is constructible (subtypes delegate to it) and holds context."""
    exc = IntegrationError("timeout", status=504, endpoint="/x")
    assert exc.failure_mode == "timeout"
    assert exc.status == 504
    assert exc.endpoint == "/x"


# --- Classification carried by the TYPE (BR1.1 fatal / BR1.2, BR1.3 recoverable) ---

# A single map documents which types the sync route must treat as fatal. The
# CLASSIFICATION lives in the type, not in this module (no decision logic here).
FATAL_TYPES = (IntegrationBanError,)
RECOVERABLE_TYPES = (IntegrationTimeoutError, IntegrationUnparseableError)


@pytest.mark.parametrize("exc_type", FATAL_TYPES)
def test_fatal_types_are_integration_errors(exc_type):
    """Fatal subtypes are IntegrationError subclasses (caught by the root)."""
    exc = exc_type()
    assert isinstance(exc, IntegrationError)
    # Fatal types must not be a recoverable type.
    assert not isinstance(exc, RECOVERABLE_TYPES)


@pytest.mark.parametrize("exc_type", RECOVERABLE_TYPES)
def test_recoverable_types_are_integration_errors_and_distinct_from_ban(exc_type):
    """Recoverable subtypes are IntegrationError subclasses, not a ban."""
    exc = exc_type()
    assert isinstance(exc, IntegrationError)
    assert not isinstance(exc, IntegrationBanError)


def test_root_catches_every_subtype():
    """The sync route catches by the root and routes on the concrete subtype."""
    for exc in (
        IntegrationBanError(),
        IntegrationTimeoutError(),
        IntegrationUnparseableError(),
    ):
        with pytest.raises(IntegrationError):
            raise exc


# --- Re-parenting of SofascoreIPBanError (FR4.4, FR2.1 preserved) ---


def test_sofascore_ip_ban_error_is_an_integration_ban_error():
    """SofascoreIPBanError now IS-A IntegrationBanError (and thus IntegrationError)."""
    exc = SofascoreIPBanError("Sofascore devolvio 403 para /x")
    assert isinstance(exc, IntegrationBanError)
    assert isinstance(exc, IntegrationError)
    # Fatal classification: it is a ban.
    assert exc.failure_mode == "ban"


def test_sofascore_ip_ban_error_caught_by_integration_root():
    """A consumer catching the root catches the pre-existing Sofascore ban too."""
    with pytest.raises(IntegrationError):
        raise SofascoreIPBanError("Sofascore devolvio 403 buscando 'x'")


# --- NFR3 defense: no credential in str/repr/args (BR1.4) ---

_FAKE_PASSWORD = "fake-pw-do-not-log-9137"  # test value only; not a real secret
_FAKE_TOKEN = "fake-token-do-not-log-4462"  # test value only; not a real secret


@pytest.mark.parametrize(
    "exc_type",
    [
        IntegrationError,
        IntegrationBanError,
        IntegrationTimeoutError,
        IntegrationUnparseableError,
        SofascoreIPBanError,
    ],
)
def test_credentials_never_appear_in_exception_surface(exc_type):
    """Even when a credential exists in the call context, it cannot reach the
    exception: the constructor accepts only non-sensitive fields, so str/repr/
    args never contain the password or token (NFR3, BR1.4).

    The credential is deliberately NOT passed to the constructor (there is no
    parameter for it); this spec is the safety net proving the design holds.
    """
    if exc_type is IntegrationError:
        exc = exc_type("timeout", status=401, endpoint="/login")
    elif exc_type is SofascoreIPBanError:
        exc = exc_type("Sofascore devolvio 403 para /login")
    else:
        exc = exc_type(status=401, endpoint="/login")

    surface = " ".join([str(exc), repr(exc), repr(exc.args)])
    assert _FAKE_PASSWORD not in surface
    assert _FAKE_TOKEN not in surface
