"""Infrastructure adapter for ``schema-lifecycle`` — the only module with SQL (BR1.3).

Hosts the raw schema DDL and championship-bootstrap SQL formerly inline in the
``DataManagerV2`` lifecycle methods, moved **verbatim** including the engine
branch (BR1.2/FR1.4) and the legacy bare ``except`` paths (BR3.2). The facade's
``__init__`` stays on the facade (object construction) and delegates its
``_init_database`` / ``_ensure_schema_updates`` calls here. Internal calls between
these methods (``reset_database`` → ``init_database``; ``ensure_championship_exists``
→ ``ensure_championship_in_transaction``) stay local to this adapter so there is
no nested facade delegation. Byte-for-byte identical behavior (BR3.1).
"""

import logging
from datetime import datetime
from typing import Any, Optional

from app.services.data_manager.schema_lifecycle.domain.ports import (
    SchemaLifecycleDataPort,
)

logger = logging.getLogger(__name__)


class SchemaLifecycleAdapter(SchemaLifecycleDataPort):
    """Adapt the schema-lifecycle SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def init_database(self):
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
            sql = self.db.adapt_sql("""
                CREATE TABLE users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            drop_and_create_table("users", sql, "users")

            # Teams - User teams in championship
            sql = self.db.adapt_sql("""
                CREATE TABLE teams (
                    team_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    team_name TEXT NOT NULL,
                    initial_budget INTEGER DEFAULT 270000000,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            drop_and_create_table("teams", sql, "teams")

            # Players - Football players
            sql = self.db.adapt_sql("""
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
            """)
            drop_and_create_table("players", sql, "players")

            # Championships - Championship metadata
            sql = self.db.adapt_sql("""
                CREATE TABLE championships (
                    championship_id TEXT PRIMARY KEY,
                    name TEXT,
                    season_start DATE,
                    season_end DATE,
                    total_matchdays INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            drop_and_create_table("championships", sql, "championships")

            # ============================================================
            # FACT TABLES (Time-Series Data - Historical Records)
            # ============================================================

            # Team standings - Historical standings per matchday
            sql = self.db.adapt_sql("""
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
            """)
            drop_and_create_table("team_standings", sql, "team_standings")

            # Player performance - Player points per matchday per team
            sql = self.db.adapt_sql("""
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
            """)
            drop_and_create_table("player_performance", sql, "player_performance")

            # Transactions - Historical transfer records
            sql = self.db.adapt_sql("""
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
            """)
            drop_and_create_table("transactions", sql, "transactions")

            # Punishments and Bonuses - Admin actions (punish/bonus)
            sql = self.db.adapt_sql("""
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
            """)
            drop_and_create_table("punishments_bonuses", sql, "punishments_bonuses")

            # Clauses - Player release clauses
            sql = self.db.adapt_sql("""
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
            """)
            drop_and_create_table("clauses", sql, "clauses")

            # Team rosters - Historical roster changes
            sql = self.db.adapt_sql("""
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
            """)
            drop_and_create_table("team_rosters", sql, "team_rosters")

            # Dream teams and MVPs - Historical dream teams and MVPs per round
            sql = self.db.adapt_sql("""
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
            """)
            drop_and_create_table("dream_teams_mvps", sql, "dream_teams_mvps")

            # Sync metadata - Track last sync for each data type
            sql = self.db.adapt_sql("""
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
            """)
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
                        if table.startswith("pg_") or table.startswith("sqlite_"):
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
        self.init_database()
        logger.info("✅ Database reset complete - new schema created")

    def ensure_championship_exists(
        self, championship_id: str, name: str = None, conn=None, cursor=None
    ):
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
                self.ensure_championship_in_transaction(cursor, championship_id, name)
                conn.commit()
        else:
            # Use existing connection/cursor (same transaction)
            self.ensure_championship_in_transaction(cursor, championship_id, name)

    def ensure_championship_in_transaction(self, cursor, championship_id: str, name: str = None):
        """Internal helper to ensure championship exists using provided cursor"""
        # Check if championship exists
        sql = "SELECT championship_id FROM championships WHERE championship_id = ?"
        sql = self.db.adapt_params(sql)
        cursor.execute(sql, (championship_id,))
        exists = cursor.fetchone()

        if not exists:
            # Create championship record
            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    INSERT INTO championships (championship_id, name, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (championship_id) DO NOTHING
                """
            else:
                sql = """
                    INSERT OR IGNORE INTO championships (championship_id, name, created_at)
                    VALUES (?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

            cursor.execute(sql, (championship_id, name or championship_id, datetime.now()))
            logger.debug(f"Created championship record: {championship_id}")

    def ensure_schema_updates(self):
        """Ensure new tables/indexes exist without requiring a full reset."""
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)

                create_stats_sql = self.db.adapt_sql("""
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
                """)
                cursor.execute(create_stats_sql)

                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_player_champ_stats_champ_player ON player_championship_stats(championship_id, player_id)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_player_champ_stats_owner ON player_championship_stats(owner_team_id)"
                )

                create_odds_sql = self.db.adapt_sql("""
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
                """)
                cursor.execute(create_odds_sql)

                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_match_odds_champ_matchday ON match_odds(championship_id, matchday)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_match_odds_round ON match_odds(round_id)"
                )

                create_articles_sql = self.db.adapt_sql("""
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
                """)
                cursor.execute(create_articles_sql)
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_matchday_articles_champ_matchday ON matchday_articles(championship_id, matchday)"
                )
                # Migration: add dream_team_prize to team_prizes
                try:
                    cursor.execute(
                        "ALTER TABLE team_prizes ADD COLUMN IF NOT EXISTS dream_team_prize INTEGER DEFAULT 0"
                    )
                except Exception:
                    pass  # Column may already exist or table may not exist yet
        except Exception as e:
            logger.warning(f"Could not ensure schema updates: {e}")
