"""Facade tests for the decomposed assistant service (BR6.1).

Unlike the per-seam characterization tests, these drive the ``AssistantService``
facade through its NEW constructor port injection (``read=`` / ``usage=`` /
``llm=``, the OCP pattern of ``analytics/facade.py``) — no DB, no network, no
monkeypatching. They pin the public surface and the observable ``ask()`` order.

Covered:
- Public surface identity: the historical import path still exposes
  ``get_assistant_service`` / ``AssistantService`` / ``AssistantUsageTracker``,
  and the singleton is stable.
- ``ask()`` end-to-end: happy factual, happy generative, blocked (guardrail),
  LLM degradation, context degradation — with stub ports.
- Reviewer note R-02: a factual answer does NOT invoke the usage port
  (``can_make_request`` / ``record_usage``), freezing the observed short-circuit
  order (factual precedes the quota check).
"""

import asyncio

from app.services.assistant_service import (
    AssistantService,
    AssistantUsageTracker,
    get_assistant_service,
)

# --- Stub ports (implemented in-test per the unit-test instructions) ---------


class _StubUsage:
    """Records whether the quota port was touched (R-02)."""

    def __init__(self, allowed=True, reason=""):
        self._allowed = allowed
        self._reason = reason
        self.can_make_request_calls = 0
        self.record_usage_calls = []

    def can_make_request(self):
        self.can_make_request_calls += 1
        return self._allowed, self._reason

    def record_usage(self, input_tokens, output_tokens):
        self.record_usage_calls.append((input_tokens, output_tokens))

    def get_usage_summary(self):
        return {"tokens_used": 0}


class _StubRead:
    """Minimal read port returning canned identity + context data."""

    def __init__(self, team_value=(16_000_000, 2)):
        self._team_value = team_value

    def get_user_identity(self, user_id, championship_id):
        return {
            "user_name": "Ana",
            "team_name": "Los Cracks",
            "team_id": "T1",
            "championship_name": "Liga Test",
            "is_pro": False,
        }

    def get_team_value(self, championship_id, team_id):
        return self._team_value

    # Context reads used by the generative path (roster + budget always attempted).
    def get_roster_rows_ctx(self, championship_id, team_id):
        return [("p1", "Vinicius", "DEL", 30_000_000, 8.0, 8.5, 7.5, 10)]

    def get_budget_data(self, user_id, championship_id, team_id):
        return {
            "total_spent": 50_000_000,
            "total_income": 10_000_000,
            "initial_budget": 200_000_000,
            "prizes": 0,
            "team_value": 30_000_000,
        }

    # Unused reads for these flows (kept for protocol completeness).
    def get_balance_data(self, *a, **k):
        return {}

    def get_roster_rows(self, *a, **k):
        return []

    def get_standings(self, *a, **k):
        return None, []

    def get_free_agents(self, *a, **k):
        return []

    def get_clausulables(self, *a, **k):
        return []

    def get_transactions(self, *a, **k):
        return []

    def get_next_matches(self, *a, **k):
        return None, [], []

    def get_is_pro(self, *a, **k):
        return False

    def get_market_today(self, *a, **k):
        return []

    def save_market_today(self, *a, **k):
        return None


class _StubReadCtxDegraded(_StubRead):
    """Roster read fails, budget succeeds → partial context (BR3.3 degradation at facade)."""

    def get_roster_rows_ctx(self, championship_id, team_id):
        return []  # roster omitted; budget section still present


class _StubLLM:
    """LLM port double: returns a canned completion, or None to force degradation."""

    def __init__(self, result=("respuesta generativa", 12, 8)):
        self._result = result
        self.calls = 0

    def complete(self, system, history, message):
        self.calls += 1
        return self._result


# --- Public surface identity -------------------------------------------------


def test_public_surface_and_singleton_stable():
    """The historical import path exposes the surface and a stable singleton."""
    assert callable(get_assistant_service)
    assert AssistantUsageTracker is not None
    first = get_assistant_service()
    second = get_assistant_service()
    assert isinstance(first, AssistantService)
    assert first is second  # singleton identity preserved


