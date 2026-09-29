"""Characterization tests for the assistant factual layer (BR2.1, BR2.2).

These freeze the CURRENT observable behavior of ``_try_factual_answer`` and its
``_factual_*`` handlers BEFORE they move to ``assistant/application/`` over
``AssistantReadPort``. After extraction the same assertions must hold.

BR2.1 — a factual question is answered directly from DB data, WITHOUT any LLM
         call (the handlers never touch ``client`` / ``groq_client``).
BR2.2 — the answer content reflects the rows read from the data source (the
         reads are the port's responsibility; here we seed the fake DB and
         assert the answer mirrors it).

The DB boundary is the injected in-memory ``fake_db``; no network, no LLM.
"""

import app.services.assistant.facade as facade_mod
from app.services.assistant_service import AssistantService


def _service_on(fake_db, monkeypatch):
    """Build a service whose DB boundary is the in-memory fake (no LLM)."""
    monkeypatch.setattr(facade_mod, "get_db", lambda: fake_db)
    return AssistantService()


def _create_team_value_schema(fake_db):
    """Minimal schema for the team_value factual handler."""
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute(
            "CREATE TABLE player_championship_stats "
            "(championship_id TEXT, owner_team_id TEXT, player_id TEXT)"
        )
        cur.execute("CREATE TABLE players (player_id TEXT, value INTEGER)")


def _seed_two_players(fake_db, championship_id, team_id):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute(
            "INSERT INTO players (player_id, value) VALUES ('p1', 10000000), ('p2', 6000000)"
        )
        cur.execute(
            fake_db.adapt_params(
                "INSERT INTO player_championship_stats (championship_id, owner_team_id, player_id) "
                "VALUES (?, ?, 'p1'), (?, ?, 'p2')"
            ),
            (championship_id, team_id, championship_id, team_id),
        )


_IDENTITY = {
    "user_name": "Ana",
    "team_name": "Los Cracks",
    "team_id": "T1",
    "championship_name": "Liga Test",
    "is_pro": False,
}


# --- BR2.1 / BR2.2: factual answer from data, no LLM -------------------------


def test_factual_team_value_answer_reflects_db_rows(fake_db, monkeypatch):
    """A team-value factual question is answered from DB rows, no LLM (BR2.1, BR2.2)."""
    _create_team_value_schema(fake_db)
    _seed_two_players(fake_db, "C1", "T1")
    service = _service_on(fake_db, monkeypatch)

    answer = service._try_factual_answer("U1", "C1", "¿Cuánto vale mi plantilla?", _IDENTITY)

    assert answer is not None
    # 10M + 6M = 16.0M total, 2 players, average 8.0M — mirrors the seeded rows.
    assert "16.0M€" in answer
    assert "Jugadores: 2" in answer
    assert "8.0M€" in answer


def test_factual_bypassed_by_strategy_words(fake_db, monkeypatch):
    """Strategy questions bypass the factual path so they reach the LLM (BR2.1)."""
    _create_team_value_schema(fake_db)
    _seed_two_players(fake_db, "C1", "T1")
    service = _service_on(fake_db, monkeypatch)

    # Contains a strategy word ("recomiend") → factual path returns None.
    answer = service._try_factual_answer(
        "U1", "C1", "¿Qué jugador me recomiendas por su valor de plantilla?", _IDENTITY
    )
    assert answer is None


def test_factual_no_match_returns_none(fake_db, monkeypatch):
    """A message matching no factual pattern returns None (flow continues to LLM)."""
    _create_team_value_schema(fake_db)
    service = _service_on(fake_db, monkeypatch)

    answer = service._try_factual_answer("U1", "C1", "háblame del once ideal", _IDENTITY)
    assert answer is None


def test_factual_does_not_invoke_llm(fake_db, monkeypatch):
    """The factual path never touches the LLM providers (BR2.1).

    Accessing ``client`` would raise (no GEMINI_API_KEY); the factual answer must
    complete without ever touching it, proving no LLM call happens.
    """
    _create_team_value_schema(fake_db)
    _seed_two_players(fake_db, "C1", "T1")
    service = _service_on(fake_db, monkeypatch)

    # Sentinel: if the factual path touched the LLM client, this would flip.
    touched = {"llm": False}

    class _Guard:
        def __getattr__(self, _name):
            touched["llm"] = True
            raise AssertionError("factual path must not touch the LLM")

    monkeypatch.setattr(service, "_client", _Guard(), raising=False)
    monkeypatch.setattr(service, "_groq_client", _Guard(), raising=False)

    answer = service._try_factual_answer("U1", "C1", "¿qué valor tiene mi equipo?", _IDENTITY)
    assert answer is not None
    assert touched["llm"] is False
