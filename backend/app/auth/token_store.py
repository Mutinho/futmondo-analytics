"""
Refresh token storage — persists tokens in DB for revocation support.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from app.services.db_connection import get_db

logger = logging.getLogger(__name__)


def init_auth_tables():
    """Create auth-related tables if they don't exist."""
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        if db.db_type in ["postgresql", "postgres"]:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_users (
                    id TEXT PRIMARY KEY,
                    futmondo_email TEXT UNIQUE NOT NULL,
                    futmondo_user_id TEXT,
                    display_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES app_users(id),
                    expires_at TIMESTAMP NOT NULL,
                    revoked BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_championships (
                    user_id TEXT NOT NULL REFERENCES app_users(id),
                    championship_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    initial_budget BIGINT DEFAULT 200000000,
                    has_clauses BOOLEAN DEFAULT FALSE,
                    excluded_teams TEXT DEFAULT '[]',
                    PRIMARY KEY (user_id, championship_id)
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_users (
                    id TEXT PRIMARY KEY,
                    futmondo_email TEXT UNIQUE NOT NULL,
                    futmondo_user_id TEXT,
                    display_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    revoked INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_championships (
                    user_id TEXT NOT NULL,
                    championship_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    initial_budget INTEGER DEFAULT 200000000,
                    has_clauses INTEGER DEFAULT 0,
                    excluded_teams TEXT DEFAULT '[]',
                    PRIMARY KEY (user_id, championship_id)
                )
            ''')
        
        logger.info("Auth tables ensured")


def save_refresh_token(token_hash: str, user_id: str, expires_at: datetime):
    """Store a refresh token hash."""
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        if db.db_type in ["postgresql", "postgres"]:
            cursor.execute('''
                INSERT INTO refresh_tokens (token_hash, user_id, expires_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (token_hash) DO NOTHING
            ''', (token_hash, user_id, expires_at))
        else:
            cursor.execute('''
                INSERT OR IGNORE INTO refresh_tokens (token_hash, user_id, expires_at)
                VALUES (?, ?, ?)
            ''', (token_hash, user_id, expires_at))


def is_refresh_token_valid(token_hash: str) -> bool:
    """Check if a refresh token is valid (exists, not revoked, not expired)."""
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = "SELECT revoked, expires_at FROM refresh_tokens WHERE token_hash = ?"
        sql = db.adapt_params(sql)
        cursor.execute(sql, (token_hash,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        revoked = row[0]
        expires_at = row[1]
        
        if revoked:
            return False
        
        # Check expiry
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        
        if expires_at and datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc) if expires_at.tzinfo is None else expires_at:
            return False
        
        return True


def revoke_refresh_token(token_hash: str):
    """Revoke a specific refresh token."""
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        if db.db_type in ["postgresql", "postgres"]:
            cursor.execute("UPDATE refresh_tokens SET revoked = TRUE WHERE token_hash = %s", (token_hash,))
        else:
            cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE token_hash = ?", (token_hash,))


def revoke_all_user_tokens(user_id: str):
    """Revoke all refresh tokens for a user (logout everywhere)."""
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        if db.db_type in ["postgresql", "postgres"]:
            cursor.execute("UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = %s", (user_id,))
        else:
            cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE user_id = ?", (user_id,))


def upsert_user(user_id: str, email: str, futmondo_user_id: str = "", display_name: str = ""):
    """Create or update an app user."""
    db = get_db()
    now = datetime.now()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        if db.db_type in ["postgresql", "postgres"]:
            cursor.execute('''
                INSERT INTO app_users (id, futmondo_email, futmondo_user_id, display_name, last_login)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    futmondo_user_id = EXCLUDED.futmondo_user_id,
                    display_name = EXCLUDED.display_name,
                    last_login = EXCLUDED.last_login
            ''', (user_id, email, futmondo_user_id, display_name, now))
        else:
            cursor.execute('''
                INSERT OR REPLACE INTO app_users (id, futmondo_email, futmondo_user_id, display_name, last_login)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, email, futmondo_user_id, display_name, now))


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email."""
    db = get_db()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = "SELECT id, futmondo_email, futmondo_user_id, display_name FROM app_users WHERE futmondo_email = ?"
        sql = db.adapt_params(sql)
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "futmondo_user_id": row[2],
                "display_name": row[3],
            }
        return None
