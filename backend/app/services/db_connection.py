#!/usr/bin/env python3
"""
Database Connection Manager - Abstracts SQLite and PostgreSQL connections
"""

import os
import logging
from typing import Optional, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DBConnection:
    """Database connection manager supporting both SQLite and PostgreSQL"""
    
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
        
        if self.db_type == "postgresql" or self.db_type == "postgres":
            import psycopg2
            from psycopg2 import pool
            
            if DATABASE_URL:
                # Railway provides DATABASE_URL in format: postgresql://user:pass@host:port/dbname
                connection_string = DATABASE_URL
            else:
                # Fallback to individual settings (for local dev)
                connection_string = (
                    f"host={POSTGRES_HOST} port={POSTGRES_PORT} "
                    f"dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}"
                )
            
            self.connection_string = connection_string
            self.connector = psycopg2
            
            # Create connection pool - EFFICIENT: reuse connections
            # minconn=2, maxconn=10 allows 2-10 concurrent connections
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
        else:
            import sqlite3
            self.db_path = DATABASE_PATH
            self.connector = sqlite3
            logger.info(f"✅ Using SQLite database: {self.db_path}")
    
    def _test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = self.get_cursor(conn)
                if self.db_type in ["postgresql", "postgres"]:
                    cursor.execute("SELECT 1;")
                    logger.info("✅ PostgreSQL connection successful")
                else:
                    cursor.execute("SELECT 1;")
                    logger.info("✅ SQLite connection successful")
        except Exception as e:
            logger.error(f"❌ {self.db_type.upper()} connection failed: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection (context manager) - EFFICIENT: uses connection pool for PostgreSQL"""
        if self.db_type in ["postgresql", "postgres"]:
            # Use connection pool if available, otherwise create direct connection
            if self._pool:
                conn = self._pool.getconn()
                try:
                    yield conn
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise
                finally:
                    self._pool.putconn(conn)  # Return connection to pool
            else:
                # Fallback: direct connection
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
            # SQLite: direct connection (connection pooling not critical)
            conn = self.connector.connect(self.db_path)
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
        """Adapt SQL syntax differences between SQLite and PostgreSQL"""
        if self.db_type in ["postgresql", "postgres"]:
            # Replace SQLite-specific syntax with PostgreSQL equivalents
            sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            sql = sql.replace("AUTOINCREMENT", "")
            sql = sql.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
            # SQLite uses TEXT, PostgreSQL uses VARCHAR or TEXT (both work)
            # Keep TEXT as is - PostgreSQL supports it
        return sql
    
    def get_last_insert_id(self, cursor, table_name: str) -> Any:
        """Get last inserted ID (database-specific)"""
        if self.db_type in ["postgresql", "postgres"]:
            # PostgreSQL: cursor.fetchone()[0] after RETURNING id
            # Or use cursor.lastrowid equivalent
            return cursor.fetchone()[0] if cursor.description else None
        else:
            return cursor.lastrowid
    
    def adapt_params(self, sql: str) -> str:
        """Adapt SQL parameter placeholders for database type (? for SQLite, %s for PostgreSQL)"""
        if self.db_type in ["postgresql", "postgres"]:
            # Replace ? with %s for PostgreSQL
            # But be careful with already converted queries
            if "%s" in sql or sql.count("?") == 0:
                return sql
            return sql.replace("?", "%s")
        return sql  # SQLite uses ?

