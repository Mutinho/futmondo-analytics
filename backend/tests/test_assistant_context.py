"""Characterization tests for the assistant context builder (BR3.1-BR3.3).

These freeze the CURRENT observable behavior of ``_build_context`` and the
``_ctx_*`` helpers BEFORE they move to ``assistant/application/`` over
``AssistantReadPort``. After extraction the same assertions must hold.

BR3.1 — when there is no factual answer, the builder assembles context from DB
         (roster + budget are always attempted).
BR3.2 — all reads go through the DB (here the injected in-memory fake).
BR3.3 — degradation is NOT uniform across the ``_ctx_*`` branches (reviewer note
         R-03): ``_ctx_market_from_db`` degrades to ``""`` on a read failure
         (``except Exception: return ""``), while other branches (e.g.
         ``_ctx_standings``) do NOT swallow — a missing table raises. We freeze
         BOTH shapes.
"""

import pytest

import app.services.assistant.facade as facade_mod
from app.services.assistant_service import AssistantService


def _service_on(fake_db, monkeypatch):
    monkeypatch.setattr(facade_mod, "get_db", lambda: fake_db)
    return AssistantService()


_IDENTITY = {
    "user_name": "Ana",
    "team_name": "Los Cracks",
    "team_id": "T1",
    "championship_name": "Liga Test",
    "is_pro": False,
}


def _seed_roster_and_budget(fake_db):
    """Minimal schema+rows so _ctx_roster and _ctx_budget produce content."""
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute(
            "CREATE TABLE player_championship_stats "
            "(championship_id TEXT, owner_team_id TEXT, owner_team_name TEXT, player_id TEXT, "
            "average_overall REAL, average_last_five REAL, clause_price INTEGER)"
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
            "CREATE TABLE user_championships (user_id TEXT, championship_id TEXT, initial_budget INTEGER)"
        )
        cur.execute(
            "CREATE TABLE team_prizes (championship_id TEXT, team_id TEXT, ranking_prize INTEGER, "
            "mvp_prize INTEGER, points_prize INTEGER, dream_team_prize INTEGER)"
        )
        cur.execute(
            "INSERT INTO players (player_id, name, role, value, real_team_id) "
            "VALUES ('p1', 'Vinicius', 'DEL', 30000000, 'rt1')"
        )
        cur.execute(
            "INSERT INTO player_championship_stats "
            "(championship_id, owner_team_id, player_id, average_overall, average_last_five) "
            "VALUES ('C1', 'T1', 'p1', 8.0, 8.5)"
        )
        cur.execute(
            "INSERT INTO user_championships (user_id, championship_id, initial_budget) VALUES ('U1', 'C1', 200000000)"
        )


# --- BR3.1 / BR3.2: builds roster + budget context from DB -------------------


def test_build_context_includes_roster_and_budget(fake_db, monkeypatch):
    """A non-factual, non-follow-up question builds roster + budget context (BR3.1, BR3.2)."""
    _seed_roster_and_budget(fake_db)
    service = _service_on(fake_db, monkeypatch)

    context, context_types = service._build_context(
        "U1", "C1", "analiza mi plantilla en profundidad para la temporada", _IDENTITY
    )

    assert "roster" in context_types
    assert "budget" in context_types
    assert "Vinicius" in context  # roster row read from the fake DB
    assert "PRESUPUESTO" in context  # budget section header


# --- BR3.3: NON-uniform degradation (reviewer note R-03) ---------------------


def test_ctx_market_from_db_degrades_to_empty_string(fake_db, monkeypatch):
    """Market read degrades to '' when the table is absent (BR3.3, degrading branch)."""
    service = _service_on(fake_db, monkeypatch)
    # No market_today table exists → the branch swallows and returns "".
    assert service._ctx_market_from_db("C1") == ""


def test_ctx_standings_does_not_degrade_on_missing_table(fake_db, monkeypatch):
    """Standings context does NOT swallow: a missing table raises (BR3.3, non-degrading branch).

    This freezes the asymmetry called out in R-03 — degradation is per-branch,
    not uniform, so the extraction must preserve each branch's shape.
    """
    service = _service_on(fake_db, monkeypatch)
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        with pytest.raises(Exception):
            # _ctx_standings opens its own read via the shared cursor; the table
            # does not exist, so the underlying execute raises (no try/except).
            service._ctx_standings(cur, fake_db, "C1")
