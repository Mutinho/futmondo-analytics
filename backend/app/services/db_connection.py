#!/usr/bin/env python3
"""
Database Connection Manager - Abstracts SQLite, PostgreSQL, and Turso (LibSQL) connections
"""

import os
import logging
from typing import Optional, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DBConnection:
    """Database connection manager supporting SQLite, PostgreSQL, and Turso"""
    
    def __init__(self):
        from app.core.config import (
            DATABASE_TYPE, DATABASE_PATH,
            POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, DATABASE_URL
        )
        
        # If DATABASE_URL is provided (Railway), use it and set type to postgresql
        if DATABASE_URL:
            self.db_type = "postgresql"
        else:
            self.db_type = DATABASE_TYPE.lower() if DATABASE_TYPE else "sqlite"
        
        self.db_path = DATABASE_PATH
        self._pool = None  # Connection pool for PostgreSQL
        
        if self.db_type == "turso":
            self._init_turso()
        elif self.db_type == "postgresql" or self.db_type == "postgres":
            self._init_postgresql(DATABASE_URL, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)
        else:
            self._init_sqlite()
    
    def _init_turso(self):
        """Initialize Turso via libsql embedded replica (local reads, remote writes)"""
        from app.core.config import TURSO_DATABASE_URL, TURSO_AUTH_TOKEN
        import libsql_experimental as libsql
        
        self.connector = libsql
        self.turso_url = TURSO_DATABASE_URL
        self.turso_token = TURSO_AUTH_TOKEN
        
        # Local replica file inside the data volume
        self._local_replica_path = "/app/data/turso_replica.db"
        
        # Create persistent connection with embedded replica
        self._turso_conn = libsql.connect(
            self._local_replica_path,
            sync_url=self.turso_url,
            auth_token=self.turso_token
        )
        
        # Initial sync: pull remote data into local replica
        self._turso_conn.sync()
        logger.info(f"✅ Using Turso embedded replica: {self.turso_url} → {self._local_replica_path}")
    
    def _init_postgresql(self, database_url, host, port, db, user, password):
        """Initialize PostgreSQL connection with connection pool"""
        import psycopg2
        from psycopg2 import pool
        
        if database_url:
            connection_string = database_url
        else:
            connection_string = (
                f"host={host} port={port} "
                f"dbname={db} user={user} password={password}"
            )
        
        self.connection_string = connection_string
        self.connector = psycopg2
        
        try:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                2, 10, connection_string
            )
            logger.info("✅ PostgreSQL connection pool created (2-10 connections)")
        except Exception as e:
            logger.warning(f"Could not create connection pool, using direct connections: {e}")
            self._pool = None
        
        self._test_connection()
        logger.info("✅ Using PostgreSQL database")
    
    def _init_sqlite(self):
        """Initialize SQLite connection"""
        import sqlite3
        self.connector = sqlite3
        logger.info(f"✅ Using SQLite database: {self.db_path}")
    
    def _test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = self.get_cursor(conn)
                cursor.execute("SELECT 1;")
                logger.info(f"✅ {self.db_type.capitalize()} connection successful")
        except Exception as e:
            logger.error(f"❌ {self.db_type.upper()} connection failed: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection (context manager)"""
        if self.db_type == "turso":
            # Embedded replica: use persistent connection
            # Reads are local (fast), writes go to remote automatically
            try:
                yield self._turso_conn
                self._turso_conn.commit()
            except Exception as e:
                self._turso_conn.rollback()
                raise
        elif self.db_type in ["postgresql", "postgres"]:
            if self._pool:
                conn = self._pool.getconn()
                try:
                    yield conn
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise
                finally:
                    self._pool.putconn(conn)
            else:
                conn = self.connector.connect(self.connection_string)
                try:
                    yield conn
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
        else:
            # SQLite
            conn = self.connector.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL;")
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def get_cursor(self, conn):
        """Get a cursor from a connection"""
        return conn.cursor()
    
    def execute_sql(self, sql: str, params: Optional[tuple] = None):
        """Execute SQL and return cursor (for compatibility)"""
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor
    
    def adapt_sql(self, sql: str) -> str:
        """Adapt SQL syntax differences between databases"""
        if self.db_type in ["postgresql", "postgres"]:
            sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            sql = sql.replace("AUTOINCREMENT", "")
            sql = sql.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
        # Turso is SQLite-compatible — no adaptation needed
        return sql
    
    def get_last_insert_id(self, cursor, table_name: str) -> Any:
        """Get last inserted ID (database-specific)"""
        if self.db_type in ["postgresql", "postgres"]:
            return cursor.fetchone()[0] if cursor.description else None
        else:
            # SQLite and Turso both support lastrowid
            return cursor.lastrowid
    
    def adapt_params(self, sql: str) -> str:
        """Adapt SQL parameter placeholders (? for SQLite/Turso, %s for PostgreSQL)"""
        if self.db_type in ["postgresql", "postgres"]:
            if "%s" in sql or sql.count("?") == 0:
                return sql
            return sql.replace("?", "%s")
        # SQLite and Turso both use ?
        return sql
    
    def sync(self):
        """Sync Turso embedded replica with remote (no-op for other backends)"""
        if self.db_type == "turso" and hasattr(self, '_turso_conn'):
            self._turso_conn.sync()
            logger.info("🔄 Turso replica synced")



# --- Singleton ---
_db_instance: Optional[DBConnection] = None


def get_db() -> DBConnection:
    """Get or create the global DBConnection singleton."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DBConnection()
    return _db_instance
