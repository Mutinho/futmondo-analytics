import types

import pytest

from app.services.analytics_service import AnalyticsService


@pytest.fixture
def analytics_service():
    """Analytics facade wired to an in-memory stub port (no DB, no network).

    Injects the stub through the NEW constructor (``AnalyticsService(data=...)``,
    BR2.6) instead of monkeypatching ``__init__``. The stub implements the whole
    ``AnalyticsDataPort`` surface, including the two ``fetch_*`` reads that
    replaced the former inline SQL: ``fetch_all_teams`` returns the same team
    lookup the old fixture preloaded into ``_team_cache``, and
    ``fetch_players_by_ids`` returns ``{}`` (mirroring the old no-DB path where
    ``player_info_map`` stayed empty), so every ``get_*`` payload is identical
    before and after the extraction (BR1.1).
    """

    class StubPort:
        def __init__(self):
            self.get_latest_matchday = lambda championship_id: 10
            self.get_team_by_id = lambda team_id: {"team_id": team_id, "team_name": "Team One"}
            self.get_team_standings_history = lambda championship_id, window=None: [
                {"team_id": "team-1", "matchday": 9, "position": 2, "points": 450, "points_this_matchday": 60, "team_value": 100},
                {"team_id": "team-1", "matchday": 10, "position": 1, "points": 520, "points_this_matchday": 70, "team_value": 110},
            ]
            self.get_player_performance_history = lambda championship_id, player_ids=None, window=None: [
                {"player_id": "player-1", "team_id": "team-1", "matchday": 9, "points": 10, "value": 0, "was_best_player": False},
                {"player_id": "player-1", "team_id": "team-1", "matchday": 10, "points": 12, "value": 0, "was_best_player": False},
            ]
            self.get_player_by_id = lambda player_id: {"id": player_id, "name": "Player One"}
            self.get_transactions_raw = lambda championship_id, days=None: [
                {"player_id": "player-1", "price": 1000000, "buyer_team_id": "team-1", "seller_team_id": "team-2", "transaction_date": None, "matchday": 10,
                 "transaction_id": "txn-1", "seller_user_id": None, "buyer_user_id": None}
            ]
            self.get_clausulable_player_stats = lambda championship_id: [
                {"player_id": "player-1", "clause_price": 1200000, "suggested_clause": 1500000}
            ]
            self.get_clauses_raw = lambda championship_id, days=None: [
                {"payer_team_id": "team-1", "receiver_team_id": "team-2", "amount": 5000000, "created_date": None, "payer_user_id": None,
                 "receiver_user_id": None, "player_name": "Player One"}
            ]
            self.get_free_agent_candidates = lambda championship_id: [
                {"player_id": "player-2", "name": "Player Two", "clause_price": 800000, "suggested_clause": 1000000,
                 "average_last_five": 7.5, "average_overall": 6.2}
            ]
            self.get_player_streak_data = lambda championship_id, min_matchday=None: [
                {"player_id": "player-1", "matchday": 8, "points": 7},
                {"player_id": "player-1", "matchday": 9, "points": 8},
                {"player_id": "player-1", "matchday": 10, "points": 9},
            ]
            self.get_match_odds = lambda championship_id, matchday=None, upcoming_only=False: [
                {
                    "match_id": "match-1",
                    "matchday": 11,
                    "match_date": None,
                    "home_team_id": "team-1",
                    "home_team_name": "Team One",
                    "away_team_id": "team-2",
                    "away_team_name": "Team Two",
                    "odds_home": 1.8,
                    "odds_draw": 3.5,
                    "odds_away": 4.0
                }
            ]
            # Used by _build_team_lookup / _resolve_team to map team ids to
            # readable names without touching the DB (get_user_consistency,
            # get_user_market_activity, get_championship_custom_classification).
            self.get_all_users_with_points = lambda championship_id: [
                {"team_id": "team-1", "user_id": "user-1", "team_name": "Team One", "username": "Alice"},
                {"team_id": "team-2", "user_id": "user-2", "team_name": "Team Two", "username": "Bob"},
            ]

        # The two reads that replaced the former inline SQL (BR1.2). fetch_all_teams
        # reproduces the team lookup the old fixture preloaded into _team_cache;
        # fetch_players_by_ids returns {} (the old no-DB path left it empty).
        def fetch_all_teams(self):
            return {
                "team-1": {"team_id": "team-1", "user_id": None, "team_name": "Team One"},
            }

        def fetch_players_by_ids(self, player_ids):
            return {}

    return AnalyticsService(data=StubPort())