# --- ask() end-to-end flows --------------------------------------------------


def test_ask_blocked_by_guardrail():
    """A long off-topic message returns the guardrail response, no ports touched (BR6.1)."""
    usage = _StubUsage()
    service = AssistantService(read=_StubRead(), usage=usage, llm=_StubLLM())
    long_offtopic = (
        "Cuéntame por favor la receta completa con todos los ingredientes para "
        "cocinar una paella valenciana para ocho personas este domingo"
    )
    result = asyncio.run(service.ask("U1", "C1", long_offtopic, history=[]))
    assert "🚫" in result["response"]
    assert result["context_used"] == ["guardrail"]
    assert usage.can_make_request_calls == 0  # never reached the quota check


def test_ask_factual_does_not_touch_quota(monkeypatch):
    """A factual answer short-circuits BEFORE the quota check (R-02, BR6.1)."""
    usage = _StubUsage()
    llm = _StubLLM()
    service = AssistantService(read=_StubRead(team_value=(16_000_000, 2)), usage=usage, llm=llm)

    result = asyncio.run(service.ask("U1", "C1", "¿cuánto vale mi plantilla?", history=[]))

    assert result["context_used"] == ["direct_db"]
    assert "16.0M€" in result["response"]
    # R-02: neither the quota check nor usage recording nor the LLM was invoked.
    assert usage.can_make_request_calls == 0
    assert usage.record_usage_calls == []
    assert llm.calls == 0


def test_ask_generative_happy_path_records_usage():
    """A generative question checks quota, calls the LLM, records usage (BR6.1)."""
    usage = _StubUsage(allowed=True)
    llm = _StubLLM(result=("respuesta generativa", 12, 8))
    service = AssistantService(read=_StubRead(), usage=usage, llm=llm)

    result = asyncio.run(service.ask("U1", "C1", "dame tu opinion general", history=[]))

    assert result["response"] == "respuesta generativa"
    assert "roster" in result["context_used"]
    assert "budget" in result["context_used"]
    assert usage.can_make_request_calls == 1
    assert usage.record_usage_calls == [(12, 8)]
    assert llm.calls == 1


def test_ask_generative_llm_degradation():
    """When the LLM port returns None, ask() degrades to the saturation message (BR5.3)."""
    usage = _StubUsage(allowed=True)

    class _ExhaustedLLM:
        def complete(self, system, history, message):
            return None

    service = AssistantService(read=_StubRead(), usage=usage, llm=_ExhaustedLLM())

    result = asyncio.run(service.ask("U1", "C1", "dame tu opinion general", history=[]))

    assert "saturados" in result["response"]
    assert result["context_used"] == []
    assert usage.record_usage_calls == []  # nothing recorded on degradation


def test_ask_generative_quota_exhausted():
    """When quota is exhausted the LLM is never called (BR4.1, BR6.1)."""
    usage = _StubUsage(
        allowed=False, reason="Has alcanzado el límite mensual gratuito del asistente."
    )
    llm = _StubLLM()
    service = AssistantService(read=_StubRead(), usage=usage, llm=llm)

    result = asyncio.run(service.ask("U1", "C1", "dame tu opinion general", history=[]))

    assert "límite mensual" in result["response"]
    assert result["context_used"] == []
    assert llm.calls == 0


def test_ask_generative_context_degradation_partial():
    """A failing roster read still yields a budget-only context, no crash (BR3.3)."""
    usage = _StubUsage(allowed=True)
    llm = _StubLLM(result=("respuesta", 1, 1))
    service = AssistantService(read=_StubReadCtxDegraded(), usage=usage, llm=llm)

    result = asyncio.run(service.ask("U1", "C1", "dame tu opinion general", history=[]))

    assert result["response"] == "respuesta"
    # Roster omitted (degraded), budget still present — partial context.
    assert "roster" not in result["context_used"]
    assert "budget" in result["context_used"]
