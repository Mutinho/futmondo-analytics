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
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Helper function to safely drop and create a table
            def drop_and_create_table(table_name, create_sql, description=""):
                try:
                    # SQLite doesn't support CASCADE, PostgreSQL does
                    if self.db.db_type in ["postgresql", "postgres"]:
                        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                    else:
                        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    conn.commit()  # Commit the drop
                    logger.info(f"✅ Dropped {description or table_name} table")
                except Exception as e:
                    logger.warning(f"⚠️ Could not drop {table_name}: {e}")
                    try:
                        conn.rollback()
                    except:
                        pass
                try:
                    cursor.execute(create_sql)
                    conn.commit()  # Commit after creating each table
                    logger.info(f"✅ Created {description or table_name} table")
                except Exception as e:
                    logger.error(f"❌ Error creating {description or table_name} table: {e}")
                    logger.error(f"SQL: {create_sql[:200]}...")  # Log first 200 chars of SQL
                    try:
                        conn.rollback()
                    except:
                        pass
                    raise
            
            # ============================================================
            # DIMENSION TABLES (Reference Data - Changes Rarely)
            # ============================================================
            
            # Users - Championship participants
            sql = self.db.adapt_sql('''
                CREATE TABLE users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            drop_and_create_table("users", sql, "users")
            
            # Teams - User teams in championship
            sql = self.db.adapt_sql('''
                CREATE TABLE teams (
                    team_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    team_name TEXT NOT NULL,
                    initial_budget INTEGER DEFAULT 270000000,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            drop_and_create_table("teams", sql, "teams")
            
            # Players - Football players
            sql = self.db.adapt_sql('''
                CREATE TABLE players (
                    player_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    real_team_id TEXT,
                    real_team_name TEXT,
                    slug TEXT,
                    photo_url TEXT,
                    photo_local_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            drop_and_create_table("players", sql, "players")
            
            # Championships - Championship metadata
            sql = self.db.adapt_sql('''
                CREATE TABLE championships (
                    championship_id TEXT PRIMARY KEY,
                    name TEXT,
                    season_start DATE,
                    season_end DATE,
                    total_matchdays INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            drop_and_create_table("championships", sql, "championships")
            
            # ============================================================
            # FACT TABLES (Time-Series Data - Historical Records)
            # ============================================================
            
            # Team standings - Historical standings per matchday
            sql = self.db.adapt_sql('''
                CREATE TABLE team_standings (
                    id SERIAL PRIMARY KEY,
                    championship_id TEXT NOT NULL,
                    team_id TEXT NOT NULL,
                    matchday INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    points INTEGER NOT NULL,
                    points_this_matchday INTEGER DEFAULT 0,
                    team_value INTEGER,
                    goals_for INTEGER DEFAULT 0,
                    goals_against INTEGER DEFAULT 0,
                    goal_difference INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(championship_id, team_id, matchday),
                    FOREIGN KEY (team_id) REFERENCES teams (team_id),
                    FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
                )
            ''')
            drop_and_create_table("team_standings", sql, "team_standings")
            
            # Player performance - Player points per matchday per team
            sql = self.db.adapt_sql('''
                CREATE TABLE player_performance (
                    id SERIAL PRIMARY KEY,
                    championship_id TEXT NOT NULL,
                    player_id TEXT NOT NULL,
                    team_id TEXT NOT NULL,
                    matchday INTEGER NOT NULL,
                    points INTEGER NOT NULL,
                    value INTEGER,
                    minutes_played INTEGER,
                    goals INTEGER DEFAULT 0,
                    assists INTEGER DEFAULT 0,
                    yellow_cards INTEGER DEFAULT 0,
                    red_cards INTEGER DEFAULT 0,
                    was_starter BOOLEAN DEFAULT false,
                    was_best_player BOOLEAN DEFAULT false,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(championship_id, player_id, team_id, matchday),
                    FOREIGN KEY (player_id) REFERENCES players (player_id),
                    FOREIGN KEY (team_id) REFERENCES teams (team_id),
                    FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
                )
            ''')
            drop_and_create_table("player_performance", sql, "player_performance")
            
            # Transactions - Historical transfer records
            sql = self.db.adapt_sql('''
                CREATE TABLE transactions (
                    transaction_id SERIAL PRIMARY KEY,
                    championship_id TEXT NOT NULL,
                    api_transaction_id TEXT UNIQUE NOT NULL,
                    player_id TEXT NOT NULL,
                    seller_user_id TEXT,
                    buyer_user_id TEXT NOT NULL,
                    seller_team_id TEXT,
                    buyer_team_id TEXT,
                    price INTEGER NOT NULL,
                    transaction_date TIMESTAMP NOT NULL,
                    matchday INTEGER,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (player_id),
                    FOREIGN KEY (seller_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (buyer_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (seller_team_id) REFERENCES teams (team_id),
                    FOREIGN KEY (buyer_team_id) REFERENCES teams (team_id)
                )
            ''')
            drop_and_create_table("transactions", sql, "transactions")
            
            # Punishments and Bonuses - Admin actions (punish/bonus)
            sql = self.db.adapt_sql('''
                CREATE TABLE punishments_bonuses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    championship_id TEXT NOT NULL,
                    news_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    team_id TEXT,
                    user_name TEXT NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('punish', 'bonus')),
                    amount INTEGER NOT NULL,
                    admin_name TEXT,
                    created_date TIMESTAMP NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (team_id) REFERENCES teams (team_id)
                )
            ''')
            drop_and_create_table("punishments_bonuses", sql, "punishments_bonuses")
            
            # Clauses - Player release clauses
            sql = self.db.adapt_sql('''
                CREATE TABLE clauses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    championship_id TEXT NOT NULL,
                    news_id TEXT UNIQUE NOT NULL,
                    payer_user_id TEXT NOT NULL,
                    payer_team_id TEXT,
                    payer_name TEXT NOT NULL,
                    receiver_user_id TEXT NOT NULL,
                    receiver_team_id TEXT,
                    receiver_name TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    created_date TIMESTAMP NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (payer_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (receiver_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (payer_team_id) REFERENCES teams (team_id),
                    FOREIGN KEY (receiver_team_id) REFERENCES teams (team_id)
                )
            ''')
            drop_and_create_table("clauses", sql, "clauses")
            
            # Team rosters - Historical roster changes
            sql = self.db.adapt_sql('''
                CREATE TABLE team_rosters (
                    id SERIAL PRIMARY KEY,
                    championship_id TEXT NOT NULL,
                    team_id TEXT NOT NULL,
                    player_id TEXT NOT NULL,
                    matchday INTEGER NOT NULL,
                    formation_position TEXT,
                    is_starter BOOLEAN DEFAULT false,
                    lineup_order INTEGER,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(championship_id, team_id, player_id, matchday),
                    FOREIGN KEY (team_id) REFERENCES teams (team_id),
                    FOREIGN KEY (player_id) REFERENCES players (player_id),
                    FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
                )
            ''')
            drop_and_create_table("team_rosters", sql, "team_rosters")
            
            # Dream teams and MVPs - Historical dream teams and MVPs per round
            sql = self.db.adapt_sql('''
                CREATE TABLE dream_teams_mvps (
                    id SERIAL PRIMARY KEY,
                    championship_id TEXT NOT NULL,
                    round_id TEXT NOT NULL,
                    matchday INTEGER NOT NULL,
                    player_id TEXT NOT NULL,
                    is_mvp BOOLEAN DEFAULT false,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(championship_id, round_id, player_id, is_mvp),
                    FOREIGN KEY (player_id) REFERENCES players (player_id),
                    FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
                )
            ''')
            drop_and_create_table("dream_teams_mvps", sql, "dream_teams_mvps")
            
            # Sync metadata - Track last sync for each data type
            sql = self.db.adapt_sql('''
                CREATE TABLE sync_metadata (
                    id SERIAL PRIMARY KEY,
                    championship_id TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    last_sync_id TEXT,
                    last_sync_date TIMESTAMP,
                    last_sync_matchday INTEGER,
                    records_synced INTEGER DEFAULT 0,
                    sync_duration_seconds REAL,
                    sync_status TEXT DEFAULT 'success',
                    error_message TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(championship_id, data_type),
                    FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
                )
            ''')
            drop_and_create_table("sync_metadata", sql, "sync_metadata")
            
            # ============================================================
            # INDEXES FOR PERFORMANCE (Critical for Historical Queries)
            # ============================================================
            
            indexes = [
                # Team standings indexes
                "CREATE INDEX IF NOT EXISTS idx_team_standings_championship_matchday ON team_standings(championship_id, matchday)",
                "CREATE INDEX IF NOT EXISTS idx_team_standings_team ON team_standings(team_id)",
                "CREATE INDEX IF NOT EXISTS idx_team_standings_position ON team_standings(position, matchday)",
                "CREATE INDEX IF NOT EXISTS idx_team_standings_recorded_at ON team_standings(recorded_at)",
                
                # Player performance indexes
                "CREATE INDEX IF NOT EXISTS idx_player_performance_championship_matchday ON player_performance(championship_id, matchday)",
                "CREATE INDEX IF NOT EXISTS idx_player_performance_player ON player_performance(player_id)",
                "CREATE INDEX IF NOT EXISTS idx_player_performance_team ON player_performance(team_id)",
                "CREATE INDEX IF NOT EXISTS idx_player_performance_matchday_points ON player_performance(matchday, points)",
                
                # Transaction indexes
                "CREATE INDEX IF NOT EXISTS idx_transactions_player ON transactions(player_id)",
                "CREATE INDEX IF NOT EXISTS idx_transactions_buyer ON transactions(buyer_user_id, transaction_date)",
                "CREATE INDEX IF NOT EXISTS idx_transactions_seller ON transactions(seller_user_id, transaction_date)",
                "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)",
                "CREATE INDEX IF NOT EXISTS idx_transactions_matchday ON transactions(matchday)",
                "CREATE INDEX IF NOT EXISTS idx_transactions_api_id ON transactions(api_transaction_id)",
                
                # Dream teams and MVPs indexes
                "CREATE INDEX IF NOT EXISTS idx_dream_teams_mvps_championship_round ON dream_teams_mvps(championship_id, round_id, matchday)",
                "CREATE INDEX IF NOT EXISTS idx_dream_teams_mvps_player ON dream_teams_mvps(player_id)",
                "CREATE INDEX IF NOT EXISTS idx_dream_teams_mvps_matchday ON dream_teams_mvps(matchday)",
                
                # Sync metadata indexes
                "CREATE INDEX IF NOT EXISTS idx_sync_metadata_type ON sync_metadata(data_type, championship_id)",
                "CREATE INDEX IF NOT EXISTS idx_sync_metadata_date ON sync_metadata(last_sync_date)",
                
                # Roster indexes
                "CREATE INDEX IF NOT EXISTS idx_team_rosters_team_matchday ON team_rosters(team_id, matchday)",
                "CREATE INDEX IF NOT EXISTS idx_team_rosters_player ON team_rosters(player_id)",
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                except Exception as e:
                    logger.debug(f"Could not create index: {e}")
            
            # Update users table to remove old columns if they exist
            try:
                sql = "ALTER TABLE users DROP COLUMN IF EXISTS team_id"
                cursor.execute(sql)
            except Exception:
                pass
            try:
                sql = "ALTER TABLE users DROP COLUMN IF EXISTS team_name"
                cursor.execute(sql)
            except Exception:
                pass
    
    def reset_database(self):
        """Drop all tables and recreate schema"""
        logger.warning("⚠️  Resetting database - all data will be lost!")
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                
                # Ensure we're in a clean transaction state
                try:
                    conn.rollback()
                except Exception:
                    pass
                
                # First, drop all tables from both old and new schemas
                # Get all table names from the database
                if self.db.db_type in ["postgresql", "postgres"]:
                    # For PostgreSQL, get all tables from public schema
                    cursor.execute("""
                        SELECT tablename 
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                    """)
                    all_tables = [row[0] for row in cursor.fetchall()]
                else:
                    # For SQLite, get all tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    all_tables = [row[0] for row in cursor.fetchall()]
                
                # Drop all tables
                for table in all_tables:
                    try:
                        # Skip system tables
                        if table.startswith('pg_') or table.startswith('sqlite_'):
                            continue
                        cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                        logger.info(f"✅ Dropped table: {table}")
                    except Exception as e:
                        logger.error(f"❌ Could not drop table {table}: {e}")
                        raise
                
                # Commit the drops before recreating
                conn.commit()
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise
        
        # Recreate schema in a new connection
        self._init_database()
        logger.info("✅ Database reset complete - new schema created")
    
    def save_player(self, player_data: Dict) -> str:
        """Save or update player information"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            player_id = player_data.get("id", "")
            if not player_id:
                return None
            
            sql = '''
                INSERT INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            sql = self.db.adapt_params(sql)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    INSERT INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (player_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        role = EXCLUDED.role,
                        real_team_id = EXCLUDED.real_team_id,
                        real_team_name = EXCLUDED.real_team_name,
                        slug = EXCLUDED.slug,
                        photo_url = EXCLUDED.photo_url,
                        last_updated = EXCLUDED.last_updated
                '''
            else:
                sql = '''
                    INSERT OR REPLACE INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)
            
            now = datetime.now()
            cursor.execute(sql, (
                player_id,
                player_data.get("name", ""),
                player_data.get("role", ""),
                player_data.get("teamId", ""),
                player_data.get("team", ""),
                player_data.get("slug", ""),
                player_data.get("photo_url", ""),
                now
            ))
            
            return player_id
    
    def save_players_batch(self, players: List[Dict]) -> int:
        """Save or update multiple players in a single transaction (batch upsert).
        
        Args:
            players: List of dicts with keys: id, name, role, real_team_id/teamId,
                     real_team_name/team, slug, photo_url/photo
        
        Returns:
            Number of players processed
        """
        if not players:
            return 0
        
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            now = datetime.now()
            
            if self.db.db_type in ["postgresql", "postgres"]:
                from psycopg2.extras import execute_values
                sql = '''
                    INSERT INTO players (player_id, name, role, role2, real_team_id, real_team_name, slug, photo_url, value, last_updated)
                    VALUES %s
                    ON CONFLICT (player_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        role = EXCLUDED.role,
                        role2 = EXCLUDED.role2,
                        real_team_id = EXCLUDED.real_team_id,
                        real_team_name = EXCLUDED.real_team_name,
                        slug = EXCLUDED.slug,
                        photo_url = EXCLUDED.photo_url,
                        value = EXCLUDED.value,
                        last_updated = EXCLUDED.last_updated
                '''
                values = []
                for p in players:
                    player_id = p.get("id", "")
                    if not player_id:
                        continue
                    values.append((
                        player_id,
                        p.get("name", ""),
                        p.get("role", ""),
                        p.get("role2", ""),
                        p.get("teamId", p.get("real_team_id", "")),
                        p.get("team", p.get("real_team_name", "")),
                        p.get("slug", ""),
                        p.get("photo", p.get("photo_url", "")),
                        p.get("value", 0) or 0,
                        now,
                    ))
                
                # Use execute_values for efficient batch insert
                # Unwrap the _TursoCursorWrapper if present
                raw_cursor = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                execute_values(raw_cursor, sql, values, page_size=100)
            else:
                # SQLite/Turso: use executemany
                sql = '''
                    INSERT OR REPLACE INTO players 
                    (player_id, name, role, role2, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                values = []
                for p in players:
                    player_id = p.get("id", "")
                    if not player_id:
                        continue
                    values.append((
                        player_id,
                        p.get("name", ""),
                        p.get("role", ""),
                        p.get("role2", ""),
                        p.get("teamId", p.get("real_team_id", "")),
                        p.get("team", p.get("real_team_name", "")),
                        p.get("slug", ""),
                        p.get("photo", p.get("photo_url", "")),
                        now,
                    ))
                cursor.executemany(sql, values)
            
            return len(values)
    
    def save_team_standing(self, championship_id: str, team_id: str, matchday: int, 
                           position: int, points: int, points_this_matchday: int = 0,
                          team_value: int = None, conn=None, cursor=None, **kwargs) -> None:
        """Save team standing for a specific matchday
        
        Args:
            conn: Optional existing database connection (for same transaction)
            cursor: Optional existing cursor (for same transaction)
        """
        use_existing = conn is not None and cursor is not None
        
        if not use_existing:
            conn = self.db.get_connection().__enter__()
            cursor = self.db.get_cursor(conn)
            should_close = True
        else:
            should_close = False
        
        try:
            # Ensure championship exists in the same transaction
            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            # Extra safety: insert championship record directly (idempotent)
            if self.db.db_type in ["postgresql", "postgres"]:
                cursor.execute(
                    """
                    INSERT INTO championships (championship_id, name, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (championship_id) DO NOTHING
                    """,
                    (championship_id, championship_id, datetime.now())
                )
            else:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO championships (championship_id, name, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (championship_id, championship_id, datetime.now())
                )
            
            sql = '''
                INSERT INTO team_standings 
                (championship_id, team_id, matchday, position, points, points_this_matchday, team_value, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            sql = self.db.adapt_params(sql)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    INSERT INTO team_standings 
                    (championship_id, team_id, matchday, position, points, points_this_matchday, team_value, recorded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (championship_id, team_id, matchday) DO UPDATE SET
                        position = EXCLUDED.position,
                        points = EXCLUDED.points,
                        points_this_matchday = EXCLUDED.points_this_matchday,
                        team_value = EXCLUDED.team_value,
                        recorded_at = EXCLUDED.recorded_at
                '''
            else:
                sql = '''
                    INSERT OR REPLACE INTO team_standings 
                    (championship_id, team_id, matchday, position, points, points_this_matchday, team_value, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)
            
            now = datetime.now()
            cursor.execute(sql, (championship_id, team_id, matchday, position, points, points_this_matchday, team_value, now))
            
            if not use_existing:
                conn.commit()
        finally:
            if should_close:
                try:
                    conn.close()
                except:
                    pass
    
    def save_player_performance(self, championship_id: str, player_id: str, team_id: str,
                               matchday: int, points: int, value: int = None,
                               was_best_player: bool = False, **kwargs) -> None:
        """Save player performance for a specific matchday (single record)"""
        self.save_player_performance_batch(championship_id, [{
            "player_id": player_id,
            "team_id": team_id,
            "matchday": matchday,
            "points": points,
            "value": value,
            "was_best_player": was_best_player,
        }])
    
    def save_player_performance_batch(self, championship_id: str, records: List[Dict]) -> int:
        """Save multiple player performance records in a single transaction (batch)."""
        if not records:
            return 0
        
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)
            
            now = datetime.now()
            values = []
            for r in records:
                values.append((
                    championship_id,
                    r["player_id"],
                    r["team_id"],
                    r["matchday"],
                    r["points"],
                    r.get("value"),
                    bool(r.get("was_best_player", False)),
                    now,
                ))
            
            if self.db.db_type in ["postgresql", "postgres"]:
                from psycopg2.extras import execute_values
                raw_cursor = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                execute_values(raw_cursor, '''
                    INSERT INTO player_performance 
                    (championship_id, player_id, team_id, matchday, points, value, was_best_player, recorded_at)
                    VALUES %s
                    ON CONFLICT (championship_id, player_id, team_id, matchday) DO UPDATE SET
                        points = EXCLUDED.points,
                        value = EXCLUDED.value,
                        was_best_player = EXCLUDED.was_best_player,
                        recorded_at = EXCLUDED.recorded_at
                ''', values, page_size=200)
            else:
                cursor.executemany('''
                    INSERT OR REPLACE INTO player_performance 
                    (championship_id, player_id, team_id, matchday, points, value, was_best_player, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', values)
            
            return len(values)
    
    def save_players(self, players: List[Dict]):
        """Save players data to database (optimized for historical analysis)"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            now = datetime.now()
            
            for player in players:
                player_id = player.get("id", "")
                if not player_id:
                    continue
                
                # Extract photo URL
                photo_filename = player.get("photo", "")
                photo_url = None
                if photo_filename:
                    PHOTO_BASE_URL = "https://static01.mondocore.com/futmondo/img/faces/64"
                    if photo_filename.startswith('http'):
                        photo_url = photo_filename
                    elif photo_filename.startswith('/'):
                        photo_url = f"https://static01.mondocore.com{photo_filename}"
                    elif '.' in photo_filename:
                        photo_url = f"{PHOTO_BASE_URL}/{photo_filename}"
                
                sql = '''
                    INSERT INTO players 
                    (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)
                
                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = '''
                        INSERT INTO players 
                        (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (player_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            role = EXCLUDED.role,
                            real_team_id = EXCLUDED.real_team_id,
                            real_team_name = EXCLUDED.real_team_name,
                            slug = EXCLUDED.slug,
                            photo_url = EXCLUDED.photo_url,
                            last_updated = EXCLUDED.last_updated
                    '''
                else:
                    sql = '''
                        INSERT OR REPLACE INTO players 
                        (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    '''
                    sql = self.db.adapt_params(sql)
                
                cursor.execute(sql, (
                    player_id,
                    player.get("name", ""),
                    player.get("role", ""),
                    player.get("teamId", ""),
                    player.get("team", ""),
                    player.get("slug", ""),
                    photo_url,
                    now
                ))
        
        logger.info(f"Saved {len(players)} players to database")
    
    def save_team(self, team_id: str, team_name: str, user_id: str = "", 
                  owner_name: str = "", current_points: int = 0, team_value: int = 0):
        """Save team information"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # First ensure user exists
            if user_id:
                self._ensure_user(user_id, owner_name or team_name)
            
            sql = '''
                INSERT INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                VALUES (?, ?, ?, ?, ?)
            '''
            sql = self.db.adapt_params(sql)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    INSERT INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (team_id) DO UPDATE SET
                        user_id = EXCLUDED.user_id,
                        team_name = EXCLUDED.team_name,
                        initial_budget = EXCLUDED.initial_budget,
                        last_updated = EXCLUDED.last_updated
                '''
            else:
                sql = '''
                    INSERT OR REPLACE INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)
            
            now = datetime.now()
            cursor.execute(sql, (team_id, user_id or None, team_name, 270000000, now))
    
    def _ensure_user(self, user_id: str, username: str):
        """Ensure user exists in database"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            sql = '''
                INSERT INTO users (user_id, username, last_updated)
                VALUES (?, ?, ?)
            '''
            sql = self.db.adapt_params(sql)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    INSERT INTO users (user_id, username, last_updated)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        last_updated = EXCLUDED.last_updated
                '''
            else:
                sql = '''
                    INSERT OR REPLACE INTO users (user_id, username, last_updated)
                    VALUES (?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)
            
            now = datetime.now()
            cursor.execute(sql, (user_id, username, now))
    
    def save_round_ranking(self, round_number: int, championship_id: str, teams: List[Dict]):
        """Save round ranking data for historical analysis"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Ensure championship exists in the same transaction (MUST be first)
            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)
            
            # Commit championship creation if it was just created (to ensure it's visible)
            conn.commit()
            
            now = datetime.now()
            
            def _safe_int(value):
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return 0
            
            for team in teams:
                team_id = (
                    team.get("id")
                    or team.get("teamid")
                    or (team.get("team") or {}).get("id")
                )
                position = team.get("position", 0)
                raw_total_points = team.get("points")
                round_points_only = team.get("roundPoints")
                
                if not team_id:
                    continue
                
                prev_points_total = 0
                if round_number > 1:
                    sql_prev = '''
                        SELECT points FROM team_standings 
                        WHERE championship_id = ? AND team_id = ? AND matchday = ?
                    '''
                    sql_prev = self.db.adapt_params(sql_prev)
                    cursor.execute(sql_prev, (championship_id, team_id, round_number - 1))
                    prev_row = cursor.fetchone()
                    if prev_row:
                        prev_points_total = (
                            prev_row[0]
                            if isinstance(prev_row, tuple)
                            else prev_row.get('points', 0)
                        )

                if round_points_only is not None:
                    points_this_matchday = _safe_int(round_points_only)
                    points = prev_points_total + points_this_matchday
                elif raw_total_points is not None:
                    # Ranking API returns points for THIS round only (not accumulated)
                    points_this_matchday = _safe_int(raw_total_points)
                    points = prev_points_total + points_this_matchday
                else:
                    points_this_matchday = 0
                    points = prev_points_total

                self.save_team_standing(
                    championship_id=championship_id,
                    team_id=team_id,
                    matchday=round_number,
                    position=position,
                    points=points,
                    points_this_matchday=points_this_matchday,
                    team_value=team.get("value", 0),
                    conn=conn,
                    cursor=cursor
                )
            
            # Commit all team standings
            conn.commit()
        
        logger.info(f"Saved round {round_number} ranking for {len(teams)} teams")
    
    def save_player_transactions(self, player_id: str, owners_history: List[Dict]):
        """Legacy hook kept for compatibility with older scripts."""
        logger.debug("save_player_transactions skipped for player %s (legacy method)", player_id)
        return
    
    def save_pressroom_transactions(self, championship_id: str, transactions: List[Dict]):
        """Save transactions from pressroom endpoint (batch optimized for PostgreSQL).
        
        Each transaction has:
        - _id: transaction ID (for pagination)
        - _player: player info with _id and name
        - _buyer: buyer info with _id and name (or None if from market)
        - _seller: seller info with _id and name (or None if to market)
        - price: transaction price
        - created: transaction date
        """
        if not transactions:
            return
        
        MARKET_USER_ID = "market_user"
        MARKET_TEAM_ID = "market_team"
        
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            now = datetime.now()
            
            # --- Phase 1: Collect all users, teams, players that need to exist ---
            users_to_upsert = {}   # user_id -> username
            teams_to_upsert = {}   # team_id -> (user_id, team_name)
            players_to_upsert = {} # player_id -> (name, position, teamId, team, slug, photo)
            
            # Always ensure market user/team exist
            users_to_upsert[MARKET_USER_ID] = "Market"
            teams_to_upsert[MARKET_TEAM_ID] = (MARKET_USER_ID, "Mercado")
            
            transaction_rows = []
            
            for txn in transactions:
                player_info = txn.get("_player", {})
                player_id = player_info.get("_id") if player_info else None
                if not player_id:
                    continue
                
                api_transaction_id = txn.get("_id", "")
                if not api_transaction_id:
                    continue
                
                # Collect player
                players_to_upsert[player_id] = (
                    player_info.get("name", "Unknown"),
                    player_info.get("position", ""),
                    player_info.get("teamId", ""),
                    player_info.get("team", ""),
                    player_info.get("slug", ""),
                    player_info.get("photo", ""),
                )
                
                buyer_info = txn.get("_buyer")
                seller_info = txn.get("_seller")
                price = txn.get("price", 0)
                created = txn.get("created", "")
                matchday = txn.get("matchday") or txn.get("roundNumber") or txn.get("round")
                
                if created:
                    try:
                        transaction_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    except Exception:
                        transaction_date = now
                else:
                    transaction_date = now
                
                buyer_user_id = None
                seller_user_id = None
                buyer_team_id = None
                seller_team_id = None
                
                if buyer_info and seller_info:
                    bid = buyer_info.get("_id")
                    bname = buyer_info.get("name", "Unknown")
                    sid = seller_info.get("_id")
                    sname = seller_info.get("name", "Unknown")
                    users_to_upsert[bid] = bname
                    users_to_upsert[sid] = sname
                    teams_to_upsert[bid] = (bid, bname)
                    teams_to_upsert[sid] = (sid, sname)
                    buyer_user_id, buyer_team_id = bid, bid
                    seller_user_id, seller_team_id = sid, sid
                elif buyer_info:
                    bid = buyer_info.get("_id")
                    bname = buyer_info.get("name", "Unknown")
                    users_to_upsert[bid] = bname
                    teams_to_upsert[bid] = (bid, bname)
                    buyer_user_id, buyer_team_id = bid, bid
                    seller_user_id, seller_team_id = MARKET_USER_ID, MARKET_TEAM_ID
                elif seller_info:
                    sid = seller_info.get("_id")
                    sname = seller_info.get("name", "Unknown")
                    users_to_upsert[sid] = sname
                    teams_to_upsert[sid] = (sid, sname)
                    seller_user_id, seller_team_id = sid, sid
                    buyer_user_id, buyer_team_id = MARKET_USER_ID, MARKET_TEAM_ID
                else:
                    continue
                
                transaction_rows.append((
                    championship_id, api_transaction_id, player_id,
                    seller_user_id, buyer_user_id, seller_team_id, buyer_team_id,
                    int(price) if price is not None else 0,
                    transaction_date, matchday, now,
                ))
            
            if not transaction_rows:
                return
            
            # --- Phase 2: Batch upsert users, teams, players ---
            if self.db.db_type in ["postgresql", "postgres"]:
                from psycopg2.extras import execute_values
                raw_cursor = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                
                # Batch upsert users
                user_values = [(uid, uname, now) for uid, uname in users_to_upsert.items()]
                execute_values(raw_cursor, """
                    INSERT INTO users (user_id, username, last_updated)
                    VALUES %s
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        last_updated = EXCLUDED.last_updated
                """, user_values, page_size=100)
                
                # Batch upsert teams
                team_values = [(tid, uid, tname, 270000000, now) for tid, (uid, tname) in teams_to_upsert.items()]
                execute_values(raw_cursor, """
                    INSERT INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                    VALUES %s
                    ON CONFLICT (team_id) DO NOTHING
                """, team_values, page_size=100)
                
                # Batch upsert players
                player_values = [(pid, name, pos, tid, team, slug, photo, now) 
                                 for pid, (name, pos, tid, team, slug, photo) in players_to_upsert.items()]
                execute_values(raw_cursor, """
                    INSERT INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES %s
                    ON CONFLICT (player_id) DO NOTHING
                """, player_values, page_size=100)
                
                # --- Phase 3: Batch insert transactions ---
                execute_values(raw_cursor, """
                    INSERT INTO transactions 
                        (championship_id, api_transaction_id, player_id, seller_user_id, buyer_user_id,
                         seller_team_id, buyer_team_id, price, transaction_date, matchday, recorded_at)
                    VALUES %s
                    ON CONFLICT (api_transaction_id) DO NOTHING
                """, transaction_rows, page_size=100)
            else:
                # SQLite/Turso fallback — executemany
                cursor.executemany("""
                    INSERT OR REPLACE INTO users (user_id, username, last_updated) VALUES (?, ?, ?)
                """, [(uid, uname, now) for uid, uname in users_to_upsert.items()])
                
                cursor.executemany("""
                    INSERT OR IGNORE INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                """, [(tid, uid, tname, 270000000, now) for tid, (uid, tname) in teams_to_upsert.items()])
                
                cursor.executemany("""
                    INSERT OR IGNORE INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [(pid, name, pos, tid, team, slug, photo, now) 
                      for pid, (name, pos, tid, team, slug, photo) in players_to_upsert.items()])
                
                cursor.executemany("""
                    INSERT OR IGNORE INTO transactions 
                        (championship_id, api_transaction_id, player_id, seller_user_id, buyer_user_id,
                         seller_team_id, buyer_team_id, price, transaction_date, matchday, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, transaction_rows)

    def save_matchday_article(
        self,
        championship_id: str,
        matchday: int,
        article: str,
        summary: Optional[Dict] = None,
        generated_at: Optional[datetime] = None
    ):
        """Persist generated matchday humor article and optional structured summary."""
        if not championship_id or matchday is None or article is None:
            raise ValueError("championship_id, matchday and article are required")

        summary_json = json.dumps(summary) if summary else None
        generated_at = generated_at or datetime.now()

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # Ensure championship exists to satisfy FK constraint
            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    INSERT INTO matchday_articles
                        (championship_id, matchday, article, summary_json, generated_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (championship_id, matchday) DO UPDATE SET
                        article = EXCLUDED.article,
                        summary_json = EXCLUDED.summary_json,
                        generated_at = EXCLUDED.generated_at,
                        updated_at = EXCLUDED.updated_at
                '''
            else:
                sql = '''
                    INSERT OR REPLACE INTO matchday_articles
                        (championship_id, matchday, article, summary_json, generated_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)

            cursor.execute(
                sql,
                (
                    championship_id,
                    matchday,
                    article,
                    summary_json,
                    generated_at,
                    datetime.now(),
                ),
            )

    def get_matchday_article(self, championship_id: str, matchday: int) -> Optional[Dict[str, Any]]:
        """Retrieve stored matchday article and metadata."""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            sql = '''
                SELECT article, summary_json, generated_at, updated_at
                FROM matchday_articles
                WHERE championship_id = ? AND matchday = ?
            '''
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (championship_id, matchday))
            row = cursor.fetchone()

            if not row:
                return None

            if isinstance(row, tuple):
                article, summary_json, generated_at, updated_at = row
            else:
                article = row.get("article")
                summary_json = row.get("summary_json")
                generated_at = row.get("generated_at")
                updated_at = row.get("updated_at")

            return {
                "championship_id": championship_id,
                "matchday": matchday,
                "article": article,
                "summary": json.loads(summary_json) if summary_json else None,
                "generated_at": generated_at,
                "updated_at": updated_at
            }
    
    def get_user_id_by_name(self, user_name: str) -> Optional[Dict[str, str]]:
        """Get user_id and team_id by user name (username or team_name)
        
        Uses case-insensitive matching and creates user if not found.
        
        Returns:
            Dict with 'user_id' and 'team_id', or None if not found and couldn't create
        """
        if not user_name:
            return None
        
        # Normalize name (trim, lowercase for comparison)
        normalized_name = user_name.strip()
        
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Try exact match first (case-insensitive)
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = "SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)"
            else:
                sql = "SELECT user_id FROM users WHERE LOWER(username) = LOWER(?)"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (normalized_name,))
            row = cursor.fetchone()
            
            if row:
                user_id = row[0] if isinstance(row, tuple) else row.get('user_id')
                
                # Try to find team_id for this user
                sql = "SELECT team_id FROM teams WHERE user_id = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (user_id,))
                team_row = cursor.fetchone()
                team_id = team_row[0] if team_row and isinstance(team_row, tuple) else (team_row.get('team_id') if team_row else None)
                
                return {"user_id": user_id, "team_id": team_id}
            
            # Try to find by team_name (case-insensitive)
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = "SELECT team_id, user_id FROM teams WHERE LOWER(team_name) = LOWER(?)"
            else:
                sql = "SELECT team_id, user_id FROM teams WHERE LOWER(team_name) = LOWER(?)"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (normalized_name,))
            row = cursor.fetchone()
            
            if row:
                team_id = row[0] if isinstance(row, tuple) else row.get('team_id')
                user_id = row[1] if isinstance(row, tuple) else row.get('user_id')
                return {"user_id": user_id or team_id, "team_id": team_id}
            
            # Try partial match (contains)
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = "SELECT user_id FROM users WHERE LOWER(username) LIKE LOWER(?)"
            else:
                sql = "SELECT user_id FROM users WHERE LOWER(username) LIKE LOWER(?)"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (f"%{normalized_name}%",))
            row = cursor.fetchone()
            
            if row:
                user_id = row[0] if isinstance(row, tuple) else row.get('user_id')
                sql = "SELECT team_id FROM teams WHERE user_id = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (user_id,))
                team_row = cursor.fetchone()
                team_id = team_row[0] if team_row and isinstance(team_row, tuple) else (team_row.get('team_id') if team_row else None)
                return {"user_id": user_id, "team_id": team_id}
            
            # Try partial match on team_name
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = "SELECT team_id, user_id FROM teams WHERE LOWER(team_name) LIKE LOWER(?)"
            else:
                sql = "SELECT team_id, user_id FROM teams WHERE LOWER(team_name) LIKE LOWER(?)"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (f"%{normalized_name}%",))
            row = cursor.fetchone()
            
            if row:
                team_id = row[0] if isinstance(row, tuple) else row.get('team_id')
                user_id = row[1] if isinstance(row, tuple) else row.get('user_id')
                return {"user_id": user_id or team_id, "team_id": team_id}
            
            # If not found, create user and team
            logger.info(f"Creating new user/team for name: {normalized_name}")
            user_id = str(uuid.uuid4())
            team_id = str(uuid.uuid4())
            
            # Create user
            sql = "INSERT INTO users (user_id, username) VALUES (?, ?)"
            sql = self.db.adapt_params(sql)
            try:
                cursor.execute(sql, (user_id, normalized_name))
            except Exception as e:
                # User might already exist, try to get it
                logger.warning(f"Could not create user {normalized_name}: {e}")
                sql = "SELECT user_id FROM users WHERE username = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (normalized_name,))
                row = cursor.fetchone()
                if row:
                    user_id = row[0] if isinstance(row, tuple) else row.get('user_id')
                else:
                    return None
            
            # Create team
            sql = "INSERT INTO teams (team_id, team_name, user_id) VALUES (?, ?, ?)"
            sql = self.db.adapt_params(sql)
            try:
                cursor.execute(sql, (team_id, normalized_name, user_id))
            except Exception as e:
                # Team might already exist
                logger.warning(f"Could not create team {normalized_name}: {e}")
                sql = "SELECT team_id FROM teams WHERE team_name = ? OR user_id = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (normalized_name, user_id))
                row = cursor.fetchone()
                if row:
                    team_id = row[0] if isinstance(row, tuple) else row.get('team_id')
                else:
                    team_id = user_id  # Use user_id as fallback
            
            conn.commit()
            return {"user_id": user_id, "team_id": team_id}
    
    def save_punishments_bonuses(self, championship_id: str, news_items: List[Dict]):
        """Save punishments and bonuses from locker news
        
        Each news item has:
        - _id: news ID (for pagination)
        - styp: "punish" or "bonus"
        - data: dict with "quantity", "to" (user name), "admin"
        - created: date
        """
        if not news_items:
            return
        
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with self.db.get_connection() as conn:
                    cursor = self.db.get_cursor(conn)
                    
                    # Ensure championship exists in the same transaction
                    self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)
                    
                    for news_item in news_items:
                        news_id = news_item.get("_id")
                        styp = news_item.get("styp")
                        data = news_item.get("data", {})
                        created = news_item.get("created", "")
                        
                        # Only process punish and bonus types
                        if styp not in ["punish", "bonus"]:
                            continue
                        
                        if not news_id or not data:
                            continue
                        
                        quantity = data.get("quantity", 0)
                        user_name = data.get("to", "")
                        admin_name = data.get("admin", "")
                        
                        if not user_name or quantity == 0:
                            continue
                        
                        # Get user_id and team_id by name
                        user_info = self.get_user_id_by_name(user_name)
                        if not user_info:
                            logger.warning(f"Could not find user/team for name: {user_name}")
                            continue
                        
                        user_id = user_info.get("user_id")
                        team_id = user_info.get("team_id")
                        
                        # Parse date
                        try:
                            if created:
                                created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                            else:
                                created_date = datetime.now()
                        except:
                            created_date = datetime.now()
                        
                        # Insert or update punishment/bonus
                        if self.db.db_type in ["postgresql", "postgres"]:
                            sql = '''
                                INSERT INTO punishments_bonuses 
                                (championship_id, news_id, user_id, team_id, user_name, type, amount, admin_name, created_date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (news_id) DO NOTHING
                            '''
                        else:
                            sql = '''
                                INSERT OR IGNORE INTO punishments_bonuses 
                                (championship_id, news_id, user_id, team_id, user_name, type, amount, admin_name, created_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            '''
                            sql = self.db.adapt_params(sql)
                        
                        cursor.execute(sql, (
                            championship_id,
                            news_id,
                            user_id,
                            team_id,
                            user_name,
                            styp,
                            quantity,
                            admin_name,
                            created_date
                        ))
                    
                    # Commit all at once
                    conn.commit()
                    return  # Success, exit retry loop
                    
            except Exception as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.warning(f"Failed to save punishments/bonuses: {e}")
                    raise
    
    def get_user_punishments_bonuses(self, championship_id: str) -> Dict[str, Dict]:
        """Get all punishments and bonuses grouped by user_id/team_id"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    SELECT 
                        COALESCE(team_id, user_id) as user_key,
                        user_id,
                        team_id,
                        MAX(user_name) as user_name,
                        type,
                        SUM(amount) as total_amount,
                        COUNT(*) as count
                    FROM punishments_bonuses
                    WHERE championship_id = %s
                    GROUP BY COALESCE(team_id, user_id), user_id, team_id, type
                '''
                params = (championship_id,)
            else:
                sql = '''
                    SELECT 
                        COALESCE(team_id, user_id) as user_key,
                        user_id,
                        team_id,
                        MAX(user_name) as user_name,
                        type,
                        SUM(amount) as total_amount,
                        COUNT(*) as count
                    FROM punishments_bonuses
                    WHERE championship_id = ?
                    GROUP BY COALESCE(team_id, user_id), user_id, team_id, type
                '''
                sql = self.db.adapt_params(sql)
                params = (championship_id,)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            user_adjustments: Dict[str, Dict] = {}
            
            for row in results:
                user_key = row[0]
                row_user_id = row[1]
                row_team_id = row[2]
                row_user_name = row[3]
                adjustment_type = row[4]
                total_amount = row[5] if row[5] else 0
                count = row[6] if row[6] else 0
                
                key = row_team_id if row_team_id else row_user_id
                if key not in user_adjustments:
                    user_adjustments[key] = {
                        "total_punishments": 0,
                        "total_bonuses": 0,
                        "net_adjustment": 0,
                        "punishment_count": 0,
                        "bonus_count": 0,
                        "user_id": row_user_id,
                        "team_id": row_team_id,
                        "user_name": row_user_name
                    }
                
                if adjustment_type == "punish":
                    user_adjustments[key]["total_punishments"] += total_amount
                    user_adjustments[key]["punishment_count"] += count
                elif adjustment_type == "bonus":
                    user_adjustments[key]["total_bonuses"] += total_amount
                    user_adjustments[key]["bonus_count"] += count
            
            for key, data in user_adjustments.items():
                data["net_adjustment"] = data["total_bonuses"] - data["total_punishments"]
            
            return user_adjustments
    
    def parse_clause_text(self, text: str) -> Optional[Dict[str, str]]:
        """Parse clause text to extract payer, receiver, amount, and player name
        
        Example: "El equipo <strong>Santi Sesma</strong> ha pagado <strong>21.377.932</strong> propiedad de <strong>Patxo Torre</strong> como clausula de <strong>Virgili</strong>"
        
        Returns:
            Dict with 'payer_name', 'receiver_name', 'amount', 'player_name' or None if parsing fails
        """
        if not text:
            return None
        
        # Pattern: "El equipo <strong>[PAYER]</strong> ha pagado <strong>[AMOUNT]</strong> propiedad de <strong>[RECEIVER]</strong> como clausula de <strong>[PLAYER]</strong>"
        # Try with HTML tags first (more reliable)
        pattern_with_html = r'El equipo\s+<strong>([^<]+)</strong>\s+ha pagado\s+<strong>([\d.]+)</strong>\s+propiedad de\s+<strong>([^<]+)</strong>\s+como clausula de\s+<strong>([^<]+)</strong>'
        match = re.search(pattern_with_html, text, re.IGNORECASE)
        
        if not match:
            # Fallback: pattern without HTML tags
            text_clean = re.sub(r'<[^>]+>', '', text)
            pattern = r'El equipo\s+([^h]+?)\s+ha pagado\s+([\d.]+)\s+propiedad de\s+([^c]+?)\s+como clausula de\s+(.+)'
            match = re.search(pattern, text_clean, re.IGNORECASE)
        
        if match:
            payer_name = match.group(1).strip()
            amount_str = match.group(2).strip().replace('.', '')  # Remove dots from number
            receiver_name = match.group(3).strip()
            player_name = match.group(4).strip()
            
            try:
                amount = int(amount_str)
            except ValueError:
                logger.warning(f"Could not parse amount: {amount_str}")
                return None
            
            return {
                "payer_name": payer_name,
                "receiver_name": receiver_name,
                "amount": amount,
                "player_name": player_name
            }
        
        return None
    
    def save_clauses(self, championship_id: str, news_items: List[Dict]):
        """Save clauses from locker news
        
        Each news item has:
        - _id: news ID (for pagination)
        - styp: "clause"
        - txt: HTML text with clause information
        - created: date
        """
        if not news_items:
            return
        
        # First, parse all clauses and get/create users (outside transaction to avoid locks)
        parsed_clauses = []
        for news_item in news_items:
            news_id = news_item.get("_id")
            styp = news_item.get("styp")
            txt = news_item.get("txt", "")
            created = news_item.get("created", "")
            
            # Only process clause types
            if styp != "clause":
                continue
            
            if not news_id or not txt:
                continue
            
            # Parse clause text
            clause_data = self.parse_clause_text(txt)
            if not clause_data:
                logger.warning(f"Could not parse clause text: {txt[:100]}")
                continue
            
            payer_name = clause_data.get("payer_name")
            receiver_name = clause_data.get("receiver_name")
            amount = clause_data.get("amount")
            player_name = clause_data.get("player_name")
            
            # Get user_id and team_id for payer and receiver (will create if not found)
            # Use retry logic for user creation
            payer_info = None
            receiver_info = None
            
            max_user_retries = 3
            for user_attempt in range(max_user_retries):
                try:
                    payer_info = self.get_user_id_by_name(payer_name)
                    receiver_info = self.get_user_id_by_name(receiver_name)
                    break
                except Exception as e:
                    if "locked" in str(e).lower() and user_attempt < max_user_retries - 1:
                        import time
                        time.sleep(0.1 * (user_attempt + 1))
                        continue
                    else:
                        logger.warning(f"Error getting user info for {payer_name}/{receiver_name}: {e}")
                        break
            
            if not payer_info:
                logger.warning(f"Could not find or create user/team for payer: {payer_name}")
                continue
            
            if not receiver_info:
                logger.warning(f"Could not find or create user/team for receiver: {receiver_name}")
                continue
            
            payer_user_id = payer_info.get("user_id")
            payer_team_id = payer_info.get("team_id")
            receiver_user_id = receiver_info.get("user_id")
            receiver_team_id = receiver_info.get("team_id")
            
            # Parse date
            try:
                if created:
                    created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                else:
                    created_date = datetime.now()
            except:
                created_date = datetime.now()
            
            parsed_clauses.append({
                "news_id": news_id,
                "payer_user_id": payer_user_id,
                "payer_team_id": payer_team_id,
                "payer_name": payer_name,
                "receiver_user_id": receiver_user_id,
                "receiver_team_id": receiver_team_id,
                "receiver_name": receiver_name,
                "player_name": player_name,
                "amount": amount,
                "created_date": created_date
            })
        
        # Now save all parsed clauses in a single transaction
        if not parsed_clauses:
            return
        
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with self.db.get_connection() as conn:
                    cursor = self.db.get_cursor(conn)
                    
                    # Ensure championship exists in the same transaction
                    self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)
                    
                    for clause_data in parsed_clauses:
                        # Insert or update clause
                        if self.db.db_type in ["postgresql", "postgres"]:
                            sql = '''
                                INSERT INTO clauses 
                                (championship_id, news_id, payer_user_id, payer_team_id, payer_name, 
                                 receiver_user_id, receiver_team_id, receiver_name, player_name, amount, created_date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (news_id) DO NOTHING
                            '''
                        else:
                            sql = '''
                                INSERT OR IGNORE INTO clauses 
                                (championship_id, news_id, payer_user_id, payer_team_id, payer_name, 
                                 receiver_user_id, receiver_team_id, receiver_name, player_name, amount, created_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            '''
                            sql = self.db.adapt_params(sql)
                        
                        cursor.execute(sql, (
                            championship_id,
                            clause_data["news_id"],
                            clause_data["payer_user_id"],
                            clause_data["payer_team_id"],
                            clause_data["payer_name"],
                            clause_data["receiver_user_id"],
                            clause_data["receiver_team_id"],
                            clause_data["receiver_name"],
                            clause_data["player_name"],
                            clause_data["amount"],
                            clause_data["created_date"]
                        ))
                    
                    # Commit all at once
                    conn.commit()
                    return  # Success, exit retry loop
                    
            except Exception as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.warning(f"Failed to save clauses: {e}")
                    raise
    
    def get_user_clauses_stats(self, championship_id: str) -> Dict[str, Dict]:
        """Get clause statistics grouped by user_id/team_id
        
        Returns:
            Dict with user_id/team_id as key and stats as value:
            {
                user_id_or_team_id: {
                    "clauses_paid": int,  # Number of clauses paid
                    "clauses_received": int,  # Number of clauses received
                    "total_paid": int,  # Total amount paid
                    "total_received": int  # Total amount received
                }
            }
        """
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    SELECT 
                        COALESCE(payer_team_id, payer_user_id) as payer_key,
                        COALESCE(receiver_team_id, receiver_user_id) as receiver_key,
                        payer_team_id,
                        payer_user_id,
                        receiver_team_id,
                        receiver_user_id,
                        COUNT(*) as count,
                        SUM(amount) as total
                    FROM clauses
                    WHERE championship_id = %s
                    GROUP BY COALESCE(payer_team_id, payer_user_id), COALESCE(receiver_team_id, receiver_user_id),
                             payer_team_id, payer_user_id, receiver_team_id, receiver_user_id
                '''
            else:
                sql = '''
                    SELECT 
                        COALESCE(payer_team_id, payer_user_id) as payer_key,
                        COALESCE(receiver_team_id, receiver_user_id) as receiver_key,
                        payer_team_id,
                        payer_user_id,
                        receiver_team_id,
                        receiver_user_id,
                        COUNT(*) as count,
                        SUM(amount) as total
                    FROM clauses
                    WHERE championship_id = ?
                    GROUP BY COALESCE(payer_team_id, payer_user_id), COALESCE(receiver_team_id, receiver_user_id),
                             payer_team_id, payer_user_id, receiver_team_id, receiver_user_id
                '''
                sql = self.db.adapt_params(sql)
            
            cursor.execute(sql, (championship_id,))
            results = cursor.fetchall()
            
            user_clauses = {}
            
            for row in results:
                payer_key = row[0]
                receiver_key = row[1]
                payer_team_id = row[2]
                payer_user_id = row[3]
                receiver_team_id = row[4]
                receiver_user_id = row[5]
                count = row[6] if row[6] else 0
                total = row[7] if row[7] else 0
                
                # Use team_id as key if available, otherwise user_id
                payer_id = payer_team_id if payer_team_id else payer_user_id
                receiver_id = receiver_team_id if receiver_team_id else receiver_user_id
                
                # Initialize payer stats
                if payer_id not in user_clauses:
                    user_clauses[payer_id] = {
                        "clauses_paid": 0,
                        "clauses_received": 0,
                        "total_paid": 0,
                        "total_received": 0
                    }
                
                # Initialize receiver stats
                if receiver_id not in user_clauses:
                    user_clauses[receiver_id] = {
                        "clauses_paid": 0,
                        "clauses_received": 0,
                        "total_paid": 0,
                        "total_received": 0
                    }
                
                # Add to payer stats
                user_clauses[payer_id]["clauses_paid"] += count
                user_clauses[payer_id]["total_paid"] += total
                
                # Add to receiver stats
                user_clauses[receiver_id]["clauses_received"] += count
                user_clauses[receiver_id]["total_received"] += total
            
            return user_clauses
    
    def _get_or_create_user_id(self, user_id_or_username: str, username: str) -> str:
        """Get or create user ID from username or ID"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Check if user_id_or_username is already a user_id (UUID format)
            if len(user_id_or_username) == 36 and user_id_or_username.count('-') == 4:
                # Already a UUID
                sql = "SELECT user_id FROM users WHERE user_id = ?"
                sql = self.db.adapt_params(sql)
                cursor.execute(sql, (user_id_or_username,))
                row = cursor.fetchone()
                if row:
                    return user_id_or_username
            
            # Check by username
            sql = "SELECT user_id FROM users WHERE username = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            if row:
                return row[0] if isinstance(row, tuple) else row.get('user_id')
            
            # Create new user
            user_id = str(uuid.uuid4())
            self._ensure_user(user_id, username)
            return user_id
    
    def save_market_players(self, championship_id: str, players: List[Dict], matchday: int = None):
        """Save market players data with historical tracking"""
        if matchday is None:
            # Try to get current matchday
            matchday = 1  # Default
        
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Ensure championship exists in the same transaction
            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)
            
            now = datetime.now()
            
            for player in players:
                player_id = player.get("id", "")
                if not player_id:
                    continue
                
                market_price = player.get("marketPrice", player.get("price", player.get("market_price")))
                availability = player.get("availability", player.get("available", "unknown"))
                market_statistics = json.dumps(player.get("marketStats", player.get("statistics", {})))
                
                sql = '''
                    INSERT INTO player_market_data 
                    (championship_id, player_id, matchday, market_price, availability, market_statistics, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)
                
                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = '''
                        INSERT INTO player_market_data 
                        (championship_id, player_id, matchday, market_price, availability, market_statistics, recorded_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (championship_id, player_id, matchday) DO UPDATE SET
                            market_price = EXCLUDED.market_price,
                            availability = EXCLUDED.availability,
                            market_statistics = EXCLUDED.market_statistics,
                            recorded_at = EXCLUDED.recorded_at
                    '''
                else:
                    sql = '''
                        INSERT OR REPLACE INTO player_market_data 
                        (championship_id, player_id, matchday, market_price, availability, market_statistics, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    '''
                    sql = self.db.adapt_params(sql)
                
                cursor.execute(sql, (
                    championship_id,
                    player_id,
                    matchday,
                    market_price,
                    availability,
                    market_statistics,
                    now
                ))
        
        logger.info(f"Saved {len(players)} market players for matchday {matchday}")
    
    def save_team_roster(self, championship_id: str, team_id: str, players: List[Dict], matchday: int = None):
        """Save team roster with historical tracking
        
        Also ensures the team exists in the teams table.
        """
        if matchday is None:
            matchday = 1  # Default
        
        # Ensure championship exists before inserting
        self.ensure_championship_exists(championship_id)
        
        # Ensure team exists in teams table (create if not exists)
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Check if team exists
            sql = "SELECT team_id FROM teams WHERE team_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (team_id,))
            team_exists = cursor.fetchone()
            
            if not team_exists:
                # Create team entry (we don't have name/user_id here, but that's OK)
                sql = "INSERT INTO teams (team_id, team_name, user_id) VALUES (?, ?, ?)"
                sql = self.db.adapt_params(sql)
                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = '''
                        INSERT INTO teams (team_id, team_name, user_id) 
                        VALUES (%s, %s, %s)
                        ON CONFLICT (team_id) DO NOTHING
                    '''
                else:
                    sql = "INSERT OR IGNORE INTO teams (team_id, team_name, user_id) VALUES (?, ?, ?)"
                    sql = self.db.adapt_params(sql)
                
                cursor.execute(sql, (team_id, None, team_id))  # Use team_id as user_id fallback
                conn.commit()
        
        # Now save the roster
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Ensure championship exists in the same transaction
            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)
            
            now = datetime.now()
            
            for idx, player in enumerate(players):
                player_id = player.get("id", "")
                if not player_id:
                    continue
                
                formation_position = player.get("position", player.get("formationPosition", ""))
                is_starter = player.get("isStarter", player.get("starter", True))
                lineup_order = player.get("lineupOrder", player.get("order", idx))
                
                sql = '''
                    INSERT INTO team_rosters 
                    (championship_id, team_id, player_id, matchday, formation_position, is_starter, lineup_order, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)
                
                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = '''
                        INSERT INTO team_rosters 
                        (championship_id, team_id, player_id, matchday, formation_position, is_starter, lineup_order, recorded_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (championship_id, team_id, player_id, matchday) DO UPDATE SET
                            formation_position = EXCLUDED.formation_position,
                            is_starter = EXCLUDED.is_starter,
                            lineup_order = EXCLUDED.lineup_order,
                            recorded_at = EXCLUDED.recorded_at
                    '''
                else:
                    sql = '''
                        INSERT OR REPLACE INTO team_rosters 
                        (championship_id, team_id, player_id, matchday, formation_position, is_starter, lineup_order, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    '''
                    sql = self.db.adapt_params(sql)
                
                cursor.execute(sql, (
                    championship_id,
                    team_id,
                    player_id,
                    matchday,
                    formation_position,
                    is_starter,
                    lineup_order,
                    now
                ))
            
            # Commit the transaction
            conn.commit()
        
        logger.info(f"Saved roster for team {team_id} (matchday {matchday}): {len(players)} players")
    
    def ensure_championship_exists(self, championship_id: str, name: str = None, conn=None, cursor=None):
        """Ensure championship record exists in championships table
        
        Creates the championship if it doesn't exist to satisfy foreign key constraints.
        Can use an existing connection/cursor to ensure it's in the same transaction.
        
        Args:
            championship_id: Championship ID
            name: Championship name (optional)
            conn: Optional existing database connection (for same transaction)
            cursor: Optional existing cursor (for same transaction)
        """
        use_existing = conn is not None and cursor is not None
        
        if not use_existing:
            # Use context manager for standalone call
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                self._ensure_championship_in_transaction(cursor, championship_id, name)
                conn.commit()
        else:
            # Use existing connection/cursor (same transaction)
            self._ensure_championship_in_transaction(cursor, championship_id, name)
    
    def _ensure_championship_in_transaction(self, cursor, championship_id: str, name: str = None):
        """Internal helper to ensure championship exists using provided cursor"""
        # Check if championship exists
        sql = "SELECT championship_id FROM championships WHERE championship_id = ?"
        sql = self.db.adapt_params(sql)
        cursor.execute(sql, (championship_id,))
        exists = cursor.fetchone()
        
        if not exists:
            # Create championship record
            if self.db.db_type in ["postgresql", "postgres"]:
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
                sql = self.db.adapt_params(sql)
            
            cursor.execute(sql, (championship_id, name or championship_id, datetime.now()))
            logger.debug(f"Created championship record: {championship_id}")
    
    def get_last_sync_metadata(self, championship_id: str, data_type: str) -> Optional[Dict]:
        """Get last sync metadata for a specific data type
        
        Args:
            championship_id: Championship ID
            data_type: Type of data (transactions, clauses, dream_teams, rosters, player_performance, players)
        
        Returns:
            Dict with sync metadata or None if not found
        """
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            sql = "SELECT last_sync_id, last_sync_date, last_sync_matchday, records_synced, sync_status, updated_at FROM sync_metadata WHERE championship_id = ? AND data_type = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (championship_id, data_type))
            row = cursor.fetchone()
            
            if row:
                return {
                    "last_sync_id": row[0],
                    "last_sync_date": row[1],
                    "last_sync_matchday": row[2],
                    "records_synced": row[3],
                    "sync_status": row[4],
                    "updated_at": row[5]
                }
            return None
    
    def update_sync_metadata(self, championship_id: str, data_type: str, last_sync_id: str = None, 
                            last_sync_date: datetime = None, last_sync_matchday: int = None,
                            records_synced: int = 0, sync_duration_seconds: float = None,
                            sync_status: str = "success", error_message: str = None):
        """Update sync metadata after a synchronization
        
        Args:
            championship_id: Championship ID
            data_type: Type of data (transactions, clauses, dream_teams, rosters, player_performance, players)
            last_sync_id: Last processed ID (transaction_id, news_id, etc.)
            last_sync_date: Last sync timestamp
            last_sync_matchday: Last processed matchday (for matchday-based data)
            records_synced: Number of records synced
            sync_duration_seconds: Duration of sync in seconds
            sync_status: Status of sync (success, error, partial)
            error_message: Error message if sync failed
        """
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Ensure championship exists in the same transaction
            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    INSERT INTO sync_metadata 
                    (championship_id, data_type, last_sync_id, last_sync_date, last_sync_matchday,
                     records_synced, sync_duration_seconds, sync_status, error_message, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (championship_id, data_type) DO UPDATE SET
                        last_sync_id = EXCLUDED.last_sync_id,
                        last_sync_date = EXCLUDED.last_sync_date,
                        last_sync_matchday = EXCLUDED.last_sync_matchday,
                        records_synced = EXCLUDED.records_synced,
                        sync_duration_seconds = EXCLUDED.sync_duration_seconds,
                        sync_status = EXCLUDED.sync_status,
                        error_message = EXCLUDED.error_message,
                        updated_at = EXCLUDED.updated_at
                '''
            else:
                sql = '''
                    INSERT OR REPLACE INTO sync_metadata 
                    (championship_id, data_type, last_sync_id, last_sync_date, last_sync_matchday,
                     records_synced, sync_duration_seconds, sync_status, error_message, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)
            
            now = datetime.now()
            cursor.execute(sql, (
                championship_id,
                data_type,
                last_sync_id,
                last_sync_date or now,
                last_sync_matchday,
                records_synced,
                sync_duration_seconds,
                sync_status,
                error_message,
                now
            ))
            conn.commit()
    
    def save_dream_team_mvp(self, championship_id: str, round_id: str, matchday: int,
                            dream_team_players: List[str], mvp_player_id: str = None,
                            player_details: Optional[Dict[str, Dict]] = None) -> None:
        """Save dream team and MVP for a specific round
        
        Args:
            championship_id: Championship ID
            round_id: Round ID
            matchday: Matchday number
            dream_team_players: List of player IDs in dream team
            mvp_player_id: Player ID of MVP (optional)
        """
        if not dream_team_players and not mvp_player_id:
            return
        
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Ensure championship exists in the same transaction
            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)
            
            player_details = player_details or {}

            def player_exists(player_id: str) -> bool:
                if not player_id:
                    return False
                if self.db.db_type in ["postgresql", "postgres"]:
                    check_sql = "SELECT 1 FROM players WHERE player_id = %s"
                else:
                    check_sql = "SELECT 1 FROM players WHERE player_id = ?"
                    check_sql = self.db.adapt_params(check_sql)
                cursor.execute(check_sql, (player_id,))
                return cursor.fetchone() is not None

            def ensure_player(player_id: str) -> bool:
                if player_exists(player_id):
                    return True
                details = player_details.get(player_id)
                if not details:
                    return False
                payload = {
                    "id": details.get("id") or details.get("_id") or player_id,
                    "name": details.get("name", ""),
                    "role": details.get("role") or details.get("position", ""),
                    "teamId": details.get("teamId") or details.get("team_id") or details.get("teamId"),
                    "team": details.get("team") or details.get("teamName", ""),
                    "slug": details.get("slug", ""),
                    "photo_url": details.get("photo") or details.get("photo_url", "")
                }
                try:
                    self.save_player(payload)
                    return player_exists(player_id)
                except Exception as e:
                    logger.warning("Could not upsert player %s for dream team: %s", player_id, e)
                    return False

            # Save dream team players
            for player_id in dream_team_players:
                if not player_id:
                    continue
                if not ensure_player(player_id):
                    logger.warning("Skipping dream team player %s for round %s: not found in players table",
                                   player_id, round_id)
                    continue
                
                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = '''
                        INSERT INTO dream_teams_mvps 
                        (championship_id, round_id, matchday, player_id, is_mvp, recorded_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (championship_id, round_id, player_id, is_mvp) DO NOTHING
                    '''
                else:
                    sql = '''
                        INSERT OR IGNORE INTO dream_teams_mvps 
                        (championship_id, round_id, matchday, player_id, is_mvp, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    '''
                    sql = self.db.adapt_params(sql)
                
                cursor.execute(sql, (
                    championship_id,
                    round_id,
                    matchday,
                    player_id,
                    False,  # is_mvp
                    datetime.now()
                ))
            
            # Save MVP if provided
            if mvp_player_id:
                if not ensure_player(mvp_player_id):
                    logger.warning("Skipping MVP %s for round %s: not found in players table",
                                   mvp_player_id, round_id)
                    mvp_player_id = None

            if mvp_player_id:
                if self.db.db_type in ["postgresql", "postgres"]:
                    sql = '''
                        INSERT INTO dream_teams_mvps 
                        (championship_id, round_id, matchday, player_id, is_mvp, recorded_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (championship_id, round_id, player_id, is_mvp) DO NOTHING
                    '''
                else:
                    sql = '''
                        INSERT OR IGNORE INTO dream_teams_mvps 
                        (championship_id, round_id, matchday, player_id, is_mvp, recorded_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    '''
                    sql = self.db.adapt_params(sql)
                
                cursor.execute(sql, (
                    championship_id,
                    round_id,
                    matchday,
                    mvp_player_id,
                    True,  # is_mvp
                    datetime.now()
                ))
            
            conn.commit()
            logger.info(f"Saved dream team/MVP for round {round_id} (matchday {matchday}): {len(dream_team_players)} players, MVP: {mvp_player_id or 'None'}")
    
    def save_pressroom_news(self, championship_id: str, news_items: List[Dict]):
        """Save pressroom news (kept for compatibility but not in optimized schema)"""
        # Pressroom news is not critical for historical analysis
        # Can be stored in separate table if needed
        logger.info(f"Skipping {len(news_items)} pressroom news items (not in optimized schema)")
    
    def should_update_cache(self, data_type: str) -> bool:
        """Check if cache should be updated (always true for fresh data in V2)"""
        return True  # Always update in V2 for historical accuracy
    
    def get_users_unique_players_stats(self, championship_id: str) -> List[Dict]:
        """Get statistics of unique players aligned by each user/team"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            unique_players_sql = '''
                SELECT 
                    COALESCE(t.team_id, tr.team_id) as team_id,
                    COALESCE(t.team_name, tr.team_id) as team_name,
                    COALESCE(t.user_id, tr.team_id) as user_id,
                    u.username,
                    COUNT(DISTINCT tr.player_id) as unique_players_count
                FROM team_rosters tr
                LEFT JOIN teams t ON tr.team_id = t.team_id
                LEFT JOIN users u ON COALESCE(t.user_id, tr.team_id) = u.user_id
                WHERE tr.championship_id = ?
                GROUP BY COALESCE(t.team_id, tr.team_id), COALESCE(t.team_name, tr.team_id), COALESCE(t.user_id, tr.team_id), u.username
            '''
            unique_players_sql = self.db.adapt_sql(unique_players_sql)
            unique_players_sql = self.db.adapt_params(unique_players_sql)
            cursor.execute(unique_players_sql, (championship_id,))
            results = cursor.fetchall()

            stats = {}
            for row in results:
                team_id = row[0]
                stats[team_id] = {
                    "team_id": team_id,
                    "team_name": row[1] if row[1] and row[1] != team_id else None,
                    "user_id": row[2],
                    "username": row[3],
                    "unique_players_count": row[4],
                    "clauses_paid": 0,
                    "clauses_received": 0,
                    "total_clauses_paid": 0,
                    "total_clauses_received": 0,
                    "transaction_count": 0,
                    "total_spent": 0,
                    "total_received": 0,
                    "transaction_profit": 0
                }

            clauses_sql = '''
                SELECT 
                    COALESCE(payer_team_id, payer_user_id) as payer_id,
                    COALESCE(receiver_team_id, receiver_user_id) as receiver_id,
                    COUNT(*) as clause_count,
                    SUM(amount) as total_amount
                FROM clauses
                WHERE championship_id = ?
                GROUP BY COALESCE(payer_team_id, payer_user_id), COALESCE(receiver_team_id, receiver_user_id)
            '''
            clauses_sql = self.db.adapt_sql(clauses_sql)
            clauses_sql = self.db.adapt_params(clauses_sql)
            cursor.execute(clauses_sql, (championship_id,))
            clauses_rows = cursor.fetchall()

            for row in clauses_rows:
                payer_id, receiver_id, clause_count, total_amount = row
                if payer_id in stats:
                    stats[payer_id]["clauses_paid"] += clause_count or 0
                    stats[payer_id]["total_clauses_paid"] += total_amount or 0
                if receiver_id in stats:
                    stats[receiver_id]["clauses_received"] += clause_count or 0
                    stats[receiver_id]["total_clauses_received"] += total_amount or 0

            transactions_sql = '''
                SELECT 
                    buyer_team_id,
                    seller_team_id,
                    price
                FROM transactions
                WHERE championship_id = ?
            '''
            transactions_sql = self.db.adapt_sql(transactions_sql)
            transactions_sql = self.db.adapt_params(transactions_sql)
            cursor.execute(transactions_sql, (championship_id,))
            txn_rows = cursor.fetchall()

            for row in txn_rows:
                buyer_team_id, seller_team_id, price = row
                if buyer_team_id in stats:
                    stats[buyer_team_id]["transaction_count"] += 1
                    stats[buyer_team_id]["total_spent"] += price or 0
                    stats[buyer_team_id]["transaction_profit"] -= price or 0
                if seller_team_id in stats:
                    stats[seller_team_id]["transaction_count"] += 1
                    stats[seller_team_id]["total_received"] += price or 0
                    stats[seller_team_id]["transaction_profit"] += price or 0

            # Normalize team_name and username fallbacks
            for team_id, entry in stats.items():
                if not entry["team_name"]:
                    team_info = self.get_team_by_id(team_id)
                    if team_info and team_info.get("team_name"):
                        entry["team_name"] = team_info["team_name"]
                if not entry.get("username") and entry.get("user_id"):
                    user_info = self.get_user_by_id(entry["user_id"])
                    if user_info and user_info.get("username"):
                        entry["username"] = user_info["username"]

            return list(stats.values())
    
    def get_all_players_with_points(self, championship_id: str) -> List[Dict]:
        """Get all players with their total points"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    SELECT 
                        p.id as player_id,
                        p.name as player_name,
                        p.role,
                        p.team,
                        COALESCE(SUM(pp.points), 0) as total_points
                    FROM players p
                    LEFT JOIN player_performance pp ON p.id = pp.player_id AND (pp.championship_id = %s OR pp.championship_id IS NULL)
                    GROUP BY p.id, p.name, p.role, p.team
                    ORDER BY total_points DESC
                '''
            else:
                sql = '''
                    SELECT 
                        p.id as player_id,
                        p.name as player_name,
                        p.role,
                        p.team,
                        COALESCE(SUM(pp.points), 0) as total_points
                    FROM players p
                    LEFT JOIN player_performance pp ON p.id = pp.player_id AND (pp.championship_id = ? OR pp.championship_id IS NULL)
                    GROUP BY p.id, p.name, p.role, p.team
                    ORDER BY total_points DESC
                '''
            
            cursor.execute(sql, (championship_id,))
            results = cursor.fetchall()
            
            players = []
            for row in results:
                players.append({
                    "player_id": row[0],
                    "player_name": row[1],
                    "role": row[2],
                    "team": row[3],
                    "total_points": row[4] if row[4] else 0
                })
            
            return players
    
    def get_all_player_transactions(self, championship_id: str) -> Dict[str, List[Dict]]:
        """Get all transactions grouped by player_id"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    SELECT 
                        player_id,
                        price,
                        transaction_date,
                        buyer_user_id,
                        seller_user_id
                    FROM transactions
                    WHERE championship_id = %s OR championship_id = ''
                    ORDER BY player_id, transaction_date
                '''
            else:
                sql = '''
                    SELECT 
                        player_id,
                        price,
                        transaction_date,
                        buyer_user_id,
                        seller_user_id
                    FROM transactions
                    WHERE championship_id = ? OR championship_id = ''
                    ORDER BY player_id, transaction_date
                '''
            
            cursor.execute(sql, (championship_id,))
            results = cursor.fetchall()
            
            transactions_by_player = {}
            for row in results:
                player_id = row[0]
                if player_id not in transactions_by_player:
                    transactions_by_player[player_id] = []
                
                transactions_by_player[player_id].append({
                    "price": row[1],
                    "transaction_date": row[2].isoformat() if row[2] else None,
                    "buyer_user_id": row[3],
                    "seller_user_id": row[4]
                })
            
            return transactions_by_player
    
    def get_all_users_with_points(self, championship_id: str) -> List[Dict]:
        """Get all users/teams with their total points from team standings"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Get the latest matchday for each team to get their current total points
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    SELECT DISTINCT ON (ts.team_id)
                        ts.team_id,
                        t.team_name,
                        t.user_id,
                        u.username,
                        ts.points as total_points
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    LEFT JOIN users u ON t.user_id = u.user_id
                    WHERE ts.championship_id = %s
                    ORDER BY ts.team_id, ts.matchday DESC
                '''
            else:
                sql = '''
                    SELECT 
                        ts.team_id,
                        t.team_name,
                        t.user_id,
                        u.username,
                        ts.points as total_points
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    LEFT JOIN users u ON t.user_id = u.user_id
                    WHERE ts.championship_id = ? 
                    AND ts.matchday = (
                        SELECT MAX(matchday) 
                        FROM team_standings 
                        WHERE championship_id = ? AND team_id = ts.team_id
                    )
                    ORDER BY ts.points DESC
                '''
            
            if self.db.db_type in ["postgresql", "postgres"]:
                cursor.execute(sql, (championship_id,))
            else:
                cursor.execute(sql, (championship_id, championship_id))
            
            results = cursor.fetchall()
            
            users = []
            for row in results:
                users.append({
                    "team_id": row[0],
                    "team_name": row[1],
                    "user_id": row[2],
                    "username": row[3] if row[3] else row[1],
                    "total_points": row[4] if row[4] else 0
                })
            
            return users
    
    def get_user_transactions(self, championship_id: str, user_id: str = None) -> Dict[str, Dict]:
        """Get all transactions grouped by user_id/team_id (buyer and seller)
        
        Returns a dict with user_id/team_id as key and transaction summary as value.
        The key can be either a user_id (UUID) or team_id, depending on what's available.
        
        {
            user_id_or_team_id: {
                "total_spent": int,  # Money spent on purchases
                "total_received": int,  # Money received from sales
                "transaction_profit": int,  # total_received - total_spent
                "transaction_count": int
            }
        }
        """
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # First, get a mapping of username -> team_id from teams table
            username_to_team_id = {}
            team_id_to_user_id = {}
            
            sql_teams = "SELECT team_id, user_id, team_name FROM teams"
            cursor.execute(sql_teams)
            team_rows = cursor.fetchall()
            for team_row in team_rows:
                team_id = team_row[0]
                user_id_from_team = team_row[1]
                team_name = team_row[2]
                
                if team_id:
                    team_id_to_user_id[team_id] = user_id_from_team or team_id
                    # Also map by team_name (username might be same as team_name)
                    if team_name:
                        username_to_team_id[team_name] = team_id
            
            # Also get username -> user_id mapping from users table
            username_to_user_id = {}
            sql_users = "SELECT user_id, username FROM users"
            cursor.execute(sql_users)
            user_rows = cursor.fetchall()
            for user_row in user_rows:
                user_id_from_db = user_row[0]
                username = user_row[1]
                if username:
                    username_to_user_id[username] = user_id_from_db
            
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    SELECT 
                        buyer_user_id,
                        seller_user_id,
                        buyer_team_id,
                        seller_team_id,
                        price,
                        transaction_date
                    FROM transactions
                    WHERE championship_id = %s
                '''
                params = (championship_id,)
                if user_id:
                    sql += ' AND (buyer_user_id = %s OR seller_user_id = %s OR buyer_team_id = %s OR seller_team_id = %s)'
                    params = (championship_id, user_id, user_id, user_id, user_id)
                sql += ' ORDER BY transaction_date'
            else:
                sql = '''
                    SELECT 
                        buyer_user_id,
                        seller_user_id,
                        buyer_team_id,
                        seller_team_id,
                        price,
                        transaction_date
                    FROM transactions
                    WHERE championship_id = ?
                '''
                params = (championship_id,)
                if user_id:
                    sql += ' AND (buyer_user_id = ? OR seller_user_id = ? OR buyer_team_id = ? OR seller_team_id = ?)'
                    params = (championship_id, user_id, user_id, user_id, user_id)
                sql += ' ORDER BY transaction_date'
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # Helper to get team_id from user_id (UUID)
            def get_team_id_from_user_id(uuid_str: str) -> str:
                if not uuid_str:
                    return None
                
                # First, check if uuid_str is already a team_id
                if uuid_str in team_id_to_user_id:
                    return uuid_str
                
                # Try to find user by UUID and get their team_id
                # Reverse lookup: find team_id where user_id matches
                for tid, uid in team_id_to_user_id.items():
                    if uid == uuid_str:
                        return tid
                
                # Try to find by username (if user_id is actually a username)
                if uuid_str in username_to_team_id:
                    return username_to_team_id[uuid_str]
                
                # Also check username_to_user_id and then map to team_id
                if uuid_str in username_to_user_id:
                    user_id_from_username = username_to_user_id[uuid_str]
                    # Now find team_id for this user_id
                    for tid, uid in team_id_to_user_id.items():
                        if uid == user_id_from_username:
                            return tid
                
                # If not found, return the UUID itself (will be used as fallback)
                return uuid_str
            
            user_transactions = {}
            
            for row in results:
                buyer_user_id = row[0]
                seller_user_id = row[1]
                buyer_team_id = row[2]
                seller_team_id = row[3]
                price = row[4] if row[4] else 0
                
                # Map user_ids to team_ids for better matching
                if not buyer_team_id:
                    buyer_team_id = get_team_id_from_user_id(buyer_user_id) if buyer_user_id else None
                if not seller_team_id:
                    seller_team_id = get_team_id_from_user_id(seller_user_id) if seller_user_id else None
                
                # Use team_id as key if available and different from user_id, otherwise use user_id
                # This ensures all transactions for the same user are grouped together
                if buyer_team_id and buyer_team_id != buyer_user_id:
                    buyer_key = buyer_team_id
                else:
                    buyer_key = buyer_user_id
                
                if seller_team_id and seller_team_id != seller_user_id:
                    seller_key = seller_team_id
                else:
                    seller_key = seller_user_id
                
                # Skip market transactions (seller is "Market")
                if seller_user_id and seller_user_id.lower() != "market" and seller_key:
                    # This is a sale - seller receives money
                    if seller_key not in user_transactions:
                        user_transactions[seller_key] = {
                            "total_spent": 0,
                            "total_received": 0,
                            "transaction_count": 0
                        }
                    user_transactions[seller_key]["total_received"] += price
                    user_transactions[seller_key]["transaction_count"] += 1
                
                # Buyer spends money
                if buyer_key:
                    if buyer_key not in user_transactions:
                        user_transactions[buyer_key] = {
                            "total_spent": 0,
                            "total_received": 0,
                            "transaction_count": 0
                        }
                    # Buyer always spends money (whether from market or another user)
                    user_transactions[buyer_key]["total_spent"] += price
                    user_transactions[buyer_key]["transaction_count"] += 1
            
            # Calculate profit for each user
            for user_key, data in user_transactions.items():
                data["transaction_profit"] = data["total_received"] - data["total_spent"]
            
            return user_transactions
    
    def get_evolution_data_from_db(self, championship_id: str) -> Dict:
        """Get evolution data (points and positions per matchday) from database
        
        Returns:
            Dict with structure:
            {
                "matchdays": [1, 2, 3, ...],
                "teams": [
                    {
                        "team_id": "...",
                        "team_name": "...",
                        "points_evolution": [40, 70, 100, ...],
                        "positions_evolution": [1, 2, 1, ...]
                    }
                ]
            }
        """
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Get all team standings ordered by matchday
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    SELECT 
                        ts.team_id,
                        t.team_name,
                        ts.matchday,
                        ts.points,
                        ts.position
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    WHERE ts.championship_id = %s
                    ORDER BY ts.matchday ASC, ts.position ASC
                '''
            else:
                sql = '''
                    SELECT 
                        ts.team_id,
                        t.team_name,
                        ts.matchday,
                        ts.points,
                        ts.position
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    WHERE ts.championship_id = ?
                    ORDER BY ts.matchday ASC, ts.position ASC
                '''
            
            cursor.execute(sql, (championship_id,))
            results = cursor.fetchall()
            
            # Organize data by team
            teams_data = {}
            matchdays_set = set()
            
            for row in results:
                team_id = row[0]
                team_name = row[1]
                matchday = row[2]
                points = row[3]
                position = row[4]
                
                matchdays_set.add(matchday)
                
                if team_id not in teams_data:
                    teams_data[team_id] = {
                        "team_id": team_id,
                        "team_name": team_name,
                        "points_evolution": [],
                        "positions_evolution": []
                    }
                
                teams_data[team_id]["points_evolution"].append(points)
                teams_data[team_id]["positions_evolution"].append(position)
            
            matchdays = sorted(matchdays_set)
            
            # Ensure all teams have data for all matchdays (fill with last known value)
            for team_id, team_data in teams_data.items():
                points_evol = team_data["points_evolution"]
                positions_evol = team_data["positions_evolution"]
                
                # Fill missing matchdays with last known value
                last_points = points_evol[-1] if points_evol else 0
                last_position = positions_evol[-1] if positions_evol else 0
                
                for i, md in enumerate(matchdays):
                    if i >= len(points_evol):
                        points_evol.append(last_points)
                        positions_evol.append(last_position)
                    else:
                        last_points = points_evol[i]
                        last_position = positions_evol[i]
            
            return {
                "matchdays": matchdays,
                "teams": list(teams_data.values())
            }
    
    def get_matchday_data_for_news(self, championship_id: str, matchday: int) -> Dict:
        """Get comprehensive matchday data for generating press news"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Get current standings
            if self.db.db_type in ["postgresql", "postgres"]:
                current_sql = '''
                    SELECT 
                        t.team_id,
                        t.team_name,
                        u.username,
                        ts.position,
                        ts.points,
                        ts.points_this_matchday
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    LEFT JOIN users u ON t.user_id = u.user_id
                    WHERE ts.championship_id = %s AND ts.matchday = %s
                    ORDER BY ts.position
                '''
            else:
                current_sql = '''
                    SELECT 
                        t.team_id,
                        t.team_name,
                        u.username,
                        ts.position,
                        ts.points,
                        ts.points_this_matchday
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    LEFT JOIN users u ON t.user_id = u.user_id
                    WHERE ts.championship_id = ? AND ts.matchday = ?
                    ORDER BY ts.position
                '''
            cursor.execute(current_sql, (championship_id, matchday))
            current_standings = []
            for row in cursor.fetchall():
                current_standings.append({
                    "team_id": row[0],
                    "team_name": row[1],
                    "username": row[2],
                    "position": row[3],
                    "points": row[4],
                    "points_this_matchday": row[5]
                })
            
            # Get previous matchday standings (if exists)
            if self.db.db_type in ["postgresql", "postgres"]:
                previous_sql = '''
                    SELECT 
                        t.team_id,
                        ts.position,
                        ts.points
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    WHERE ts.championship_id = %s AND ts.matchday = %s
                '''
            else:
                previous_sql = '''
                    SELECT 
                        t.team_id,
                        ts.position,
                        ts.points
                    FROM team_standings ts
                    JOIN teams t ON ts.team_id = t.team_id
                    WHERE ts.championship_id = ? AND ts.matchday = ?
                '''
            previous_standings = {}
            if matchday > 1:
                cursor.execute(previous_sql, (championship_id, matchday - 1))
                for row in cursor.fetchall():
                    previous_standings[row[0]] = {
                        "position": row[1],
                        "points": row[2]
                    }
            
            # Get best players per team this matchday
            if self.db.db_type in ["postgresql", "postgres"]:
                best_players_sql = '''
                    SELECT 
                        pp.team_id,
                        pp.player_id,
                        p.name as player_name,
                        pp.points as player_points,
                        t.team_name
                    FROM player_performance pp
                    JOIN players p ON pp.player_id = p.player_id
                    JOIN teams t ON pp.team_id = t.team_id
                    WHERE pp.championship_id = %s AND pp.matchday = %s AND pp.was_best_player = true
                    ORDER BY pp.points DESC
                '''
            else:
                best_players_sql = '''
                    SELECT 
                        pp.team_id,
                        pp.player_id,
                        p.name as player_name,
                        pp.points as player_points,
                        t.team_name
                    FROM player_performance pp
                    JOIN players p ON pp.player_id = p.player_id
                    JOIN teams t ON pp.team_id = t.team_id
                    WHERE pp.championship_id = ? AND pp.matchday = ? AND pp.was_best_player = true
                    ORDER BY pp.points DESC
                '''
            cursor.execute(best_players_sql, (championship_id, matchday))
            best_players = []
            for row in cursor.fetchall():
                best_players.append({
                    "team_id": row[0],
                    "player_id": row[1],
                    "player_name": row[2],
                    "player_points": row[3],
                    "team_name": row[4]
                })
            
            # Get top scoring players this matchday
            if self.db.db_type in ["postgresql", "postgres"]:
                top_players_sql = '''
                    SELECT 
                        pp.player_id,
                        p.name as player_name,
                        pp.points,
                        t.team_name
                    FROM player_performance pp
                    JOIN players p ON pp.player_id = p.player_id
                    JOIN teams t ON pp.team_id = t.team_id
                    WHERE pp.championship_id = %s AND pp.matchday = %s
                    ORDER BY pp.points DESC
                    LIMIT 10
                '''
            else:
                top_players_sql = '''
                    SELECT 
                        pp.player_id,
                        p.name as player_name,
                        pp.points,
                        t.team_name
                    FROM player_performance pp
                    JOIN players p ON pp.player_id = p.player_id
                    JOIN teams t ON pp.team_id = t.team_id
                    WHERE pp.championship_id = ? AND pp.matchday = ?
                    ORDER BY pp.points DESC
                    LIMIT 10
                '''
            cursor.execute(top_players_sql, (championship_id, matchday))
            top_players = []
            for row in cursor.fetchall():
                top_players.append({
                    "player_id": row[0],
                    "player_name": row[1],
                    "points": row[2],
                    "team_name": row[3]
                })
            
            return {
                "matchday": matchday,
                "current_standings": current_standings,
                "previous_standings": previous_standings,
                "best_players": best_players,
                "top_players": top_players
            }
    
    def get_dream_team_bonus_stats(self, championship_id: str) -> Dict[str, Dict[str, int]]:
        """Return counts of dream-team appearances and MVP awards per team."""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    SELECT tr.team_id,
                           SUM(CASE WHEN dt.is_mvp THEN 0 ELSE 1 END) AS ideal_team_count,
                           SUM(CASE WHEN dt.is_mvp THEN 1 ELSE 0 END) AS mvp_count
                    FROM dream_teams_mvps dt
                    JOIN team_rosters tr
                      ON dt.championship_id = tr.championship_id
                     AND dt.matchday = tr.matchday
                     AND dt.player_id = tr.player_id
                    WHERE dt.championship_id = %s
                    GROUP BY tr.team_id
                '''
                params = (championship_id,)
            else:
                sql = '''
                    SELECT tr.team_id,
                           SUM(CASE WHEN dt.is_mvp THEN 0 ELSE 1 END) AS ideal_team_count,
                           SUM(CASE WHEN dt.is_mvp THEN 1 ELSE 0 END) AS mvp_count
                    FROM dream_teams_mvps dt
                    JOIN team_rosters tr
                      ON dt.championship_id = tr.championship_id
                     AND dt.matchday = tr.matchday
                     AND dt.player_id = tr.player_id
                    WHERE dt.championship_id = ?
                    GROUP BY tr.team_id
                '''
                sql = self.db.adapt_params(sql)
                params = (championship_id,)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            bonus_map: Dict[str, Dict[str, int]] = {}
            for row in rows:
                team_id = row[0]
                ideal_count = row[1] or 0
                mvp_count = row[2] or 0
                bonus_map[team_id] = {
                    "ideal_team_count": ideal_count,
                    "mvp_count": mvp_count,
                }

            return bonus_map

    def _ensure_schema_updates(self):
        """Ensure new tables/indexes exist without requiring a full reset."""
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)

                create_stats_sql = self.db.adapt_sql('''
                    CREATE TABLE IF NOT EXISTS player_championship_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        championship_id TEXT NOT NULL,
                        player_id TEXT NOT NULL,
                        owner_team_id TEXT,
                        owner_team_name TEXT,
                        owner_user_id TEXT,
                        clause_price INTEGER,
                        suggested_clause INTEGER,
                        average_last_five REAL,
                        average_overall REAL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(championship_id, player_id),
                        FOREIGN KEY (player_id) REFERENCES players (player_id),
                        FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
                    )
                ''')
                cursor.execute(create_stats_sql)

                cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_champ_stats_champ_player ON player_championship_stats(championship_id, player_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_champ_stats_owner ON player_championship_stats(owner_team_id)")

                create_odds_sql = self.db.adapt_sql('''
                    CREATE TABLE IF NOT EXISTS match_odds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        championship_id TEXT NOT NULL,
                        match_id TEXT NOT NULL,
                        round_id TEXT,
                        matchday INTEGER,
                        match_date TIMESTAMP,
                        home_team_id TEXT,
                        home_team_name TEXT,
                        away_team_id TEXT,
                        away_team_name TEXT,
                        odds_home REAL,
                        odds_draw REAL,
                        odds_away REAL,
                        best_bookmaker_home TEXT,
                        best_bookmaker_draw TEXT,
                        best_bookmaker_away TEXT,
                        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(championship_id, match_id),
                        FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
                    )
                ''')
                cursor.execute(create_odds_sql)

                cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_odds_champ_matchday ON match_odds(championship_id, matchday)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_odds_round ON match_odds(round_id)")

                create_articles_sql = self.db.adapt_sql('''
                    CREATE TABLE IF NOT EXISTS matchday_articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        championship_id TEXT NOT NULL,
                        matchday INTEGER NOT NULL,
                        article TEXT NOT NULL,
                        summary_json TEXT,
                        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(championship_id, matchday),
                        FOREIGN KEY (championship_id) REFERENCES championships (championship_id)
                    )
                ''')
                cursor.execute(create_articles_sql)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_matchday_articles_champ_matchday ON matchday_articles(championship_id, matchday)")
        except Exception as e:
            logger.warning(f"Could not ensure schema updates: {e}")

    def save_player_championship_stats(self, championship_id: str, player_stats: List[Dict]):
        """Persist clause and average metrics for players in a championship (batch)."""
        if not player_stats:
            return
        
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            # Ensure championship exists so FK constraints succeed
            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)
            
            now = datetime.now()
            values = []
            
            for data in player_stats:
                player_id = data.get("player_id")
                if not player_id:
                    continue
                
                owner_team_id = data.get("owner_team_id") or None
                owner_team_name = data.get("owner_team_name") or (owner_team_id if owner_team_id else "Free Agent")
                owner_user_id = data.get("owner_user_id") or owner_team_id
                
                clause_price = data.get("clause_price")
                suggested_clause = data.get("suggested_clause")
                average_last_five = data.get("average_last_five")
                average_overall = data.get("average_overall")
                
                try:
                    clause_price = int(clause_price) if clause_price is not None else None
                except (TypeError, ValueError):
                    clause_price = None
                try:
                    suggested_clause = int(suggested_clause) if suggested_clause is not None else None
                except (TypeError, ValueError):
                    suggested_clause = None
                try:
                    average_last_five = float(average_last_five) if average_last_five is not None else None
                except (TypeError, ValueError):
                    average_last_five = None
                try:
                    average_overall = float(average_overall) if average_overall is not None else None
                except (TypeError, ValueError):
                    average_overall = None
                
                values.append((
                    championship_id, player_id, owner_team_id, owner_team_name,
                    owner_user_id, clause_price, suggested_clause,
                    average_last_five, average_overall, now
                ))
            
            if not values:
                return
            
            if self.db.db_type in ["postgresql", "postgres"]:
                from psycopg2.extras import execute_values
                raw_cursor = cursor._cursor if hasattr(cursor, '_cursor') else cursor
                execute_values(raw_cursor, '''
                    INSERT INTO player_championship_stats
                    (championship_id, player_id, owner_team_id, owner_team_name, owner_user_id,
                     clause_price, suggested_clause, average_last_five, average_overall, updated_at)
                    VALUES %s
                    ON CONFLICT (championship_id, player_id) DO UPDATE SET
                        owner_team_id = EXCLUDED.owner_team_id,
                        owner_team_name = EXCLUDED.owner_team_name,
                        owner_user_id = EXCLUDED.owner_user_id,
                        clause_price = EXCLUDED.clause_price,
                        suggested_clause = EXCLUDED.suggested_clause,
                        average_last_five = EXCLUDED.average_last_five,
                        average_overall = EXCLUDED.average_overall,
                        updated_at = EXCLUDED.updated_at
                ''', values, page_size=100)
            else:
                sql = '''
                    INSERT OR REPLACE INTO player_championship_stats
                    (championship_id, player_id, owner_team_id, owner_team_name, owner_user_id,
                     clause_price, suggested_clause, average_last_five, average_overall, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                cursor.executemany(sql, values)
            
            logger.info(f"Saved {len(values)} player championship stats for {championship_id}")
    
    def get_clausulable_player_stats(self, championship_id: str) -> List[Dict]:
        """Retrieve stored clause metrics for clausulable player ranking."""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            
            sql = '''
                SELECT 
                    pcs.player_id,
                    COALESCE(p.name, 'Unknown') AS player_name,
                    pcs.owner_team_id,
                    pcs.owner_team_name,
                    pcs.owner_user_id,
                    pcs.clause_price,
                    pcs.suggested_clause,
                    pcs.average_last_five,
                    pcs.average_overall
                FROM player_championship_stats pcs
                LEFT JOIN players p ON p.player_id = pcs.player_id
                WHERE pcs.championship_id = ?
            '''
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            rows = cursor.fetchall()
        
        results: List[Dict] = []
        for row in rows:
            results.append({
                "player_id": row[0],
                "player_name": row[1],
                "owner_team_id": row[2],
                "owner_team_name": row[3],
                "owner_user_id": row[4],
                "clause_price": row[5],
                "suggested_clause": row[6],
                "average_last_five": row[7],
                "average_overall": row[8]
            })
        return results

    def save_match_odds(self, championship_id: str, matches: List[Dict], round_id: str = None, matchday: int = None):
        """Persist betting odds for upcoming matches"""
        if not matches:
            return

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            self.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = '''
                    INSERT INTO match_odds (
                        championship_id, match_id, round_id, matchday, match_date,
                        home_team_id, home_team_name, away_team_id, away_team_name,
                        odds_home, odds_draw, odds_away,
                        best_bookmaker_home, best_bookmaker_draw, best_bookmaker_away,
                        fetched_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (championship_id, match_id) DO UPDATE SET
                        round_id = EXCLUDED.round_id,
                        matchday = EXCLUDED.matchday,
                        match_date = EXCLUDED.match_date,
                        home_team_id = EXCLUDED.home_team_id,
                        home_team_name = EXCLUDED.home_team_name,
                        away_team_id = EXCLUDED.away_team_id,
                        away_team_name = EXCLUDED.away_team_name,
                        odds_home = EXCLUDED.odds_home,
                        odds_draw = EXCLUDED.odds_draw,
                        odds_away = EXCLUDED.odds_away,
                        best_bookmaker_home = EXCLUDED.best_bookmaker_home,
                        best_bookmaker_draw = EXCLUDED.best_bookmaker_draw,
                        best_bookmaker_away = EXCLUDED.best_bookmaker_away,
                        fetched_at = EXCLUDED.fetched_at
                '''
            else:
                sql = '''
                    INSERT OR REPLACE INTO match_odds (
                        championship_id, match_id, round_id, matchday, match_date,
                        home_team_id, home_team_name, away_team_id, away_team_name,
                        odds_home, odds_draw, odds_away,
                        best_bookmaker_home, best_bookmaker_draw, best_bookmaker_away,
                        fetched_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                sql = self.db.adapt_params(sql)

            now = datetime.now()

            for match in matches:
                match_id = match.get("id") or match.get("_id")
                if not match_id:
                    continue

                match_date_str = match.get("date") or match.get("matchDate")
                match_date = None
                if match_date_str:
                    try:
                        match_date = datetime.fromisoformat(match_date_str.replace("Z", "+00:00"))
                    except Exception:
                        match_date = None

                odds_info = match.get("odds", {})
                sels = odds_info.get("sels", []) if isinstance(odds_info, dict) else []

                odds_home = odds_draw = odds_away = None
                bookmaker_home = bookmaker_draw = bookmaker_away = None

                for sel in sels:
                    selection_name = sel.get("sn", "").lower()
                    odds_list = sel.get("odds", [])
                    if not odds_list:
                        continue
                    best = max(odds_list, key=lambda o: o.get("c", 0) or 0)
                    price = best.get("c") or best.get("f")
                    bookmaker = best.get("bid")
                    if "draw" in selection_name or selection_name in ("empate", "tie"):
                        odds_draw = price
                        bookmaker_draw = bookmaker
                    elif selection_name == match.get("homeTeam", {}).get("name", "").lower() or sel.get("ssn") == "1":
                        odds_home = price
                        bookmaker_home = bookmaker
                    else:
                        odds_away = price
                        bookmaker_away = bookmaker

                cursor.execute(sql, (
                    championship_id,
                    match_id,
                    round_id or match.get("roundId"),
                    matchday,
                    match_date,
                    match.get("homeTeam", {}).get("id"),
                    match.get("homeTeam", {}).get("name"),
                    match.get("awayTeam", {}).get("id"),
                    match.get("awayTeam", {}).get("name"),
                    odds_home,
                    odds_draw,
                    odds_away,
                    bookmaker_home,
                    bookmaker_draw,
                    bookmaker_away,
                    now
                ))

    def get_match_odds(self, championship_id: str, matchday: Optional[int] = None, upcoming_only: bool = False) -> List[Dict]:
        """Retrieve stored match odds, optionally filtered by matchday or future date"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            base_sql = '''
                SELECT match_id, round_id, matchday, match_date,
                       home_team_id, home_team_name,
                       away_team_id, away_team_name,
                       odds_home, odds_draw, odds_away,
                       best_bookmaker_home, best_bookmaker_draw, best_bookmaker_away,
                       fetched_at
                FROM match_odds
                WHERE championship_id = ?
            '''
            params: List[Any] = [championship_id]

            if matchday is not None:
                base_sql += " AND matchday = ?"
                params.append(matchday)

            if upcoming_only:
                base_sql += " AND (match_date IS NULL OR match_date >= ? )"
                params.append(datetime.now())

            base_sql += " ORDER BY match_date"
            if self.db.db_type in ["postgresql", "postgres"]:
                base_sql += " NULLS LAST"
            base_sql = self.db.adapt_params(base_sql)

            cursor.execute(base_sql, tuple(params))
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "match_id": row[0],
                "round_id": row[1],
                "matchday": row[2],
                "match_date": row[3],
                "home_team_id": row[4],
                "home_team_name": row[5],
                "away_team_id": row[6],
                "away_team_name": row[7],
                "odds_home": row[8],
                "odds_draw": row[9],
                "odds_away": row[10],
                "best_bookmaker_home": row[11],
                "best_bookmaker_draw": row[12],
                "best_bookmaker_away": row[13],
                "fetched_at": row[14]
            })
        return results

    def get_latest_matchday(self, championship_id: str) -> Optional[int]:
        """Return the latest matchday available in team_standings"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = "SELECT MAX(matchday) FROM team_standings WHERE championship_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                return int(row[0])
        return None

    def get_team_standings_history(self, championship_id: str, window: Optional[int] = None) -> List[Dict]:
        """Return standings history for each team, optionally limited to last `window` matchdays"""
        max_matchday = self.get_latest_matchday(championship_id)
        params: List[Any] = [championship_id]
        condition = ""
        if window and max_matchday:
            min_matchday = max_matchday - window + 1
            condition = " AND matchday >= ?"
            params.append(min_matchday)

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f'''
                SELECT team_id, matchday, position, points, points_this_matchday, team_value
                FROM team_standings
                WHERE championship_id = ?{condition}
                ORDER BY team_id, matchday
            '''
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        history = []
        for row in rows:
            history.append({
                "team_id": row[0],
                "matchday": row[1],
                "position": row[2],
                "points": row[3],
                "points_this_matchday": row[4],
                "team_value": row[5]
            })
        return history

    def get_player_performance_history(self, championship_id: str, player_ids: Optional[List[str]] = None,
                                        window: Optional[int] = None) -> List[Dict]:
        """Return player performance records filtered by players and limited matchdays"""
        max_matchday = self.get_latest_matchday(championship_id)
        params: List[Any] = [championship_id]
        filters = []

        if player_ids:
            placeholders = ",".join(["?"] * len(player_ids))
            filters.append(f"player_id IN ({placeholders})")
            params.extend(player_ids)

        if window and max_matchday:
            min_matchday = max_matchday - window + 1
            filters.append("matchday >= ?")
            params.append(min_matchday)

        filter_clause = " AND " + " AND ".join(filters) if filters else ""

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f'''
                SELECT player_id, team_id, matchday, points, value, was_best_player
                FROM player_performance
                WHERE championship_id = ?{filter_clause}
                ORDER BY player_id, matchday
            '''
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        performances = []
        for row in rows:
            performances.append({
                "player_id": row[0],
                "team_id": row[1],
                "matchday": row[2],
                "points": row[3],
                "value": row[4],
                "was_best_player": bool(row[5]) if row[5] is not None else False
            })
        return performances

    def get_transactions_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        """Return raw transactions optionally filtered by recent days"""
        params: List[Any] = [championship_id]
        condition = ""
        if days:
            condition = " AND transaction_date >= ?"
            params.append(datetime.now() - timedelta(days=days))

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f'''
                SELECT api_transaction_id, player_id, seller_user_id, buyer_user_id,
                       seller_team_id, buyer_team_id, price, transaction_date, matchday
                FROM transactions
                WHERE championship_id = ?{condition}
            '''
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        items = []
        for row in rows:
            items.append({
                "transaction_id": row[0],
                "player_id": row[1],
                "seller_user_id": row[2],
                "buyer_user_id": row[3],
                "seller_team_id": row[4],
                "buyer_team_id": row[5],
                "price": row[6],
                "transaction_date": row[7],
                "matchday": row[8]
            })
        return items

    def get_clauses_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        """Return raw clause payments"""
        params: List[Any] = [championship_id]
        condition = ""
        if days:
            condition = " AND created_date >= ?"
            params.append(datetime.now() - timedelta(days=days))

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f'''
                SELECT payer_user_id, payer_team_id, receiver_user_id, receiver_team_id,
                       amount, created_date, player_name
                FROM clauses
                WHERE championship_id = ?{condition}
            '''
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        clauses = []
        for row in rows:
            clauses.append({
                "payer_user_id": row[0],
                "payer_team_id": row[1],
                "receiver_user_id": row[2],
                "receiver_team_id": row[3],
                "amount": row[4],
                "created_date": row[5],
                "player_name": row[6]
            })
        return clauses

    def get_team_by_id(self, team_id: str) -> Optional[Dict]:
        if not team_id:
            return None

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = "SELECT team_id, user_id, team_name FROM teams WHERE team_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (team_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "team_id": row[0],
            "user_id": row[1],
            "team_name": row[2]
        }

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        if not user_id:
            return None

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = "SELECT user_id, username FROM users WHERE user_id = ?"
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "user_id": row[0],
            "username": row[1]
        }

    def get_player_by_id(self, player_id: str) -> Optional[Dict]:
        if not player_id:
            return None

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = """
                SELECT player_id, name, role, real_team_name, real_team_id, photo_url
                FROM players
                WHERE player_id = ?
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (player_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "player_id": row[0],
            "name": row[1],
            "role": row[2],
            "team": row[3],
            "team_id": row[4],
            "photo_url": row[5]
        }

    def get_free_agent_candidates(self, championship_id: str) -> List[Dict]:
        """Return players without owner based on player_championship_stats"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = '''
                SELECT pcs.player_id, p.name, pcs.clause_price, pcs.suggested_clause,
                       pcs.average_last_five, pcs.average_overall
                FROM player_championship_stats pcs
                LEFT JOIN players p ON p.player_id = pcs.player_id
                WHERE pcs.championship_id = ? AND (pcs.owner_team_id IS NULL OR pcs.owner_team_id = '')
            '''
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            rows = cursor.fetchall()

        players = []
        for row in rows:
            players.append({
                "player_id": row[0],
                "name": row[1],
                "clause_price": row[2],
                "suggested_clause": row[3],
                "average_last_five": row[4],
                "average_overall": row[5]
            })
        return players

    def get_player_streak_data(self, championship_id: str, min_matchday: Optional[int] = None) -> List[Dict]:
        """Return player performance ordered by matchday for streak calculations"""
        params: List[Any] = [championship_id]
        condition = ""
        if min_matchday:
            condition = " AND matchday >= ?"
            params.append(min_matchday)

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f'''
                SELECT player_id, matchday, points
                FROM player_performance
                WHERE championship_id = ?{condition}
                ORDER BY player_id, matchday
            '''
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                "player_id": row[0],
                "matchday": row[1],
                "points": row[2]
            })
        return data