def test_championship_trends(analytics_service):
    result = analytics_service.get_championship_trends("champ", window=2)
    assert result["teams"][0]["team_name"] == "Team One"
    assert result["teams"][0]["total_points"] == 520


def test_player_form(analytics_service):
    result = analytics_service.get_player_form("champ", window=2)
    assert result["players"][0]["average_points"] == 11


def test_player_value_trend(analytics_service):
    result = analytics_service.get_player_value_trend("champ", window=30)
    assert result["players"][0]["last_transaction_price"] == 1000000


def test_clause_network(analytics_service):
    result = analytics_service.get_clause_network("champ")
    assert result["edges"][0]["count"] == 1


def test_opportunity_streaks(analytics_service):
    result = analytics_service.get_opportunity_streaks("champ", min_streak=3, threshold=6)
    assert result["streaks"][0]["streak_length"] == 3


def test_matchday_projections(analytics_service):
    result = analytics_service.get_matchday_projections("champ", matchday=11)
    assert result["matches"][0]["home"]["team_name"] == "Team One"


# ---------------------------------------------------------------------------
# Characterization-first (Step 3, BR1.3): freeze the 5 previously uncovered
# get_* BEFORE moving any code. Each asserts a real payload key/value produced
# by the CURRENT analytics_service.py — never assert True, never mirror specs.
# ---------------------------------------------------------------------------


def test_championship_custom_classification(analytics_service):
    result = analytics_service.get_championship_custom_classification("champ")
    classification = result["classification"]
    # team-1 accrued 60 + 70 = 130 points across matchdays 9 and 10.
    assert classification[0]["team_id"] == "team-1"
    assert classification[0]["team_name"] == "Team One"
    assert classification[0]["total_points"] == 130.0
    assert classification[0]["rank"] == 1
    assert result["available_matchdays"] == [9, 10]


def test_championship_heatmap(analytics_service):
    result = analytics_service.get_championship_heatmap("champ")
    matchdays = {cell["matchday"]: cell["scores"] for cell in result["matchdays"]}
    # points_this_matchday for team-1: 60 at md 9, 70 at md 10.
    assert matchdays[9]["team-1"] == 60
    assert matchdays[10]["team-1"] == 70
    assert result["latest_matchday"] == 10


def test_user_consistency(analytics_service):
    result = analytics_service.get_user_consistency("champ")
    team = result["teams"][0]
    assert team["team_id"] == "team-1"
    assert team["team_name"] == "Team One"
    # mean of [60, 70] = 65.0 over 2 matches.
    assert team["matches"] == 2
    assert team["average_points"] == 65.0


def test_user_market_activity(analytics_service):
    result = analytics_service.get_user_market_activity("champ", window_days=30)
    teams = {t["team_id"]: t for t in result["teams"]}
    # One transaction: buyer team-1 spent 1_000_000; seller team-2 received it.
    assert teams["team-1"]["spent"] == 1000000
    assert teams["team-1"]["team_name"] == "Team One"
    # One clause: payer team-1 pays 5_000_000 to receiver team-2.
    assert teams["team-1"]["clause_total_paid"] == 5000000


def test_market_watchlist(analytics_service):
    result = analytics_service.get_market_watchlist("champ", limit=20)
    # player-2 free agent with average_last_five=7.5 -> rounded to 7.5.
    watchlist = result["players"]
    assert watchlist[0]["player_id"] == "player-2"
    assert watchlist[0]["name"] == "Player Two"
    assert watchlist[0]["average"] == 7.5


# ---------------------------------------------------------------------------
# Adapter contract tests (Step 6, BR1.2): the two relocated raw SELECTs must
# return the EXACT row shape the former inline SQL produced. Uses the in-memory
# ``fake_db`` (SQLite ``:memory:``) from backend/conftest.py, honoring the
# db_connection contract (get_connection/get_cursor/adapt_params). No network,
# no real DB, no credentials.
# ---------------------------------------------------------------------------


