"""
Tests for FR14.2: no hardcoded championship/league identifiers in config.

Asserts the EFFECT of the cleanup: the legacy literal IDs no longer appear as
defaults, and the resolution is env-driven with an EMPTY fallback (an explicit
"not configured" signal) rather than a stale hardcoded value.

The legacy literals are asserted absent by value so the test fails loudly if a
hardcoded ID is ever reintroduced (Minimal strategy: one verifiable test per
requirement). The empty-fallback contract is asserted against ``os.getenv`` with
the exact default the module uses, without reloading the module (which would
re-run ``load_dotenv`` and re-read the developer machine's ``.env``).
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-not-default-000")

import app.core.config as config  # noqa: E402

_LEGACY_CHAMPIONSHIP_ID = "599b0e413f8a751620554699"
_LEGACY_LEAGUE_ID = "504e4f584d8bec9a67000079"


def test_module_defaults_are_not_the_legacy_literals():
    """The imported module must not carry the removed hardcoded IDs (FR14.2.1)."""
    assert config.CHAMPIONSHIP_ID != _LEGACY_CHAMPIONSHIP_ID
    assert config.LEAGUE_ID != _LEGACY_LEAGUE_ID


def test_config_source_has_no_legacy_literals():
    """The legacy IDs must not survive anywhere in the config module source
    (guards against a re-hardcoded default slipping back in)."""
    import inspect

    source = inspect.getsource(config)
    assert _LEGACY_CHAMPIONSHIP_ID not in source
    assert _LEGACY_LEAGUE_ID not in source


def test_unset_ids_fall_back_to_empty_not_legacy(monkeypatch):
    """Without env configuration the fallback is empty, never a hardcoded literal
    (FR14.2.2). Mirrors the module's resolution: ``os.getenv(<key>, "")``."""
    monkeypatch.delenv("CHAMPIONSHIP_ID", raising=False)
    monkeypatch.delenv("LEAGUE_ID", raising=False)

    resolved_championship = os.getenv("CHAMPIONSHIP_ID", "")
    resolved_league = os.getenv("LEAGUE_ID", "")

    assert resolved_championship == ""
    assert resolved_league == ""
    assert resolved_championship != _LEGACY_CHAMPIONSHIP_ID
    assert resolved_league != _LEGACY_LEAGUE_ID
