#!/usr/bin/env python3
"""
Data Manager - Handles data persistence and caching
"""

import json
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from app.core.config import CACHE_DURATION_HOURS, DATABASE_PATH
from app.services.db_connection import DBConnection

logger = logging.getLogger(__name__)

@dataclass
class PlayerData:
    """Player data structure"""
    id: str
    name: str
    role: str
    team: str
    current_value: int
    current_points: int
    userteam_id: Optional[str] = None
    userteam_name: Optional[str] = None
    average_performance: Optional[Dict] = None
    last_updated: Optional[str] = None
    photo: Optional[str] = None  # Photo filename or URL
    slug: Optional[str] = None  # Player slug

@dataclass
class UserData:
    """User data structure"""
    id: str = ""  # UUID-based ID
    username: str = ""
    team_id: str = ""  # Team ID from Futmondo API
    team_name: str = ""  # Team name for display
    last_updated: str = ""

@dataclass
class TransactionData:
    """Individual transaction data structure"""
    id: int = 0  # Auto-increment primary key
    player_id: str = ""
    seller_user_id: str = ""
    buyer_user_id: str = ""
    seller_team_id: str = ""  # Team ID from Futmondo API
    buyer_team_id: str = ""   # Team ID from Futmondo API
    price: int = 0
    date: str = ""
    transaction_type: str = ""  # "TRADE"

@dataclass
class UserProfitData:
    """User profit analysis data"""
    user_id: str
    username: str
    team_id: str
    team_name: str
    total_profit: float
    total_transactions: int
    successful_trades: int
    failed_trades: int
    best_profit: float
    worst_loss: float
    avg_profit_per_trade: float
    profit_percentage: float

