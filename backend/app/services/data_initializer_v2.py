"""
Data Initializer V2 - Optimized for Historical Championship Analysis

Uses DataManagerV2 to populate database with optimized schema for historical statistics.
"""

import logging
import time
from typing import Dict
from datetime import datetime

import os
from app.core.config import CHAMPIONSHIP_ID, REQUEST_DELAY_SECONDS, FUTMONDO_EMAIL, FUTMONDO_PASSWORD
from app.services.futmondo_client import FutmondoClient
from app.services.data_manager_v2 import DataManagerV2
from app.services.photo_service import PhotoService

logger = logging.getLogger(__name__)


class DataInitializerV2:
    """Service to initialize database with optimized schema for historical analysis"""
    
    def __init__(self):
        self.client = FutmondoClient(
            email=FUTMONDO_EMAIL,
            password=FUTMONDO_PASSWORD
        )
        self.data_manager = DataManagerV2(skip_init=True)
        self.photo_service = PhotoService()
        self.championship_id = CHAMPIONSHIP_ID
    
    def initialize_all_data(self, force_refresh: bool = False) -> Dict[str, bool]:
        """Initialize all data using optimized schema
        
        Args:
            force_refresh: If True, bypasses cache and fetches fresh data
            
        Returns:
            Dictionary with status of each data fetch operation
        """
        results = {}
        
        # Ensure authenticated
        if not self.client.is_authenticated():
            logger.info("Logging in...")
            if not self.client.login():
                logger.error("Failed to authenticate")
                return {"error": "Authentication failed"}
        
        logger.info("🚀 Starting data initialization with optimized schema...")
        
        # 1. Save championship metadata
        logger.info("\n📋 Step 1: Saving championship metadata...")
        try:
            with self.data_manager.db.get_connection() as conn:
                cursor = self.data_manager.db.get_cursor(conn)
                sql = '''
                    INSERT INTO championships (championship_id, name, created_at)
                    VALUES (?, ?, ?)
                '''
                sql = self.data_manager.db.adapt_params(sql)
                
                if self.data_manager.db.db_type in ["postgresql", "postgres"]:
                    sql = '''
                        INSERT INTO championships (championship_id, name, created_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (championship_id) DO NOTHING
                    '''
                else:
                    sql = '''
                        INSERT OR IGNORE INTO championships (championship_id, name, created_at)
                        VALUES (?, ?, ?)
                    '''
                    sql = self.data_manager.db.adapt_params(sql)
                
                cursor.execute(sql, (self.championship_id, f"Championship {self.championship_id}", datetime.now()))
            
            results["championship"] = True
            logger.info("✅ Championship metadata saved")
        except Exception as e:
            logger.error(f"❌ Error saving championship: {e}")
            results["championship"] = False
        
        time.sleep(REQUEST_DELAY_SECONDS)
        
        # 2. Fetch and save players
        logger.info("\n📋 Step 2: Fetching championship players...")
        try:
            players = self.client.get_championship_players(self.championship_id)
            if players:
                self.data_manager.save_players(players)
                results["players"] = True
                logger.info(f"✅ Saved {len(players)} players")
            else:
                results["players"] = False
        except Exception as e:
            logger.error(f"❌ Error fetching players: {e}")
            results["players"] = False
        
        time.sleep(REQUEST_DELAY_SECONDS)
        
        # 3. Fetch and save teams
        logger.info("\n🏆 Step 3: Fetching championship teams...")
        try:
            standings = self.client.get_matchday_standings(self.championship_id)
            if standings and "teams" in standings:
                teams = standings["teams"]
                for team in teams:
                    team_data = team.get("team", team)
                    team_id = team_data.get("id") or team.get("id")
                    team_name = team_data.get("name") or team.get("name", "Unknown")
                    user_data = team.get("user", {})
                    user_id = user_data.get("id") or team.get("userId")
                    owner_name = user_data.get("name") or team.get("userName", "")
                    
                    if team_id:
                        self.data_manager.save_team(
                            team_id=team_id,
                            team_name=team_name,
                            user_id=user_id or "",
                            owner_name=owner_name,
                            current_points=team.get("points", 0),
                            team_value=team.get("value", 0)
                        )
                
                results["teams"] = True
                logger.info(f"✅ Saved {len(teams)} teams")
            else:
                results["teams"] = False
        except Exception as e:
            logger.error(f"❌ Error fetching teams: {e}")
            results["teams"] = False
        
        time.sleep(REQUEST_DELAY_SECONDS)
        
        # 4. Fetch round rankings (historical standings)
        logger.info("\n📊 Step 4: Fetching round rankings (historical standings)...")
        try:
            max_rounds = 38
            rounds_fetched = 0
            
            for round_num in range(1, max_rounds + 1):
                ranking = self.client.get_round_ranking(self.championship_id, round_num)
                if ranking:
                    if isinstance(ranking, dict):
                        teams = ranking.get("answer", {}).get("teams", [])
                        if not teams:
                            teams = ranking.get("teams", [])
                    elif isinstance(ranking, list):
                        teams = ranking
                    else:
                        teams = []
                    
                    if teams:
                        self.data_manager.save_round_ranking(round_num, self.championship_id, teams)
                        rounds_fetched += 1
                        time.sleep(REQUEST_DELAY_SECONDS)
                    else:
                        break
                else:
                    break
            
            results["round_rankings"] = rounds_fetched > 0
            logger.info(f"✅ Fetched {rounds_fetched} round rankings")
        except Exception as e:
            logger.error(f"❌ Error fetching round rankings: {e}")
            results["round_rankings"] = False
        
        time.sleep(REQUEST_DELAY_SECONDS)
        
        # 5. Fetch player transactions
        logger.info("\n💸 Step 5: Fetching player transactions...")
        try:
            players = self.client.get_championship_players(self.championship_id)
            if players:
                traded_players = [p for p in players if p.get("userteamId")]
                processed = 0
                
                for i, player in enumerate(traded_players):
                    if i % 10 == 0:
                        logger.info(f"  Processing player {i+1}/{len(traded_players)}")
                    
                    try:
                        player_summary = self.client.get_player_summary(
                            self.championship_id,
                            player["id"],
                            player["userteamId"]
                        )
                        
                        if player_summary and "owners" in player_summary:
                            self.data_manager.save_player_transactions(
                                player["id"],
                                player_summary["owners"]
                            )
                            processed += 1
                        
                        time.sleep(REQUEST_DELAY_SECONDS)
                    except Exception as e:
                        logger.debug(f"Could not fetch transactions for player {player.get('name', 'Unknown')}: {e}")
                
                results["transactions"] = processed > 0
                logger.info(f"✅ Processed transactions for {processed} players")
            else:
                results["transactions"] = False
        except Exception as e:
            logger.error(f"❌ Error fetching transactions: {e}")
            results["transactions"] = False
        
        time.sleep(REQUEST_DELAY_SECONDS)
        
        # 6. Fetch team rosters (for all teams)
        logger.info("\n👥 Step 6: Fetching team rosters...")
        try:
            standings = self.client.get_matchday_standings(self.championship_id)
            if standings and "teams" in standings:
                teams = standings["teams"]
                rosters_fetched = 0
                
                for team in teams:
                    team_id = team.get("team", {}).get("id") or team.get("id")
                    userteam_id = team.get("user", {}).get("id") or team.get("userId")
                    
                    if userteam_id:
                        try:
                            roster = self.client.get_userteam_roster(self.championship_id, userteam_id)
                            if roster and isinstance(roster, list):
                                # Get current matchday from standings
                                current_matchday = 1  # Default, should be calculated
                                self.data_manager.save_team_roster(
                                    self.championship_id,
                                    team_id or userteam_id,
                                    roster,
                                    current_matchday
                                )
                                rosters_fetched += 1
                                time.sleep(REQUEST_DELAY_SECONDS)
                        except Exception as e:
                            logger.debug(f"Could not fetch roster for team {team_id}: {e}")
                
                results["rosters"] = rosters_fetched > 0
                logger.info(f"✅ Fetched {rosters_fetched} team rosters")
            else:
                results["rosters"] = False
        except Exception as e:
            logger.error(f"❌ Error fetching rosters: {e}")
            results["rosters"] = False
        
        time.sleep(REQUEST_DELAY_SECONDS)
        
        # 7. Fetch market players
        logger.info("\n💰 Step 7: Fetching market players...")
        try:
            market_players = self.client.get_market_players(self.championship_id)
            if market_players:
                current_matchday = 1  # Should be calculated
                self.data_manager.save_market_players(
                    self.championship_id,
                    market_players,
                    current_matchday
                )
                results["market_players"] = True
                logger.info(f"✅ Saved {len(market_players)} market players")
            else:
                results["market_players"] = False
        except Exception as e:
            logger.error(f"❌ Error fetching market players: {e}")
            results["market_players"] = False
        
        logger.info("\n✅ Data initialization complete!")
        logger.info(f"Results: {results}")
        
        return results

