"""Characterization tests for the assistant LLM fallback + degradation.

These freeze the CURRENT observable behavior of the LLM provider path BEFORE it
moves behind ``LLMPort`` into ``assistant/infrastructure/``. They drive the real
``ask()`` with stubbed provider clients (no real LLM, no real keys) and a minimal
seeded DB for identity/context, exercising the seam end-to-end.

BR5.1 — Groq is tried BEFORE Gemini (provider order preserved).
BR5.3 — an LLM failure degrades WITHOUT crashing (a user-facing message is
         returned instead of raising).
BR5.4 — no credential/token material leaks into the degraded response.
"""

import asyncio

import app.services.assistant.facade as facade_mod
from app.services.assistant_service import AssistantService


def _service_on(fake_db, monkeypatch):
    monkeypatch.setattr(facade_mod, "get_db", lambda: fake_db)
    return AssistantService()


def _seed_minimal(fake_db):
    """Minimal schema so identity + roster/budget context reads succeed."""
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute("CREATE TABLE app_users (id TEXT, display_name TEXT)")
        cur.execute(
            "CREATE TABLE user_championships (user_id TEXT, championship_id TEXT, name TEXT, "
            "futmondo_team_id TEXT, is_pro INTEGER, initial_budget INTEGER)"
        )
        cur.execute("CREATE TABLE teams (team_id TEXT, team_name TEXT)")
        cur.execute(
            "CREATE TABLE player_championship_stats (championship_id TEXT, owner_team_id TEXT, "
            "owner_team_name TEXT, player_id TEXT, average_overall REAL, average_last_five REAL, clause_price INTEGER)"
        )
        cur.execute(
            "CREATE TABLE players (player_id TEXT, name TEXT, role TEXT, value INTEGER, real_team_id TEXT)"
        )
        cur.execute(
            "CREATE TABLE sofascore_cache (player_name TEXT, rating REAL, matches_started INTEGER)"
        )
        cur.execute(
            "CREATE TABLE transactions (championship_id TEXT, buyer_team_id TEXT, seller_team_id TEXT, "
            "player_id TEXT, price INTEGER, transaction_date TEXT)"
        )
        cur.execute(
            "CREATE TABLE team_prizes (championship_id TEXT, team_id TEXT, ranking_prize INTEGER, "
            "mvp_prize INTEGER, points_prize INTEGER, dream_team_prize INTEGER)"
        )
        cur.execute("INSERT INTO app_users (id, display_name) VALUES ('U1', 'Ana')")
        cur.execute(
            "INSERT INTO user_championships (user_id, championship_id, name, futmondo_team_id, is_pro, initial_budget) "
            "VALUES ('U1', 'C1', 'Liga Test', 'T1', 0, 200000000)"
        )
        cur.execute("INSERT INTO teams (team_id, team_name) VALUES ('T1', 'Los Cracks')")


# A non-factual, non-guardrail, short message that needs LLM reasoning.
_MSG = "dame tu opinion general"


class _GroqStub:
    """Minimal Groq-shaped client double recording that it was called first."""

    def __init__(self, calls, answer="respuesta groq"):
        self._calls = calls
        self._answer = answer

        class _Completions:
            def create(inner_self, **kwargs):
                self._calls.append("groq")
                usage = type("U", (), {"prompt_tokens": 10, "completion_tokens": 5})()
                msg = type("M", (), {"content": self._answer})()
                choice = type("C", (), {"message": msg})()
                return type("R", (), {"choices": [choice], "usage": usage})()

        class _Chat:
            completions = _Completions()

        self.chat = _Chat()


def test_groq_is_tried_before_gemini(fake_db, monkeypatch):
    """A generative question hits Groq first and returns its answer (BR5.1)."""
    _seed_minimal(fake_db)
    service = _service_on(fake_db, monkeypatch)
    calls = []
    service._groq_client = _GroqStub(calls)

    result = asyncio.run(service.ask("U1", "C1", _MSG, history=[]))

    assert result["response"] == "respuesta groq"
    assert calls == ["groq"]  # Groq called, Gemini never reached


def test_llm_failure_degrades_without_crashing(fake_db, monkeypatch):
    """When every provider fails, ask() returns a user-facing message, not a crash (BR5.3, BR5.4)."""
    _seed_minimal(fake_db)
    service = _service_on(fake_db, monkeypatch)

    class _FailingGroq:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    # No secret material in the raised error.
                    raise RuntimeError("provider unavailable")

    class _FailingGemini:
        class models:
            @staticmethod
            def generate_content(**kwargs):
                raise RuntimeError("provider unavailable")

    service._groq_client = _FailingGroq()
    service._client = _FailingGemini()

    result = asyncio.run(service.ask("U1", "C1", _MSG, history=[]))

    # Degraded gracefully to a fixed saturation message (no exception raised).
    assert "saturados" in result["response"]
    assert result["context_used"] == []
    # BR5.4: no credential/token material surfaced to the user.
    lowered = result["response"].lower()
    for leak in ("api_key", "apikey", "token", "password", "secret"):
        assert leak not in lowered
