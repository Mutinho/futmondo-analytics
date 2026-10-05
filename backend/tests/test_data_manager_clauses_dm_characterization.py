"""Characterization safety net for the ``clauses`` responsibility (rank 4).

Freezes the observable effect of the ``DataManagerV2`` clause methods
(``parse_clause_text``, ``save_clauses``, ``get_user_clauses_stats``,
``get_clauses_raw``, ``get_clausulable_player_stats``) over the in-memory SQLite
fake so behavior is identical before and after the DDD extraction (BR2.1/BR3.1).
Asserts the effect — parsed fields, rows written, aggregation, raw payloads, and
the parse-failure ``return None`` edge — never ``assert True`` (BR2.2/BR2.3).

No network, no real DB, no credentials (BR2.3/NFR6): everything runs on the
shared ``:memory:`` SQLite fake seeded from literals.
"""

import pytest

from app.services.data_manager_v2 import DataManagerV2


def _make_dm(fake_db):
    """Build a facade bound to the in-memory fake, with the clause schema seeded."""
    dm = DataManagerV2(skip_init=True)
    dm.db = fake_db
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS championships (
                championship_id TEXT PRIMARY KEY, name TEXT, created_at TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY, username TEXT UNIQUE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS teams (
                team_id TEXT PRIMARY KEY, user_id TEXT, team_name TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clauses (
                championship_id TEXT, news_id TEXT PRIMARY KEY,
                payer_user_id TEXT, payer_team_id TEXT, payer_name TEXT,
                receiver_user_id TEXT, receiver_team_id TEXT, receiver_name TEXT,
                player_name TEXT, amount INTEGER, created_date TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS player_championship_stats (
                championship_id TEXT, player_id TEXT, owner_team_id TEXT,
                owner_team_name TEXT, owner_user_id TEXT, clause_price INTEGER,
                suggested_clause INTEGER, average_last_five REAL,
                average_overall REAL, clause_date TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY, name TEXT
            )
            """
        )
    return dm


def _seed_users(fake_db):
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", ("u-payer", "Payer"))
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)", ("u-recv", "Receiver")
        )
        cursor.execute(
            "INSERT INTO teams (team_id, user_id, team_name) VALUES (?, ?, ?)",
            ("t-payer", "u-payer", "Payer"),
        )
        cursor.execute(
            "INSERT INTO teams (team_id, user_id, team_name) VALUES (?, ?, ?)",
            ("t-recv", "u-recv", "Receiver"),
        )


_CLAUSE_TXT = (
    "El equipo <strong>Payer</strong> ha pagado <strong>21.377.932</strong> "
    "propiedad de <strong>Receiver</strong> como clausula de <strong>Virgili</strong>"
)


def test_parse_clause_text_extracts_fields(fake_db):
    dm = _make_dm(fake_db)
    parsed = dm.parse_clause_text(_CLAUSE_TXT)
    assert parsed is not None
    assert parsed["payer_name"] == "Payer"
    assert parsed["receiver_name"] == "Receiver"
    assert parsed["player_name"] == "Virgili"
    assert parsed["amount"] == 21377932


def test_parse_clause_text_unparseable_returns_none(fake_db):
    dm = _make_dm(fake_db)
    assert dm.parse_clause_text("") is None
    assert dm.parse_clause_text("not a clause at all") is None


def test_save_clauses_writes_row_and_raw_roundtrips(fake_db):
    dm = _make_dm(fake_db)
    _seed_users(fake_db)
    dm.save_clauses(
        "champ1",
        [{"_id": "news1", "styp": "clause", "txt": _CLAUSE_TXT, "created": ""}],
    )

    raw = dm.get_clauses_raw("champ1")
    assert len(raw) == 1
    assert raw[0]["amount"] == 21377932
    assert raw[0]["player_name"] == "Virgili"
    assert raw[0]["payer_team_id"] == "t-payer"
    assert raw[0]["receiver_team_id"] == "t-recv"


def test_save_clauses_skips_non_clause_items(fake_db):
    dm = _make_dm(fake_db)
    _seed_users(fake_db)
    dm.save_clauses("champ1", [{"_id": "n", "styp": "news", "txt": "x", "created": ""}])
    assert dm.get_clauses_raw("champ1") == []


def test_save_clauses_empty_list_is_noop(fake_db):
    dm = _make_dm(fake_db)
    dm.save_clauses("champ1", [])
    assert dm.get_clauses_raw("champ1") == []


def test_get_user_clauses_stats_aggregates_paid_and_received(fake_db):
    dm = _make_dm(fake_db)
    _seed_users(fake_db)
    dm.save_clauses(
        "champ1",
        [{"_id": "news1", "styp": "clause", "txt": _CLAUSE_TXT, "created": ""}],
    )
    stats = dm.get_user_clauses_stats("champ1")
    assert stats["t-payer"]["clauses_paid"] == 1
    assert stats["t-payer"]["total_paid"] == 21377932
    assert stats["t-recv"]["clauses_received"] == 1
    assert stats["t-recv"]["total_received"] == 21377932


def test_get_clausulable_player_stats_joins_player_name(fake_db):
    dm = _make_dm(fake_db)
    with fake_db.get_connection() as conn:
        cursor = fake_db.get_cursor(conn)
        cursor.execute("INSERT INTO players (player_id, name) VALUES (?, ?)", ("p1", "Messi"))
        cursor.execute(
            """
            INSERT INTO player_championship_stats
            (championship_id, player_id, owner_team_id, owner_team_name, owner_user_id,
             clause_price, suggested_clause, average_last_five, average_overall, clause_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("champ1", "p1", "t1", "Team 1", "u1", 100, 120, 8.5, 7.9, "2099-01-01"),
        )
    rows = dm.get_clausulable_player_stats("champ1")
    assert len(rows) == 1
    assert rows[0]["player_id"] == "p1"
    assert rows[0]["player_name"] == "Messi"
    assert rows[0]["clause_price"] == 100


def test_get_clausulable_player_stats_unknown_championship_empty(fake_db):
    dm = _make_dm(fake_db)
    assert dm.get_clausulable_player_stats("nope") == []