def _make_adapter(fake_db, dm):
    from app.services.analytics.infrastructure.data_manager_adapter import (
        DataManagerAnalyticsAdapter,
    )

    # Inject the fake DB via db_factory; inject a stub data manager for delegation.
    return DataManagerAnalyticsAdapter(dm=dm, db_factory=lambda: fake_db)


def test_adapter_fetch_all_teams_row_shape(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute("CREATE TABLE teams (team_id TEXT, user_id TEXT, team_name TEXT)")
        cur.execute("INSERT INTO teams VALUES ('team-1', 'user-1', 'Team One')")
        cur.execute("INSERT INTO teams VALUES ('team-2', 'user-2', 'Team Two')")

    adapter = _make_adapter(fake_db, dm=types.SimpleNamespace())
    teams = adapter.fetch_all_teams()

    # Exact shape the former inline SELECT produced: {team_id: {team_id, user_id, team_name}}.
    assert teams["team-1"] == {"team_id": "team-1", "user_id": "user-1", "team_name": "Team One"}
    assert teams["team-2"]["team_name"] == "Team Two"


def test_adapter_fetch_players_by_ids_row_shape(fake_db):
    with fake_db.get_connection() as conn:
        cur = fake_db.get_cursor(conn)
        cur.execute(
            "CREATE TABLE players (player_id TEXT, name TEXT, real_team_id TEXT, value INTEGER)"
        )
        cur.execute("INSERT INTO players VALUES ('p1', 'Alpha', 'rt-1', 5000000)")
        cur.execute("INSERT INTO players VALUES ('p2', 'Beta', 'rt-2', 0)")

    adapter = _make_adapter(fake_db, dm=types.SimpleNamespace())
    info = adapter.fetch_players_by_ids(["p1", "p2"])

    # Exact shape the former inline SELECT produced: {name, real_team_id, value}.
    assert info["p1"] == {"name": "Alpha", "real_team_id": "rt-1", "value": 5000000}
    # value falls back to 0 when NULL/0 (preserved `row[3] or 0`).
    assert info["p2"]["value"] == 0


def test_adapter_fetch_players_by_ids_empty_returns_empty(fake_db):
    adapter = _make_adapter(fake_db, dm=types.SimpleNamespace())
    assert adapter.fetch_players_by_ids([]) == {}


def test_adapter_delegates_reads_to_data_manager(fake_db):
    calls = {}

    class RecordingDM:
        def get_team_standings_history(self, championship_id, window=None):
            calls["standings"] = (championship_id, window)
            return [{"team_id": "team-1", "matchday": 1, "points_this_matchday": 5}]

        def get_latest_matchday(self, championship_id):
            calls["latest"] = championship_id
            return 7

    adapter = _make_adapter(fake_db, dm=RecordingDM())

    # Delegated reads return the DM result unchanged and forward arguments.
    assert adapter.get_latest_matchday("champ") == 7
    assert calls["latest"] == "champ"
    result = adapter.get_team_standings_history("champ", window=3)
    assert result[0]["team_id"] == "team-1"
    assert calls["standings"] == ("champ", 3)


def test_no_arg_constructor_and_historical_import_path(monkeypatch):
    """Step 9: ``AnalyticsService()`` (no args) still constructs, and the
    historical import path resolves to the same facade. The DataManagerV2 the
    default adapter builds is stubbed so no DB is touched."""
    import app.services.analytics.infrastructure.data_manager_adapter as adapter_mod
    from app.services.analytics.facade import AnalyticsService as FacadeService
    from app.services.analytics_service import AnalyticsService as ShimService

    monkeypatch.setattr(adapter_mod, "DataManagerV2", lambda: types.SimpleNamespace())

    # The re-export shim and the facade are the same class (import path preserved).
    assert ShimService is FacadeService

    svc = ShimService()  # no arguments — the endpoint calls it this way
    # Observable attributes preserved (FR2.3).
    assert svc._team_cache == {}
    assert svc._player_cache == {}
    assert hasattr(svc, "get_championship_trends")


