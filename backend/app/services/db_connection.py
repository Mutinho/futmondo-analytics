#!/usr/bin/env python3
"""
Database Connection Manager - PostgreSQL/Neon connection abstraction.

Historical note (FR14.1): this manager previously abstracted SQLite, Turso
(LibSQL) and PostgreSQL. Production now targets a single engine — PostgreSQL/Neon
via ``DATABASE_URL`` — so the SQLite and Turso branches were removed as dead code.
The in-memory SQLite test fake in ``conftest.py`` is a separate, self-contained
double and is unaffected by this cleanup.
"""

import logging
from contextlib import contextmanager
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DBConnection:
    """Database connection manager for PostgreSQL/Neon."""

    def __init__(self):
        from app.core.config import DATABASE_PATH, DATABASE_URL

        # Production targets PostgreSQL/Neon exclusively (resolved from
        # DATABASE_URL). db_type is retained as a stable attribute because
        # callers and the SQL-adaptation helpers still read it.
        self.db_type = "postgresql"

        # Local cache path (kept for photo_service / data_manager_v2 which read
        # DATABASE_PATH); not a database engine selector.
        self.db_path = DATABASE_PATH
        self._pool = None  # Connection pool for PostgreSQL

        self._init_postgresql(DATABASE_URL)

    def _init_postgresql(self, database_url):
        """Initialize PostgreSQL connection with a threaded connection pool."""
        import psycopg2

        self.connection_string = database_url
        self.connector = psycopg2

        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                5, 20, database_url
            )
            logger.info("✅ PostgreSQL threaded connection pool created (5-20 connections)")
        except Exception as e:
            # Reclassified (FR3.2.2 / BR1.6): RECOVERABLE. Failing to build the
            # pool is not fatal — fall back to direct connections and continue.
            # The subsequent _test_connection() still fails FATALLY if the DB is
            # truly unreachable, so this degrade does not mask a dead database.
            logger.warning(f"Could not create connection pool, using direct connections: {e}")
            self._pool = None

        self._test_connection()
        logger.info("✅ Using PostgreSQL database")

    def _test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = self.get_cursor(conn)
                cursor.execute("SELECT 1;")
                logger.info(f"✅ {self.db_type.capitalize()} connection successful")
        except Exception as e:
            # Reclassified (FR3.2.2 / BR1.6): FATAL. A DB that fails the liveness
            # probe cannot serve requests — log and PROPAGATE (fail fast/clean),
            # never degrade to a warning. Behaviour preserved from the original.
            logger.error(f"❌ {self.db_type.upper()} connection failed: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Get a database connection (context manager).

        Transactional failure classification (FR3.2.2 / BR1.6): FATAL. On any
        exception inside the ``with`` block the transaction is rolled back and
        the exception is re-raised — never swallowed — so no partial/half-written
        data survives (NFR2). This rollback()+raise semantics is pre-existing and
        deliberately UNCHANGED by the error-layer hardening.
        """
        if self._pool:
            max_attempts = 3
            conn = None
            for attempt in range(max_attempts):
                conn = self._pool.getconn()
                try:
                    conn.cursor().execute("SELECT 1")
                    break  # Connection is alive
                except Exception:
                    # Connection is dead — discard and retry
                    try:
                        self._pool.putconn(conn, close=True)
                    except Exception:
                        logger.debug(
                            "failed to return dead connection to pool "
                            "(attempt %d/%d); discarding",
                            attempt + 1,
                            max_attempts,
                            exc_info=True,
                        )
                    conn = None
                    if attempt == max_attempts - 1:
                        # All pool connections dead — recreate pool
                        logger.warning("All pool connections dead, recreating pool...")
                        try:
                            self._pool.closeall()
                        except Exception:
                            logger.warning(
                                "failed to close exhausted pool before "
                                "recreating; proceeding with a fresh pool",
                                exc_info=True,
                            )
                        import psycopg2.pool
                        self._pool = psycopg2.pool.ThreadedConnectionPool(
                            5, 20, self.connection_string
                        )
                        conn = self._pool.getconn()
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                self._pool.putconn(conn)
        else:
            conn = self.connector.connect(self.connection_string)
            try:
                yield conn
                conn.commit()
            except Exception:
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
        """Adapt SQL DDL syntax for PostgreSQL"""
        sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        sql = sql.replace("AUTOINCREMENT", "")
        sql = sql.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
        return sql

    def get_last_insert_id(self, cursor, table_name: str) -> Any:
        """Get last inserted ID via the RETURNING row (PostgreSQL)"""
        return cursor.fetchone()[0] if cursor.description else None

    def adapt_params(self, sql: str) -> str:
        """Adapt SQL parameter placeholders (? → %s for PostgreSQL)"""
        if "%s" in sql or sql.count("?") == 0:
            return sql
        return sql.replace("?", "%s")

    def sync(self):
        """No-op retained for API compatibility with prior multi-engine callers."""
        return None


# --- Singleton ---
_db_instance: Optional[DBConnection] = None


def get_db() -> DBConnection:
    """Get or create the global DBConnection singleton."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DBConnection()
    return _db_instance
