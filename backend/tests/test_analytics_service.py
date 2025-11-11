import types

import pytest

from app.services.analytics_service import AnalyticsService


@pytest.fixture
def analytics_service(monkeypatch):
    class StubDM:
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

    stub_dm = StubDM()

    def fake_init(self):
        self.dm = stub_dm

    monkeypatch.setattr(AnalyticsService, "__init__", fake_init)
    return AnalyticsService()


def test_championship_trends(analytics_service):
    result = analytics_service.get_championship_trends("champ", window=2)
    assert result["teams"][0]["team_name"] == "Team One"
    assert result["teams"][0]["total_points"] == 520


def test_player_form(analytics_service):
    result = analytics_service.get_player_form("champ", window=2)
    assert result["players"][0]["average_points"] == 11


def test_player_value_trend(analytics_service):
    result = analytics_service.get_player_value_trend("champ", window=30)
    assert result["players"][0]["latest_price"] == 1000000


def test_clause_network(analytics_service):
    result = analytics_service.get_clause_network("champ")
    assert result["edges"][0]["count"] == 1


def test_opportunity_streaks(analytics_service):
    result = analytics_service.get_opportunity_streaks("champ", min_streak=3, threshold=6)
    assert result["streaks"][0]["streak_length"] == 3


def test_matchday_projections(analytics_service):
    result = analytics_service.get_matchday_projections("champ", matchday=11)
    assert result["matches"][0]["home"]["team_name"] == "Team One"


