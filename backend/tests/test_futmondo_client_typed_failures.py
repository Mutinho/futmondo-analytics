"""Effect specs — ``FutmondoClient._make_request`` typed failures (u2-integrations).

Q1 floor: a failure spec asserts the EFFECT, never a bare ``pytest.raises``. Here
the effect is "the correct typed subtype is raised per failure mode AND no
credential appears in its surface" (FR4.2, BR1.1, NFR3/BR4.2).

No network, no real DB, no real credentials: ``self.session.post`` is
monkeypatched with in-memory fakes; auth state is injected with obviously-fake
values (gitleaks scans test files).
"""

import json

import pytest
import requests

from app.services.futmondo_client import FutmondoClient
from app.services.integration_errors import (
    IntegrationError,
    IntegrationRequestError,
    IntegrationTimeoutError,
    IntegrationUnparseableError,
)

# Fake credentials — test values only, never real secrets (gitleaks scans tests).
_FAKE_EMAIL = "fake-user@example.test"
_FAKE_PASSWORD = "fake-pw-do-not-log-7781"  # noqa: S105 - test double
_FAKE_TOKEN = "fake-token-do-not-log-3390"  # noqa: S105 - test double
_ENDPOINT = "/1/userteam/rounds"


def _authenticated_client():
    client = FutmondoClient(email=_FAKE_EMAIL, password=_FAKE_PASSWORD)
    client.token = _FAKE_TOKEN
    client.user_id = "fake-user-id"
    return client


def _assert_no_credentials(exc):
    """The exception surface must never contain the password or token (NFR3)."""
    surface = " ".join([str(exc), repr(exc), repr(exc.args)])
    assert _FAKE_PASSWORD not in surface
    assert _FAKE_TOKEN not in surface


def test_timeout_raises_integration_timeout_error_with_endpoint():
    client = _authenticated_client()

    def _raise_timeout(*a, **k):
        raise requests.exceptions.Timeout("read timed out")

    client.session.post = _raise_timeout

    with pytest.raises(IntegrationTimeoutError) as excinfo:
        client._make_request(_ENDPOINT, {"query": {}})

    exc = excinfo.value
    # EFFECT: correct subtype + non-sensitive context, recoverable classification.
    assert isinstance(exc, IntegrationError)
    assert exc.failure_mode == "timeout"
    assert exc.endpoint == _ENDPOINT
    _assert_no_credentials(exc)


def test_connection_error_raises_integration_request_error_with_endpoint():
    client = _authenticated_client()

    def _raise_conn(*a, **k):
        raise requests.exceptions.ConnectionError("connection refused")

    client.session.post = _raise_conn

    with pytest.raises(IntegrationRequestError) as excinfo:
        client._make_request(_ENDPOINT, {"query": {}})

    exc = excinfo.value
    assert isinstance(exc, IntegrationError)
    assert exc.failure_mode == "request_exception"
    assert exc.endpoint == _ENDPOINT
    # A RequestException is NOT a timeout subtype.
    assert not isinstance(exc, IntegrationTimeoutError)
    _assert_no_credentials(exc)


def test_unparseable_response_raises_integration_unparseable_error():
    client = _authenticated_client()

    class _BadJsonResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            raise json.JSONDecodeError("Expecting value", "", 0)

    client.session.post = lambda *a, **k: _BadJsonResponse()

    with pytest.raises(IntegrationUnparseableError) as excinfo:
        client._make_request(_ENDPOINT, {"query": {}})

    exc = excinfo.value
    assert isinstance(exc, IntegrationError)
    assert exc.failure_mode == "unparseable"
    assert exc.endpoint == _ENDPOINT
    _assert_no_credentials(exc)


def test_typed_failure_never_returns_silent_none():
    """No failure mode is masked as None any more (FR4.2): all raise."""
    client = _authenticated_client()

    def _raise_timeout(*a, **k):
        raise requests.exceptions.Timeout("t")

    client.session.post = _raise_timeout
    with pytest.raises(IntegrationError):
        result = client._make_request(_ENDPOINT, {"query": {}})
        # Must not reach here with a None; the raise is the contract.
        assert result is not None
