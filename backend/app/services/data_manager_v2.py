"""
Data Manager V2 - Optimized for Historical Championship Statistics Analysis

This version is designed for efficient historical and statistical queries.
Key design principles:
- Temporal data with proper indexing on dates/matchdays
- Historical records preserved (no data loss)
- Optimized for aggregation queries
- Support for time-series analysis
- Efficient joins for statistical queries
"""

import logging
import json
import uuid
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from app.core.config import CACHE_DURATION_HOURS, DATABASE_PATH
from app.services.db_connection import DBConnection

logger = logging.getLogger(__name__)


class DataManagerV2:
    """Data manager optimized for historical championship statistics"""
    
    def __init__(self, db_path: str = None, skip_init: bool = True):
        self.db_path = db_path or DATABASE_PATH
        self.cache_duration = timedelta(hours=CACHE_DURATION_HOURS)
        self.db = DBConnection()
        if not skip_init:
            self._init_database()
        self._ensure_schema_updates()
    
    def _init_database(self):
        """Initialize database with optimized schema for historical analysis"""
        from app.services.data_manager.schema_lifecycle.application.schema_lifecycle import (
            SchemaLifecycleService,
        )
        from app.services.data_manager.schema_lifecycle.infrastructure.schema_lifecycle_adapter import (
            SchemaLifecycleAdapter,
        )

        return SchemaLifecycleService(SchemaLifecycleAdapter(self)).init_database()

    def reset_database(self):
        """Drop all tables and recreate schema"""
        from app.services.data_manager.schema_lifecycle.application.schema_lifecycle import (
            SchemaLifecycleService,
        )
        from app.services.data_manager.schema_lifecycle.infrastructure.schema_lifecycle_adapter import (
            SchemaLifecycleAdapter,
        )

        return SchemaLifecycleService(SchemaLifecycleAdapter(self)).reset_database()

    def save_player(self, player_data: Dict) -> str:
        """Save or update player information"""
        from app.services.data_manager.players.application.players import PlayersService
        from app.services.data_manager.players.infrastructure.players_adapter import (
            PlayersAdapter,
        )

        return PlayersService(PlayersAdapter(self)).save_player(player_data)

    def save_players_batch(self, players: List[Dict]) -> int:
        """Save or update multiple players in a single transaction (batch upsert)."""
        from app.services.data_manager.players.application.players import PlayersService
        from app.services.data_manager.players.infrastructure.players_adapter import (
            PlayersAdapter,
        )

        return PlayersService(PlayersAdapter(self)).save_players_batch(players)

    def delete_orphan_players(self, live_player_ids: List[str]) -> int:
        """Delete players that are neither in the current API list nor referenced by any historical table."""
        from app.services.data_manager.players.application.players import PlayersService
        from app.services.data_manager.players.infrastructure.players_adapter import (
            PlayersAdapter,
        )

        return PlayersService(PlayersAdapter(self)).delete_orphan_players(live_player_ids)

    def save_team_standing(self, championship_id: str, team_id: str, matchday: int,
                           position: int, points: int, points_this_matchday: int = 0,
                          team_value: int = None, conn=None, cursor=None, **kwargs) -> None:
        """Save team standing for a specific matchday"""
        from app.services.data_manager.teams_standings.application.teams_standings import (
            TeamsStandingsService,
        )
        from app.services.data_manager.teams_standings.infrastructure.teams_standings_adapter import (
            TeamsStandingsAdapter,
        )

        return TeamsStandingsService(TeamsStandingsAdapter(self)).save_team_standing(
            championship_id, team_id, matchday, position, points,
            points_this_matchday=points_this_matchday, team_value=team_value,
            conn=conn, cursor=cursor, **kwargs
        )

    def save_player_performance(self, championship_id: str, player_id: str, team_id: str,
                               matchday: int, points: int, value: int = None,
                               was_best_player: bool = False, **kwargs) -> None:
        """Save player performance for a specific matchday (single record)"""
        from app.services.data_manager.performance.application.performance import PerformanceService
        from app.services.data_manager.performance.infrastructure.performance_adapter import (
            PerformanceAdapter,
        )

        return PerformanceService(PerformanceAdapter(self)).save_player_performance(
            championship_id, player_id, team_id, matchday, points,
            value=value, was_best_player=was_best_player, **kwargs
        )
    def save_player_performance_batch(self, championship_id: str, records: List[Dict]) -> int:
        """Save multiple player performance records in a single transaction (batch)."""
        from app.services.data_manager.performance.application.performance import PerformanceService
        from app.services.data_manager.performance.infrastructure.performance_adapter import (
            PerformanceAdapter,
        )

        return PerformanceService(PerformanceAdapter(self)).save_player_performance_batch(
            championship_id, records
        )
    def save_players(self, players: List[Dict]):
        """Save players data to database (optimized for historical analysis)"""
        from app.services.data_manager.players.application.players import PlayersService
        from app.services.data_manager.players.infrastructure.players_adapter import (
            PlayersAdapter,
        )

        return PlayersService(PlayersAdapter(self)).save_players(players)

    def save_team(self, team_id: str, team_name: str, user_id: str = "",
                  owner_name: str = "", current_points: int = 0, team_value: int = 0):
        """Save team information"""
        from app.services.data_manager.teams_standings.application.teams_standings import (
            TeamsStandingsService,
        )
        from app.services.data_manager.teams_standings.infrastructure.teams_standings_adapter import (
            TeamsStandingsAdapter,
        )

        return TeamsStandingsService(TeamsStandingsAdapter(self)).save_team(
            team_id, team_name, user_id=user_id, owner_name=owner_name,
            current_points=current_points, team_value=team_value
        )

    def _ensure_user(self, user_id: str, username: str):
        """Ensure user exists in database"""
        from app.services.data_manager.users_stats_evolution.application.users_stats_evolution import (
            UsersStatsEvolutionService,
        )
        from app.services.data_manager.users_stats_evolution.infrastructure.users_stats_evolution_adapter import (
            UsersStatsEvolutionAdapter,
        )

        return UsersStatsEvolutionService(UsersStatsEvolutionAdapter(self)).ensure_user(user_id, username)

    def save_round_ranking(self, round_number: int, championship_id: str, teams: List[Dict]):
        """Save round ranking data for historical analysis"""
        from app.services.data_manager.teams_standings.application.teams_standings import (
            TeamsStandingsService,
        )
        from app.services.data_manager.teams_standings.infrastructure.teams_standings_adapter import (
            TeamsStandingsAdapter,
        )

        return TeamsStandingsService(TeamsStandingsAdapter(self)).save_round_ranking(
            round_number, championship_id, teams
        )

    def save_player_transactions(self, player_id: str, owners_history: List[Dict]):
        """Legacy hook kept for compatibility with older scripts."""
        from app.services.data_manager.transactions.application.transactions import (
            TransactionsService,
        )
        from app.services.data_manager.transactions.infrastructure.transactions_adapter import (
            TransactionsAdapter,
        )

        return TransactionsService(TransactionsAdapter(self)).save_player_transactions(
            player_id, owners_history
        )

    def save_pressroom_transactions(self, championship_id: str, transactions: List[Dict]):
        """Save transactions from pressroom endpoint (batch optimized for PostgreSQL)."""
        from app.services.data_manager.transactions.application.transactions import (
            TransactionsService,
        )
        from app.services.data_manager.transactions.infrastructure.transactions_adapter import (
            TransactionsAdapter,
        )

        return TransactionsService(TransactionsAdapter(self)).save_pressroom_transactions(
            championship_id, transactions
        )

    def save_matchday_article(
        self,
        championship_id: str,
        matchday: int,
        article: str,
        summary: Optional[Dict] = None,
        generated_at: Optional[datetime] = None
    ):
        """Persist generated matchday humor article and optional structured summary."""
        from app.services.data_manager.news_articles.application.news_articles import NewsArticlesService
        from app.services.data_manager.news_articles.infrastructure.news_articles_adapter import (
            NewsArticlesAdapter,
        )

        return NewsArticlesService(NewsArticlesAdapter(self)).save_matchday_article(
            championship_id, matchday, article, summary=summary, generated_at=generated_at
        )
    def get_matchday_article(self, championship_id: str, matchday: int) -> Optional[Dict[str, Any]]:
        """Retrieve stored matchday article and metadata."""
        from app.services.data_manager.news_articles.application.news_articles import NewsArticlesService
        from app.services.data_manager.news_articles.infrastructure.news_articles_adapter import (
            NewsArticlesAdapter,
        )

        return NewsArticlesService(NewsArticlesAdapter(self)).get_matchday_article(
            championship_id, matchday
        )
    def get_user_id_by_name(self, user_name: str) -> Optional[Dict[str, str]]:
        """Get user_id and team_id by user name (username or team_name)"""
        from app.services.data_manager.users_stats_evolution.application.users_stats_evolution import (
            UsersStatsEvolutionService,
        )
        from app.services.data_manager.users_stats_evolution.infrastructure.users_stats_evolution_adapter import (
            UsersStatsEvolutionAdapter,
        )

        return UsersStatsEvolutionService(UsersStatsEvolutionAdapter(self)).get_user_id_by_name(user_name)

    def save_punishments_bonuses(self, championship_id: str, news_items: List[Dict]):
        """Save punishments and bonuses from locker news"""
        from app.services.data_manager.punishments_bonuses.application.punishments_bonuses import (
            PunishmentsBonusesService,
        )
        from app.services.data_manager.punishments_bonuses.infrastructure.punishments_bonuses_adapter import (
            PunishmentsBonusesAdapter,
        )

        return PunishmentsBonusesService(PunishmentsBonusesAdapter(self)).save_punishments_bonuses(
            championship_id, news_items
        )

    def get_user_punishments_bonuses(self, championship_id: str) -> Dict[str, Dict]:
        """Get all punishments and bonuses grouped by user_id/team_id"""
        from app.services.data_manager.punishments_bonuses.application.punishments_bonuses import (
            PunishmentsBonusesService,
        )
        from app.services.data_manager.punishments_bonuses.infrastructure.punishments_bonuses_adapter import (
            PunishmentsBonusesAdapter,
        )

        return PunishmentsBonusesService(PunishmentsBonusesAdapter(self)).get_user_punishments_bonuses(
            championship_id
        )

    def parse_clause_text(self, text: str) -> Optional[Dict[str, str]]:
        """Parse clause text to extract payer, receiver, amount, and player name"""
        from app.services.data_manager.clauses.application.clauses import ClausesService
        from app.services.data_manager.clauses.infrastructure.clauses_adapter import (
            ClausesAdapter,
        )

        return ClausesService(ClausesAdapter(self)).parse_clause_text(text)

    def save_clauses(self, championship_id: str, news_items: List[Dict]):
        """Save clauses from locker news"""
        from app.services.data_manager.clauses.application.clauses import ClausesService
        from app.services.data_manager.clauses.infrastructure.clauses_adapter import (
            ClausesAdapter,
        )

        return ClausesService(ClausesAdapter(self)).save_clauses(championship_id, news_items)

    def get_user_clauses_stats(self, championship_id: str) -> Dict[str, Dict]:
        """Get clause statistics grouped by user_id/team_id"""
        from app.services.data_manager.clauses.application.clauses import ClausesService
        from app.services.data_manager.clauses.infrastructure.clauses_adapter import (
            ClausesAdapter,
        )

        return ClausesService(ClausesAdapter(self)).get_user_clauses_stats(championship_id)

    def _get_or_create_user_id(self, user_id_or_username: str, username: str) -> str:
        """Get or create user ID from username or ID"""
        from app.services.data_manager.users_stats_evolution.application.users_stats_evolution import (
            UsersStatsEvolutionService,
        )
        from app.services.data_manager.users_stats_evolution.infrastructure.users_stats_evolution_adapter import (
            UsersStatsEvolutionAdapter,
        )

        return UsersStatsEvolutionService(UsersStatsEvolutionAdapter(self)).get_or_create_user_id(
            user_id_or_username, username
        )

    def save_market_players(self, championship_id: str, players: List[Dict], matchday: int = None):
        """Save market players data with historical tracking"""
        from app.services.data_manager.market_roster.application.market_roster import (
            MarketRosterService,
        )
        from app.services.data_manager.market_roster.infrastructure.market_roster_adapter import (
            MarketRosterAdapter,
        )

        return MarketRosterService(MarketRosterAdapter(self)).save_market_players(
            championship_id, players, matchday=matchday
        )

    def save_team_roster(self, championship_id: str, team_id: str, players: List[Dict], matchday: int = None):
        """Save team roster with historical tracking"""
        from app.services.data_manager.market_roster.application.market_roster import (
            MarketRosterService,
        )
        from app.services.data_manager.market_roster.infrastructure.market_roster_adapter import (
            MarketRosterAdapter,
        )

        return MarketRosterService(MarketRosterAdapter(self)).save_team_roster(
            championship_id, team_id, players, matchday=matchday
        )

    def ensure_championship_exists(self, championship_id: str, name: str = None, conn=None, cursor=None):
        """Ensure championship record exists in championships table"""
        from app.services.data_manager.schema_lifecycle.application.schema_lifecycle import (
            SchemaLifecycleService,
        )
        from app.services.data_manager.schema_lifecycle.infrastructure.schema_lifecycle_adapter import (
            SchemaLifecycleAdapter,
        )

        return SchemaLifecycleService(SchemaLifecycleAdapter(self)).ensure_championship_exists(
            championship_id, name=name, conn=conn, cursor=cursor
        )

    def _ensure_championship_in_transaction(self, cursor, championship_id: str, name: str = None):
        """Internal helper to ensure championship exists using provided cursor"""
        from app.services.data_manager.schema_lifecycle.application.schema_lifecycle import (
            SchemaLifecycleService,
        )
        from app.services.data_manager.schema_lifecycle.infrastructure.schema_lifecycle_adapter import (
            SchemaLifecycleAdapter,
        )

        return SchemaLifecycleService(SchemaLifecycleAdapter(self)).ensure_championship_in_transaction(
            cursor, championship_id, name=name
        )

    def get_last_sync_metadata(self, championship_id: str, data_type: str) -> Optional[Dict]:
        """Get last sync metadata for a specific data type"""
        from app.services.data_manager.sync_metadata_cache.application.sync_metadata_cache import (
            SyncMetadataCacheService,
        )
        from app.services.data_manager.sync_metadata_cache.infrastructure.sync_metadata_cache_adapter import (
            SyncMetadataCacheAdapter,
        )

        return SyncMetadataCacheService(SyncMetadataCacheAdapter(self)).get_last_sync_metadata(
            championship_id, data_type
        )

    def update_sync_metadata(self, championship_id: str, data_type: str, last_sync_id: str = None,
                            last_sync_date: datetime = None, last_sync_matchday: int = None,
                            records_synced: int = 0, sync_duration_seconds: float = None,
                            sync_status: str = "success", error_message: str = None):
        """Update sync metadata after a synchronization"""
        from app.services.data_manager.sync_metadata_cache.application.sync_metadata_cache import (
            SyncMetadataCacheService,
        )
        from app.services.data_manager.sync_metadata_cache.infrastructure.sync_metadata_cache_adapter import (
            SyncMetadataCacheAdapter,
        )

        return SyncMetadataCacheService(SyncMetadataCacheAdapter(self)).update_sync_metadata(
            championship_id, data_type, last_sync_id=last_sync_id,
            last_sync_date=last_sync_date, last_sync_matchday=last_sync_matchday,
            records_synced=records_synced, sync_duration_seconds=sync_duration_seconds,
            sync_status=sync_status, error_message=error_message
        )

    def save_dream_team_mvp(self, championship_id: str, round_id: str, matchday: int,
                            dream_team_players: List[str], mvp_player_id: str = None,
                            player_details: Optional[Dict[str, Dict]] = None) -> None:
        """Save dream team and MVP for a specific round"""
        from app.services.data_manager.dream_teams_mvp.application.dream_teams_mvp import (
            DreamTeamsMvpService,
        )
        from app.services.data_manager.dream_teams_mvp.infrastructure.dream_teams_mvp_adapter import (
            DreamTeamsMvpAdapter,
        )

        return DreamTeamsMvpService(DreamTeamsMvpAdapter(self)).save_dream_team_mvp(
            championship_id, round_id, matchday, dream_team_players,
            mvp_player_id=mvp_player_id, player_details=player_details
        )

    def save_pressroom_news(self, championship_id: str, news_items: List[Dict]):
        """Save pressroom news (kept for compatibility but not in optimized schema)"""
        from app.services.data_manager.news_articles.application.news_articles import NewsArticlesService
        from app.services.data_manager.news_articles.infrastructure.news_articles_adapter import (
            NewsArticlesAdapter,
        )

        return NewsArticlesService(NewsArticlesAdapter(self)).save_pressroom_news(
            championship_id, news_items
        )
    def should_update_cache(self, data_type: str) -> bool:
        """Check if cache should be updated (always true for fresh data in V2)"""
        from app.services.data_manager.sync_metadata_cache.application.sync_metadata_cache import (
            SyncMetadataCacheService,
        )
        from app.services.data_manager.sync_metadata_cache.infrastructure.sync_metadata_cache_adapter import (
            SyncMetadataCacheAdapter,
        )

        return SyncMetadataCacheService(SyncMetadataCacheAdapter(self)).should_update_cache(data_type)

    def get_users_unique_players_stats(self, championship_id: str) -> List[Dict]:
        """Get statistics of unique players aligned by each user/team"""
        from app.services.data_manager.users_stats_evolution.application.users_stats_evolution import (
            UsersStatsEvolutionService,
        )
        from app.services.data_manager.users_stats_evolution.infrastructure.users_stats_evolution_adapter import (
            UsersStatsEvolutionAdapter,
        )

        return UsersStatsEvolutionService(UsersStatsEvolutionAdapter(self)).get_users_unique_players_stats(
            championship_id
        )

    def get_all_players_with_points(self, championship_id: str) -> List[Dict]:
        """Get all players with their total points"""
        from app.services.data_manager.players.application.players import PlayersService
        from app.services.data_manager.players.infrastructure.players_adapter import (
            PlayersAdapter,
        )

        return PlayersService(PlayersAdapter(self)).get_all_players_with_points(championship_id)

    def get_all_player_transactions(self, championship_id: str) -> Dict[str, List[Dict]]:
        """Get all transactions grouped by player_id"""
        from app.services.data_manager.transactions.application.transactions import (
            TransactionsService,
        )
        from app.services.data_manager.transactions.infrastructure.transactions_adapter import (
            TransactionsAdapter,
        )

        return TransactionsService(TransactionsAdapter(self)).get_all_player_transactions(championship_id)

    def get_all_users_with_points(self, championship_id: str) -> List[Dict]:
        """Get all users/teams with their total points from team standings"""
        from app.services.data_manager.users_stats_evolution.application.users_stats_evolution import (
            UsersStatsEvolutionService,
        )
        from app.services.data_manager.users_stats_evolution.infrastructure.users_stats_evolution_adapter import (
            UsersStatsEvolutionAdapter,
        )

        return UsersStatsEvolutionService(UsersStatsEvolutionAdapter(self)).get_all_users_with_points(championship_id)

    def get_user_transactions(self, championship_id: str, user_id: str = None) -> Dict[str, Dict]:
        """Get all transactions grouped by user_id/team_id (buyer and seller)"""
        from app.services.data_manager.transactions.application.transactions import (
            TransactionsService,
        )
        from app.services.data_manager.transactions.infrastructure.transactions_adapter import (
            TransactionsAdapter,
        )

        return TransactionsService(TransactionsAdapter(self)).get_user_transactions(championship_id, user_id=user_id)

    def get_evolution_data_from_db(self, championship_id: str) -> Dict:
        """Get evolution data (points and positions per matchday) from database"""
        from app.services.data_manager.users_stats_evolution.application.users_stats_evolution import (
            UsersStatsEvolutionService,
        )
        from app.services.data_manager.users_stats_evolution.infrastructure.users_stats_evolution_adapter import (
            UsersStatsEvolutionAdapter,
        )

        return UsersStatsEvolutionService(UsersStatsEvolutionAdapter(self)).get_evolution_data_from_db(championship_id)

    def get_matchday_data_for_news(self, championship_id: str, matchday: int) -> Dict:
        """Get comprehensive matchday data for generating press news"""
        from app.services.data_manager.news_articles.application.news_articles import NewsArticlesService
        from app.services.data_manager.news_articles.infrastructure.news_articles_adapter import (
            NewsArticlesAdapter,
        )

        return NewsArticlesService(NewsArticlesAdapter(self)).get_matchday_data_for_news(
            championship_id, matchday
        )
    def get_dream_team_bonus_stats(self, championship_id: str) -> Dict[str, Dict[str, int]]:
        """Return counts of dream-team appearances and MVP awards per team."""
        from app.services.data_manager.dream_teams_mvp.application.dream_teams_mvp import (
            DreamTeamsMvpService,
        )
        from app.services.data_manager.dream_teams_mvp.infrastructure.dream_teams_mvp_adapter import (
            DreamTeamsMvpAdapter,
        )

        return DreamTeamsMvpService(DreamTeamsMvpAdapter(self)).get_dream_team_bonus_stats(
            championship_id
        )

    def _ensure_schema_updates(self):
        """Ensure new tables/indexes exist without requiring a full reset."""
        from app.services.data_manager.schema_lifecycle.application.schema_lifecycle import (
            SchemaLifecycleService,
        )
        from app.services.data_manager.schema_lifecycle.infrastructure.schema_lifecycle_adapter import (
            SchemaLifecycleAdapter,
        )

        return SchemaLifecycleService(SchemaLifecycleAdapter(self)).ensure_schema_updates()

    def save_player_championship_stats(self, championship_id: str, player_stats: List[Dict]):
        """Persist clause and average metrics for players in a championship (batch)."""
        from app.services.data_manager.players.application.players import PlayersService
        from app.services.data_manager.players.infrastructure.players_adapter import (
            PlayersAdapter,
        )

        return PlayersService(PlayersAdapter(self)).save_player_championship_stats(
            championship_id, player_stats
        )

    def get_clausulable_player_stats(self, championship_id: str) -> List[Dict]:
        """Retrieve stored clause metrics for clausulable player ranking."""
        from app.services.data_manager.clauses.application.clauses import ClausesService
        from app.services.data_manager.clauses.infrastructure.clauses_adapter import (
            ClausesAdapter,
        )

        return ClausesService(ClausesAdapter(self)).get_clausulable_player_stats(championship_id)

    def save_match_odds(self, championship_id: str, matches: List[Dict], round_id: str = None, matchday: int = None):
        """Persist betting odds for upcoming matches"""
        from app.services.data_manager.match_odds.application.match_odds import MatchOddsService
        from app.services.data_manager.match_odds.infrastructure.match_odds_adapter import (
            MatchOddsAdapter,
        )

        return MatchOddsService(MatchOddsAdapter(self)).save_match_odds(
            championship_id, matches, round_id=round_id, matchday=matchday
        )
    def get_match_odds(self, championship_id: str, matchday: Optional[int] = None, upcoming_only: bool = False) -> List[Dict]:
        """Retrieve stored match odds, optionally filtered by matchday or future date"""
        from app.services.data_manager.match_odds.application.match_odds import MatchOddsService
        from app.services.data_manager.match_odds.infrastructure.match_odds_adapter import (
            MatchOddsAdapter,
        )

        return MatchOddsService(MatchOddsAdapter(self)).get_match_odds(
            championship_id, matchday=matchday, upcoming_only=upcoming_only
        )
    def get_latest_matchday(self, championship_id: str) -> Optional[int]:
        """Return the latest matchday available in team_standings"""
        from app.services.data_manager.teams_standings.application.teams_standings import (
            TeamsStandingsService,
        )
        from app.services.data_manager.teams_standings.infrastructure.teams_standings_adapter import (
            TeamsStandingsAdapter,
        )

        return TeamsStandingsService(TeamsStandingsAdapter(self)).get_latest_matchday(championship_id)

    def get_team_standings_history(self, championship_id: str, window: Optional[int] = None) -> List[Dict]:
        """Return standings history for each team, optionally limited to last `window` matchdays"""
        from app.services.data_manager.teams_standings.application.teams_standings import (
            TeamsStandingsService,
        )
        from app.services.data_manager.teams_standings.infrastructure.teams_standings_adapter import (
            TeamsStandingsAdapter,
        )

        return TeamsStandingsService(TeamsStandingsAdapter(self)).get_team_standings_history(
            championship_id, window=window
        )

    def get_prizes_by_team(self, championship_id: str) -> Dict[str, Dict[str, int]]:
        """Return accumulated prizes per team_id from the team_prizes table."""
        from app.services.data_manager.prizes.application.prizes import PrizesReadService
        from app.services.data_manager.prizes.infrastructure.prizes_adapter import (
            PrizesReadAdapter,
        )

        return PrizesReadService(PrizesReadAdapter(self)).get_prizes_by_team(championship_id)

    def get_player_performance_history(self, championship_id: str, player_ids: Optional[List[str]] = None,
                                        window: Optional[int] = None) -> List[Dict]:
        """Return player performance records filtered by players and limited matchdays"""
        from app.services.data_manager.performance.application.performance import PerformanceService
        from app.services.data_manager.performance.infrastructure.performance_adapter import (
            PerformanceAdapter,
        )

        return PerformanceService(PerformanceAdapter(self)).get_player_performance_history(
            championship_id, player_ids=player_ids, window=window
        )
    def get_transactions_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        """Return raw transactions optionally filtered by recent days"""
        from app.services.data_manager.transactions.application.transactions import (
            TransactionsService,
        )
        from app.services.data_manager.transactions.infrastructure.transactions_adapter import (
            TransactionsAdapter,
        )

        return TransactionsService(TransactionsAdapter(self)).get_transactions_raw(championship_id, days=days)

    def get_clauses_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        """Return raw clause payments"""
        from app.services.data_manager.clauses.application.clauses import ClausesService
        from app.services.data_manager.clauses.infrastructure.clauses_adapter import (
            ClausesAdapter,
        )

        return ClausesService(ClausesAdapter(self)).get_clauses_raw(championship_id, days=days)

    def get_team_by_id(self, team_id: str) -> Optional[Dict]:
        """Return a team row by id, or None."""
        from app.services.data_manager.teams_standings.application.teams_standings import (
            TeamsStandingsService,
        )
        from app.services.data_manager.teams_standings.infrastructure.teams_standings_adapter import (
            TeamsStandingsAdapter,
        )

        return TeamsStandingsService(TeamsStandingsAdapter(self)).get_team_by_id(team_id)

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Return a user row by id, or None."""
        from app.services.data_manager.users_stats_evolution.application.users_stats_evolution import (
            UsersStatsEvolutionService,
        )
        from app.services.data_manager.users_stats_evolution.infrastructure.users_stats_evolution_adapter import (
            UsersStatsEvolutionAdapter,
        )

        return UsersStatsEvolutionService(UsersStatsEvolutionAdapter(self)).get_user_by_id(user_id)

    def get_player_by_id(self, player_id: str) -> Optional[Dict]:
        """Return a player row by id, or None."""
        from app.services.data_manager.players.application.players import PlayersService
        from app.services.data_manager.players.infrastructure.players_adapter import (
            PlayersAdapter,
        )

        return PlayersService(PlayersAdapter(self)).get_player_by_id(player_id)

    def get_free_agent_candidates(self, championship_id: str) -> List[Dict]:
        """Return players without owner based on player_championship_stats"""
        from app.services.data_manager.market_roster.application.market_roster import (
            MarketRosterService,
        )
        from app.services.data_manager.market_roster.infrastructure.market_roster_adapter import (
            MarketRosterAdapter,
        )

        return MarketRosterService(MarketRosterAdapter(self)).get_free_agent_candidates(
            championship_id
        )

    def get_player_streak_data(self, championship_id: str, min_matchday: Optional[int] = None) -> List[Dict]:
        """Return player performance ordered by matchday for streak calculations"""
        from app.services.data_manager.teams_standings.application.teams_standings import (
            TeamsStandingsService,
        )
        from app.services.data_manager.teams_standings.infrastructure.teams_standings_adapter import (
            TeamsStandingsAdapter,
        )

        return TeamsStandingsService(TeamsStandingsAdapter(self)).get_player_streak_data(
            championship_id, min_matchday=min_matchday
        )