class DataManager:
    """Manages data persistence and caching"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self.cache_duration = timedelta(hours=CACHE_DURATION_HOURS)
        self.db = DBConnection()
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables (SQLite or PostgreSQL)"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                team_id TEXT,
                team_name TEXT,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # Players table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                team TEXT NOT NULL,
                current_value INTEGER NOT NULL,
                current_points INTEGER NOT NULL,
                userteam_id TEXT,
                userteam_name TEXT,
                average_performance TEXT,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # Transactions table - stores individual trades with user IDs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                seller_user_id TEXT NOT NULL,
                buyer_user_id TEXT NOT NULL,
                seller_team_id TEXT,
                buyer_team_id TEXT,
                price INTEGER NOT NULL,
                date TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players (id),
                FOREIGN KEY (seller_user_id) REFERENCES users (id),
                FOREIGN KEY (buyer_user_id) REFERENCES users (id)
            )
        ''')
        
        # User profits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profits (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                team_id TEXT,
                team_name TEXT,
                total_profit REAL NOT NULL,
                total_transactions INTEGER NOT NULL,
                successful_trades INTEGER NOT NULL,
                failed_trades INTEGER NOT NULL,
                best_profit REAL NOT NULL,
                worst_loss REAL NOT NULL,
                avg_profit_per_trade REAL NOT NULL,
                profit_percentage REAL NOT NULL,
                last_updated TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Cache metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_metadata (
                data_type TEXT PRIMARY KEY,
                last_updated TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        ''')
        
        # Teams table - extended team information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_id TEXT PRIMARY KEY,
                user_id TEXT,
                team_name TEXT NOT NULL,
                owner_name TEXT,
                current_points INTEGER,
                team_value INTEGER,
                last_access TEXT,
                is_admin BOOLEAN DEFAULT 0,
                initial_budget INTEGER DEFAULT 270000000,
                last_updated TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Team matchday data - stores historical matchday data with best player
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_matchday_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matchday INTEGER NOT NULL,
                team_id TEXT NOT NULL,
                points INTEGER NOT NULL,
                position INTEGER NOT NULL,
                points_this_matchday INTEGER,
                best_player_id TEXT,
                best_player_points INTEGER,
                saved_at TEXT NOT NULL,
                UNIQUE(matchday, team_id),
                FOREIGN KEY (team_id) REFERENCES teams (team_id),
                FOREIGN KEY (best_player_id) REFERENCES players (id)
            )
        ''')
        
        # Player matchday performance - player points per matchday per team
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_matchday_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                matchday INTEGER NOT NULL,
                points INTEGER NOT NULL,
                value INTEGER,
                was_best_player BOOLEAN DEFAULT 0,
                saved_at TEXT NOT NULL,
                UNIQUE(player_id, team_id, matchday),
                FOREIGN KEY (player_id) REFERENCES players (id),
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        ''')
        
        # Player photos - downloaded photos management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_photos (
                player_id TEXT PRIMARY KEY,
                photo_url TEXT,
                local_path TEXT NOT NULL,
                downloaded_at TEXT NOT NULL,
                file_size INTEGER,
                file_hash TEXT,
                last_checked TEXT,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        # Update players table to include photo fields
        try:
            cursor.execute('ALTER TABLE players ADD COLUMN photo_url TEXT')
        except Exception:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE players ADD COLUMN photo_local_path TEXT')
        except Exception:
            pass  # Column already exists
        
        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_team_matchday_data_matchday 
            ON team_matchday_data(matchday)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_team_matchday_data_team 
            ON team_matchday_data(team_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_player_matchday_performance_matchday 
            ON player_matchday_performance(matchday)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_player_matchday_performance_team 
            ON player_matchday_performance(team_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_player_matchday_performance_player 
            ON player_matchday_performance(player_id)
        ''')
        
        # Update cache_metadata to include next_update_scheduled
        try:
            cursor.execute('ALTER TABLE cache_metadata ADD COLUMN next_update_scheduled TEXT')
        except Exception:
            pass  # Column already exists
        
        # Round rankings - rankings por jornada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS round_rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round INTEGER NOT NULL,
                championship_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                points INTEGER NOT NULL,
                previous_position INTEGER,
                position_change INTEGER,
                saved_at TEXT NOT NULL,
                UNIQUE(round, championship_id, team_id),
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        ''')
        
        # Market players - jugadores en el mercado
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                championship_id TEXT NOT NULL,
                market_price INTEGER,
                availability TEXT,
                market_statistics TEXT,
                saved_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                UNIQUE(player_id, championship_id),
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        # Pressroom news - noticias y actualizaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pressroom_news (
                id TEXT PRIMARY KEY,
                championship_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                news_date TEXT NOT NULL,
                news_type TEXT,
                related_teams TEXT,
                related_players TEXT,
                image_url TEXT,
                saved_at TEXT NOT NULL
            )
        ''')
        
        # Team rosters - rosters detallados por equipo (mejorar estructura existente)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_rosters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                championship_id TEXT NOT NULL,
                formation_position TEXT,
                is_starter BOOLEAN DEFAULT 0,
                lineup_order INTEGER,
                saved_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                UNIQUE(team_id, player_id, championship_id),
                FOREIGN KEY (team_id) REFERENCES teams (team_id),
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        # Player matchday stats - estadísticas detalladas por jugador y jornada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_matchday_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                matchday INTEGER NOT NULL,
                championship_id TEXT NOT NULL,
                points INTEGER NOT NULL,
                value INTEGER,
                performance_data TEXT,
                saved_at TEXT NOT NULL,
                UNIQUE(player_id, team_id, matchday, championship_id),
                FOREIGN KEY (player_id) REFERENCES players (id),
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        ''')
        
        # Create indexes for new tables (must be after table creation)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_round_rankings_round 
            ON round_rankings(round)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_round_rankings_team 
            ON round_rankings(team_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_market_players_player 
            ON market_players(player_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_market_players_championship 
            ON market_players(championship_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pressroom_news_championship 
            ON pressroom_news(championship_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pressroom_news_date 
            ON pressroom_news(news_date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_team_rosters_team 
            ON team_rosters(team_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_team_rosters_player 
            ON team_rosters(player_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_player_matchday_stats_matchday 
            ON player_matchday_stats(matchday)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_player_matchday_stats_player 
            ON player_matchday_stats(player_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_player_matchday_stats_team 
            ON player_matchday_stats(team_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def is_cache_valid(self, data_type: str) -> bool:
        """Check if cached data is still valid"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute(
            "SELECT expires_at FROM cache_metadata WHERE data_type = ?",
            (data_type,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
        
        expires_at = datetime.fromisoformat(result[0])
        return datetime.now() < expires_at
    
    def update_cache_metadata(self, data_type: str):
        """Update cache metadata with current timestamp and schedule next daily update"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        now = datetime.now()
        expires_at = now + self.cache_duration
        # Schedule next update for next day at the same time (24 hours)
        next_update = now + timedelta(days=1)
        
        cursor.execute('''
            INSERT OR REPLACE INTO cache_metadata 
            (data_type, last_updated, expires_at, next_update_scheduled)
            VALUES (?, ?, ?, ?)
        ''', (data_type, now.isoformat(), expires_at.isoformat(), next_update.isoformat()))
        
        conn.commit()
        conn.close()
    
    def should_update_cache(self, data_type: str) -> bool:
        """Check if cache should be updated (once per day)"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute('''
            SELECT next_update_scheduled FROM cache_metadata WHERE data_type = ?
        ''', (data_type,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return True  # No cache, need to update
        
        try:
            next_update = datetime.fromisoformat(result[0])
            return datetime.now() >= next_update
        except (ValueError, TypeError):
            return True  # Invalid date, need to update
    
    def save_players(self, players: List[Dict]):
        """Save players data to database"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        # Clear existing players data
        cursor.execute("DELETE FROM players")
        cursor.execute("DELETE FROM transactions")
        
        now = datetime.now().isoformat()
        
        for player in players:
            # Extract photo URL - construct full URL if needed
            photo_filename = player.get("photo", "")
            photo_url = None
            if photo_filename:
                # Construct full URL from filename
                # Format: https://static01.mondocore.com/futmondo/img/faces/64/{photo}
                PHOTO_BASE_URL = "https://static01.mondocore.com/futmondo/img/faces/64"
                if photo_filename.startswith('http'):
                    photo_url = photo_filename
                elif photo_filename.startswith('/'):
                    photo_url = f"https://static01.mondocore.com{photo_filename}"
                elif '.' in photo_filename:
                    photo_url = f"{PHOTO_BASE_URL}/{photo_filename}"
            
            player_data = PlayerData(
                id=player["id"],
                name=player["name"],
                role=player["role"],
                team=player.get("team", "Unknown"),
                current_value=player["value"],
                current_points=player["points"],
                userteam_id=player.get("userteamId"),
                userteam_name=player.get("userteam"),
                average_performance=json.dumps(player.get("average", {})),
                last_updated=now,
                photo=photo_filename,  # Original photo filename
                slug=player.get("slug", "")
            )
            
            cursor.execute('''
                INSERT INTO players (id, name, role, team, current_value, current_points,
                                   userteam_id, userteam_name, average_performance, last_updated,
                                   photo_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player_data.id, player_data.name, player_data.role, player_data.team,
                player_data.current_value, player_data.current_points,
                player_data.userteam_id, player_data.userteam_name,
                player_data.average_performance, player_data.last_updated,
                photo_url  # Store full URL in photo_url column
            ))
            
            # Process photo if available (download and save)
            if photo_url:
                try:
                    from app.services.photo_service import PhotoService
                    photo_service = PhotoService()
                    local_path = photo_service.process_player_photo(player, player_data.id)
                    if local_path:
                        # Update with local path
                        cursor.execute('''
                            UPDATE players SET photo_local_path = ? WHERE id = ?
                        ''', (local_path, player_data.id))
                except Exception as e:
                    logger.debug(f"Could not process photo for player {player_data.id}: {e}")
        
        conn.commit()
        conn.close()
        
        self.update_cache_metadata("players")
        logger.info(f"Saved {len(players)} players to database")
    
    def get_players(self) -> List[PlayerData]:
        """Get all players from database"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute("SELECT * FROM players")
        rows = cursor.fetchall()
        conn.close()
        
        players = []
        for row in rows:
            player = PlayerData(
                id=row[0], name=row[1], role=row[2], team=row[3],
                current_value=row[4], current_points=row[5],
                userteam_id=row[6], userteam_name=row[7],
                average_performance=json.loads(row[8]) if row[8] else None,
                last_updated=row[9]
            )
            players.append(player)
        
        return players
    
    def save_user(self, user_data: UserData):
        """Save or update user data"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (id, username, team_id, team_name, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_data.id, user_data.username, user_data.team_id,
            user_data.team_name, user_data.last_updated
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[UserData]:
        """Get user by username"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserData(
                id=row[0], username=row[1], team_id=row[2] or "",
                team_name=row[3] or "", last_updated=row[4]
            )
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserData]:
        """Get user by ID"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserData(
                id=row[0], username=row[1], team_id=row[2] or "",
                team_name=row[3] or "", last_updated=row[4]
            )
        return None
    
    def get_or_create_user(self, username: str, team_id: str = "", team_name: str = "") -> UserData:
        """Get existing user or create new one with proper UUID"""
        existing_user = self.get_user_by_username(username)
        if existing_user:
            return existing_user
        
        # Create new user with proper UUID
        user_id = str(uuid.uuid4())
        new_user = UserData(
            id=user_id,
            username=username,
            team_id=team_id,
            team_name=team_name,
            last_updated=datetime.now().isoformat()
        )
        
        self.save_user(new_user)
        return new_user
    
    def save_player_transactions(self, player_id: str, owners_history: List[Dict]):
        """Save player transaction data as individual trades (one record per trade)"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        # Clear existing transactions for this player
        cursor.execute("DELETE FROM transactions WHERE player_id = ?", (player_id,))
        
        if len(owners_history) < 2:
            # If less than 2 owners, we can't determine trades
            conn.close()
            return
        
        # Helper function to get or create user within the same transaction
        def get_or_create_user_in_transaction(username: str, team_id: str = "", team_name: str = "") -> str:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return row[0]
            
            # Create new user with UUID
            user_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO users (id, username, team_id, team_name, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, team_id, team_name, datetime.now().isoformat()))
            return user_id
        
        # Process owners history to create individual trade records
        for i in range(len(owners_history)):
            current_owner = owners_history[i]
            current_username = current_owner.get("n", "Unknown")
            current_price = current_owner.get("p", 0)
            current_date = current_owner.get("d", "")
            
            # Try to get team ID if available (this might not be in the API response)
            current_team_id = current_owner.get("team_id", "")
            
            if i == 0:
                # First transaction: Initial purchase from market
                market_user_id = get_or_create_user_in_transaction("Market", "", "Market")
                buyer_user_id = get_or_create_user_in_transaction(current_username, current_team_id, current_username)
                
                cursor.execute('''
                    INSERT INTO transactions (player_id, seller_user_id, buyer_user_id, 
                                           seller_team_id, buyer_team_id, price, date, transaction_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player_id, market_user_id, buyer_user_id,
                    "", current_team_id, current_price, current_date, "TRADE"
                ))
            else:
                # Subsequent transactions: Trade between users
                previous_owner = owners_history[i-1]
                previous_username = previous_owner.get("n", "Unknown")
                previous_team_id = previous_owner.get("team_id", "")
                
                seller_user_id = get_or_create_user_in_transaction(previous_username, previous_team_id, previous_username)
                buyer_user_id = get_or_create_user_in_transaction(current_username, current_team_id, current_username)
                
                # Store one record per trade with seller and buyer user IDs
                cursor.execute('''
                    INSERT INTO transactions (player_id, seller_user_id, buyer_user_id, 
                                           seller_team_id, buyer_team_id, price, date, transaction_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player_id, seller_user_id, buyer_user_id,
                    previous_team_id, current_team_id, current_price, current_date, "TRADE"
                ))
        
        conn.commit()
        conn.close()
    
    def get_player_transactions(self, player_id: str) -> List[TransactionData]:
        """Get transactions for a specific player"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute('''
            SELECT id, player_id, seller_user_id, buyer_user_id, 
                   seller_team_id, buyer_team_id, price, date, transaction_type
            FROM transactions
            WHERE player_id = ?
            ORDER BY date
        ''', (player_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transaction = TransactionData(
                id=row[0],
                player_id=row[1],
                seller_user_id=row[2],
                buyer_user_id=row[3],
                seller_team_id=row[4] or "",
                buyer_team_id=row[5] or "",
                price=row[6],
                date=row[7],
                transaction_type=row[8]
            )
            transactions.append(transaction)
        
        return transactions
    
    def save_user_profits(self, user_profits: List[UserProfitData]):
        """Save user profit analysis data"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        # Clear existing user profits
        cursor.execute("DELETE FROM user_profits")
        
        now = datetime.now().isoformat()
        
        for user_profit in user_profits:
            cursor.execute('''
                INSERT INTO user_profits (user_id, username, team_id, team_name, total_profit, total_transactions,
                                        successful_trades, failed_trades, best_profit,
                                        worst_loss, avg_profit_per_trade, profit_percentage, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_profit.user_id, user_profit.username, user_profit.team_id, user_profit.team_name,
                user_profit.total_profit, user_profit.total_transactions, user_profit.successful_trades,
                user_profit.failed_trades, user_profit.best_profit,
                user_profit.worst_loss, user_profit.avg_profit_per_trade,
                user_profit.profit_percentage, now
            ))
        
        conn.commit()
        conn.close()
        
        self.update_cache_metadata("user_profits")
        logger.info(f"Saved {len(user_profits)} user profit records to database")
    
    def get_user_profits(self) -> List[UserProfitData]:
        """Get all user profit data from database"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute("SELECT * FROM user_profits ORDER BY total_profit DESC")
        rows = cursor.fetchall()
        conn.close()
        
        user_profits = []
        for row in rows:
            user_profit = UserProfitData(
                user_id=row[0], username=row[1], team_id=row[2] or "", team_name=row[3] or "",
                total_profit=row[4], total_transactions=row[5],
                successful_trades=row[6], failed_trades=row[7], best_profit=row[8],
                worst_loss=row[9], avg_profit_per_trade=row[10], profit_percentage=row[11]
            )
            user_profits.append(user_profit)
        
        return user_profits
    
    def save_matchday_data(self, matchday: int, teams: List[Dict]):
        """Save matchday standings data"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        # Sort teams by points (descending) to calculate position
        sorted_teams = sorted(teams, key=lambda x: x.get("points", 0), reverse=True)
        
        now = datetime.now().isoformat()
        
        for position, team in enumerate(sorted_teams, start=1):
            team_id = team.get("id", team.get("teamid", ""))
            username = team.get("name", team.get("teamname", "Unknown"))
            team_name = team.get("teamname", username)
            points = team.get("points", 0)
            
            cursor.execute('''
                INSERT OR REPLACE INTO matchday_data 
                (matchday, team_id, username, team_name, points, position, saved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (matchday, team_id, username, team_name, points, position, now))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved matchday {matchday} data for {len(teams)} teams")
    
    def get_matchday_data(self, matchday: Optional[int] = None) -> List[Dict]:
        """Get matchday data for a specific matchday or all matchdays"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        if matchday:
            cursor.execute('''
                SELECT matchday, team_id, username, team_name, points, position, saved_at
                FROM matchday_data
                WHERE matchday = ?
                ORDER BY position ASC
            ''', (matchday,))
        else:
            cursor.execute('''
                SELECT matchday, team_id, username, team_name, points, position, saved_at
                FROM matchday_data
                ORDER BY matchday ASC, position ASC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        matchday_data = []
        for row in rows:
            matchday_data.append({
                "matchday": row[0],
                "team_id": row[1],
                "username": row[2],
                "team_name": row[3],
                "points": row[4],
                "position": row[5],
                "saved_at": row[6]
            })
        
        return matchday_data
    
    def get_matchday_list(self) -> List[int]:
        """Get list of all matchdays with data"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute('''
            SELECT DISTINCT matchday
            FROM matchday_data
            ORDER BY matchday ASC
        ''')
        
        matchdays = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return matchdays
    
    def get_latest_matchday(self) -> Optional[int]:
        """Get the latest matchday number"""
        matchdays = self.get_matchday_list()
        return max(matchdays) if matchdays else None
    
    def save_round_ranking(self, round_number: int, championship_id: str, teams: List[Dict]):
        """Save round ranking data for a specific round"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        now = datetime.now().isoformat()
        
        # Get previous round ranking for position change calculation
        previous_rankings = {}
        if round_number > 1:
            cursor.execute('''
                SELECT team_id, position FROM round_rankings 
                WHERE round = ? AND championship_id = ?
            ''', (round_number - 1, championship_id))
            for row in cursor.fetchall():
                previous_rankings[row[0]] = row[1]
        
        for team in teams:
            team_id = team.get("id", team.get("teamid", ""))
            position = team.get("position", 0)
            points = team.get("points", 0)
            
            previous_position = previous_rankings.get(team_id)
            position_change = None
            if previous_position:
                position_change = previous_position - position  # Positive = moved up
            
            cursor.execute('''
                INSERT OR REPLACE INTO round_rankings
                (round, championship_id, team_id, position, points, previous_position, position_change, saved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (round_number, championship_id, team_id, position, points, previous_position, position_change, now))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved round {round_number} ranking for {len(teams)} teams")
        self.update_cache_metadata("round_rankings")
    
    def get_round_ranking(self, round_number: int, championship_id: str) -> List[Dict]:
        """Get round ranking for a specific round"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute('''
            SELECT round, team_id, position, points, previous_position, position_change, saved_at
            FROM round_rankings
            WHERE round = ? AND championship_id = ?
            ORDER BY position ASC
        ''', (round_number, championship_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        rankings = []
        for row in rows:
            rankings.append({
                "round": row[0],
                "team_id": row[1],
                "position": row[2],
                "points": row[3],
                "previous_position": row[4],
                "position_change": row[5],
                "saved_at": row[6]
            })
        
        return rankings
    
    def save_market_players(self, championship_id: str, players: List[Dict]):
        """Save market players data"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        now = datetime.now().isoformat()
        
        for player in players:
            player_id = player.get("id", "")
            if not player_id:
                continue
            
            market_price = player.get("marketPrice", player.get("price", player.get("market_price")))
            availability = player.get("availability", player.get("available", "unknown"))
            market_statistics = json.dumps(player.get("marketStats", player.get("statistics", {})))
            
            cursor.execute('''
                INSERT OR REPLACE INTO market_players
                (player_id, championship_id, market_price, availability, market_statistics, saved_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (player_id, championship_id, market_price, availability, market_statistics, now, now))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(players)} market players")
        self.update_cache_metadata("market_players")
    
    def get_market_players(self, championship_id: str) -> List[Dict]:
        """Get market players for a championship"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute('''
            SELECT player_id, market_price, availability, market_statistics, last_updated
            FROM market_players
            WHERE championship_id = ?
            ORDER BY market_price DESC
        ''', (championship_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        players = []
        for row in rows:
            players.append({
                "player_id": row[0],
                "market_price": row[1],
                "availability": row[2],
                "market_statistics": json.loads(row[3]) if row[3] else {},
                "last_updated": row[4]
            })
        
        return players
    
    def save_pressroom_news(self, championship_id: str, news_items: List[Dict]):
        """Save pressroom news data"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        now = datetime.now().isoformat()
        
        for news in news_items:
            news_id = news.get("id", news.get("_id", ""))
            if not news_id:
                # Generate ID from title and date
                title = news.get("title", "")
                date = news.get("date", news.get("newsDate", ""))
                news_id = f"{championship_id}_{date}_{hash(title)}"
            
            title = news.get("title", "")
            content = news.get("content", news.get("text", ""))
            news_date = news.get("date", news.get("newsDate", datetime.now().isoformat()))
            news_type = news.get("type", news.get("newsType", "general"))
            related_teams = json.dumps(news.get("relatedTeams", news.get("teams", [])))
            related_players = json.dumps(news.get("relatedPlayers", news.get("players", [])))
            image_url = news.get("imageUrl", news.get("image", ""))
            
            cursor.execute('''
                INSERT OR REPLACE INTO pressroom_news
                (id, championship_id, title, content, news_date, news_type, related_teams, related_players, image_url, saved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (news_id, championship_id, title, content, news_date, news_type, related_teams, related_players, image_url, now))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(news_items)} pressroom news items")
        self.update_cache_metadata("pressroom_news")
    
    def get_pressroom_news(self, championship_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get pressroom news for a championship"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        query = '''
            SELECT id, title, content, news_date, news_type, related_teams, related_players, image_url, saved_at
            FROM pressroom_news
            WHERE championship_id = ?
            ORDER BY news_date DESC
        '''
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (championship_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        news_items = []
        for row in rows:
            news_items.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "news_date": row[3],
                "news_type": row[4],
                "related_teams": json.loads(row[5]) if row[5] else [],
                "related_players": json.loads(row[6]) if row[6] else [],
                "image_url": row[7],
                "saved_at": row[8]
            })
        
        return news_items
    
    def save_team_roster(self, team_id: str, championship_id: str, players: List[Dict]):
        """Save team roster data"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        now = datetime.now().isoformat()
        
        # Delete existing roster for this team
        cursor.execute('DELETE FROM team_rosters WHERE team_id = ? AND championship_id = ?', (team_id, championship_id))
        
        for idx, player in enumerate(players):
            player_id = player.get("id", "")
            if not player_id:
                continue
            
            formation_position = player.get("position", player.get("formationPosition", ""))
            is_starter = player.get("isStarter", player.get("starter", True))
            lineup_order = player.get("lineupOrder", player.get("order", idx))
            
            cursor.execute('''
                INSERT INTO team_rosters
                (team_id, player_id, championship_id, formation_position, is_starter, lineup_order, saved_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (team_id, player_id, championship_id, formation_position, is_starter, lineup_order, now, now))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved roster for team {team_id}: {len(players)} players")
        self.update_cache_metadata("team_rosters")
    
    def get_team_roster(self, team_id: str, championship_id: str) -> List[Dict]:
        """Get team roster from database"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        cursor.execute('''
            SELECT player_id, formation_position, is_starter, lineup_order, last_updated
            FROM team_rosters
            WHERE team_id = ? AND championship_id = ?
            ORDER BY lineup_order ASC, is_starter DESC
        ''', (team_id, championship_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        roster = []
        for row in rows:
            roster.append({
                "player_id": row[0],
                "formation_position": row[1],
                "is_starter": bool(row[2]),
                "lineup_order": row[3],
                "last_updated": row[4]
            })
        
        return roster
    
    def save_player_matchday_stats(self, player_id: str, team_id: str, matchday: int, championship_id: str, 
                                   points: int, value: Optional[int] = None, performance_data: Optional[Dict] = None):
        """Save player matchday statistics"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        now = datetime.now().isoformat()
        performance_json = json.dumps(performance_data) if performance_data else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO player_matchday_stats
            (player_id, team_id, matchday, championship_id, points, value, performance_data, saved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (player_id, team_id, matchday, championship_id, points, value, performance_json, now))
        
        conn.commit()
        conn.close()
    
    def get_player_matchday_stats(self, player_id: str, team_id: Optional[str] = None, 
                                  matchday: Optional[int] = None, championship_id: Optional[str] = None) -> List[Dict]:
        """Get player matchday statistics"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        query = "SELECT player_id, team_id, matchday, championship_id, points, value, performance_data, saved_at FROM player_matchday_stats WHERE 1=1"
        params = []
        
        if player_id:
            query += " AND player_id = ?"
            params.append(player_id)
        
        if team_id:
            query += " AND team_id = ?"
            params.append(team_id)
        
        if matchday:
            query += " AND matchday = ?"
            params.append(matchday)
        
        if championship_id:
            query += " AND championship_id = ?"
            params.append(championship_id)
        
        query += " ORDER BY matchday ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        stats = []
        for row in rows:
            stats.append({
                "player_id": row[0],
                "team_id": row[1],
                "matchday": row[2],
                "championship_id": row[3],
                "points": row[4],
                "value": row[5],
                "performance_data": json.loads(row[6]) if row[6] else {},
                "saved_at": row[7]
            })
        
        return stats
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
        
        stats = {}
        
        # Count players
        cursor.execute("SELECT COUNT(*) FROM players")
        stats["total_players"] = cursor.fetchone()[0]
        
        # Count transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        stats["total_transactions"] = cursor.fetchone()[0]
        
        # Count matchdays
        cursor.execute("SELECT COUNT(DISTINCT matchday) FROM matchday_data")
        stats["total_matchdays"] = cursor.fetchone()[0]
        
        # Count users with profit data
        cursor.execute("SELECT COUNT(*) FROM user_profits")
        stats["users_analyzed"] = cursor.fetchone()[0]
        
        # Cache status
        cursor.execute("SELECT data_type, last_updated, expires_at FROM cache_metadata")
        cache_data = cursor.fetchall()
        stats["cache_status"] = {}
        
        for data_type, last_updated, expires_at in cache_data:
            expires = datetime.fromisoformat(expires_at)
            is_valid = datetime.now() < expires
            stats["cache_status"][data_type] = {
                "last_updated": last_updated,
                "expires_at": expires_at,
                "is_valid": is_valid
            }
        
        conn.close()
        return stats
