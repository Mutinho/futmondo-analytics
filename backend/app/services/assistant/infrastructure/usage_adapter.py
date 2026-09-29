"""Infrastructure adapter for the assistant usage budget (BR4.1-BR4.3).

This is the ONLY place with the ``assistant_usage`` raw SQL. It implements
:class:`AssistantUsagePort` and hosts the ``CREATE TABLE IF NOT EXISTS`` DDL and
the quota/record/summary statements moved verbatim from the former
``AssistantUsageTracker`` in ``assistant_service.py`` — the produced rows and the
returned tuples/dicts are identical, so the characterization tests stay green.

The DB boundary is injected via ``db_factory`` (defaulting to the global
``db_connection.get_db`` singleton) exactly like the analytics adapter, keeping
production behavior unchanged while remaining testable against the in-memory
SQLite fake.
"""

from datetime import date, datetime
from typing import Dict, Tuple

# Free-tier limits (relocated verbatim; still importable from the shim).
MONTHLY_TOKEN_LIMIT = 25_000_000  # 25M tokens/month (free tier gives ~30M)
DAILY_REQUEST_LIMIT = 50  # Max 50 questions per day


class AssistantUsageAdapter:
    """Adapt the ``assistant_usage`` table to :class:`AssistantUsagePort`."""

    def __init__(self, db_factory=None) -> None:
        """Create the adapter.

        Args:
            db_factory: A zero-arg callable returning a ``DBConnection``-like
                object (``get_connection`` / ``get_cursor`` / ``adapt_params``).
                Defaults to the global ``db_connection.get_db`` singleton, so
                production behavior is unchanged. Injectable for testing.
        """
        self._db_factory = db_factory
        self._ensure_table()

    def _get_db(self):
        if self._db_factory is not None:
            return self._db_factory()
        from app.services.db_connection import get_db

        return get_db()

    def _ensure_table(self) -> None:
        """Create usage table if it doesn't exist (idempotent, BR4.3)."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = """
                CREATE TABLE IF NOT EXISTS assistant_usage (
                    month TEXT PRIMARY KEY,
                    total_input_tokens INTEGER DEFAULT 0,
                    total_output_tokens INTEGER DEFAULT 0,
                    total_requests INTEGER DEFAULT 0,
                    updated_at TEXT
                )
            """
            cursor.execute(sql)
            conn.commit()

    def can_make_request(self) -> Tuple[bool, str]:
        """Check if we're within budget (BR4.1)."""
        current_month = datetime.now().strftime("%Y-%m")
        today = date.today().isoformat()

        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            sql = db.adapt_params(
                "SELECT total_input_tokens, total_output_tokens FROM assistant_usage WHERE month = ?"
            )
            cursor.execute(sql, (current_month,))
            row = cursor.fetchone()

            if row:
                total_tokens = (row[0] or 0) + (row[1] or 0)
                if total_tokens >= MONTHLY_TOKEN_LIMIT:
                    return (
                        False,
                        "Has alcanzado el límite mensual gratuito del asistente. Se restablece el próximo mes.",
                    )

            sql_daily = db.adapt_params(
                "SELECT total_requests FROM assistant_usage WHERE month = ?"
            )
            cursor.execute(sql_daily, (today,))
            daily_row = cursor.fetchone()

            if daily_row and (daily_row[0] or 0) >= DAILY_REQUEST_LIMIT:
                return (
                    False,
                    f"Has alcanzado el límite diario ({DAILY_REQUEST_LIMIT} preguntas). Inténtalo mañana.",
                )

        return True, ""

    def record_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Record token usage after each request (BR4.2)."""
        current_month = datetime.now().strftime("%Y-%m")
        today = date.today().isoformat()
        now = datetime.now().isoformat()

        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            # Upsert monthly
            cursor.execute(
                db.adapt_params("SELECT 1 FROM assistant_usage WHERE month = ?"),
                (current_month,),
            )
            if cursor.fetchone():
                cursor.execute(
                    db.adapt_params(
                        "UPDATE assistant_usage SET total_input_tokens = total_input_tokens + ?, "
                        "total_output_tokens = total_output_tokens + ?, "
                        "total_requests = total_requests + 1, updated_at = ? WHERE month = ?"
                    ),
                    (input_tokens, output_tokens, now, current_month),
                )
            else:
                cursor.execute(
                    db.adapt_params(
                        "INSERT INTO assistant_usage (month, total_input_tokens, "
                        "total_output_tokens, total_requests, updated_at) VALUES (?, ?, ?, 1, ?)"
                    ),
                    (current_month, input_tokens, output_tokens, now),
                )

            # Upsert daily
            cursor.execute(
                db.adapt_params("SELECT 1 FROM assistant_usage WHERE month = ?"),
                (today,),
            )
            if cursor.fetchone():
                cursor.execute(
                    db.adapt_params(
                        "UPDATE assistant_usage SET total_requests = total_requests + 1, "
                        "updated_at = ? WHERE month = ?"
                    ),
                    (now, today),
                )
            else:
                cursor.execute(
                    db.adapt_params(
                        "INSERT INTO assistant_usage (month, total_input_tokens, "
                        "total_output_tokens, total_requests, updated_at) VALUES (?, 0, 0, 1, ?)"
                    ),
                    (today, now),
                )

            conn.commit()

    def get_usage_summary(self) -> Dict:
        """Return current month usage."""
        current_month = datetime.now().strftime("%Y-%m")
        today = date.today().isoformat()

        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            cursor.execute(
                db.adapt_params(
                    "SELECT total_input_tokens, total_output_tokens, total_requests "
                    "FROM assistant_usage WHERE month = ?"
                ),
                (current_month,),
            )
            row = cursor.fetchone()
            tokens_used = ((row[0] or 0) + (row[1] or 0)) if row else 0
            monthly_requests = (row[2] or 0) if row else 0

            cursor.execute(
                db.adapt_params("SELECT total_requests FROM assistant_usage WHERE month = ?"),
                (today,),
            )
            daily_row = cursor.fetchone()
            requests_today = (daily_row[0] or 0) if daily_row else 0

        return {
            "tokens_used": tokens_used,
            "tokens_limit": MONTHLY_TOKEN_LIMIT,
            "pct_used": round((tokens_used / MONTHLY_TOKEN_LIMIT) * 100, 1)
            if MONTHLY_TOKEN_LIMIT > 0
            else 0,
            "requests_today": requests_today,
            "requests_daily_limit": DAILY_REQUEST_LIMIT,
            "monthly_requests": monthly_requests,
        }
