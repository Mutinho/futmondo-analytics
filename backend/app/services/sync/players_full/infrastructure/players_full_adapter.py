"""Infrastructure adapter implementing :class:`PlayersFullSyncDataPort` (BR2.2).

This is the ONLY module in the ``players_full`` sync context that touches
``DataManagerV2`` or its raw ``db`` connection. It wraps the current facade, so
the production result stays identical (BR1.2, BR2.2). The ``save_favorites`` raw
SQL that used to run inline in ``_save_favorites`` — the table-ensure DDL (both
Postgres and SQLite shapes), the delete-then-insert, and the Postgres
``execute_values`` branch — is moved here VERBATIM: not rewritten, not moved into
``data_manager_v2.py``.
"""

from datetime import datetime
from typing import Dict, List, Optional

from app.services.data_manager_v2 import DataManagerV2
from app.services.sync.players_full.domain.ports import PlayersFullSyncDataPort


class DataManagerPlayersFullAdapter(PlayersFullSyncDataPort):
    """Adapt ``DataManagerV2`` (and its raw ``db``) to ``PlayersFullSyncDataPort``."""

    def __init__(self, dm: Optional[DataManagerV2] = None) -> None:
        """Create the adapter.

        Args:
            dm: The data manager to delegate persistence to. Defaults to a fresh
                ``DataManagerV2(skip_init=True)`` to preserve the historical
                behavior (the facade never re-inits the schema per instance).
        """
        self.dm = dm if dm is not None else DataManagerV2(skip_init=True)

    def save_players_batch(self, player_records: List[Dict]) -> int:
        # Delegated verbatim to DataManagerV2 (BR2.2).
        return self.dm.save_players_batch(player_records)

    def delete_orphan_players(self, live_ids: List[str]) -> int:
        # Delegated verbatim to DataManagerV2 (BR2.2).
        return self.dm.delete_orphan_players(live_ids)

    def save_player_championship_stats(
        self, championship_id: str, stats_payload: List[Dict]
    ) -> None:
        # Delegated verbatim to DataManagerV2 (BR2.2).
        self.dm.save_player_championship_stats(championship_id, stats_payload)

    def save_favorites(
        self, championship_id: str, user_id: str, player_ids: List[str]
    ) -> None:
        # Raw SQL moved VERBATIM from DataSyncService._save_favorites (BR2.2):
        # the table-ensure DDL, the delete-then-insert, and the Postgres
        # execute_values branch. The former inline code read self.championship_id
        # and ``self.client.user_id or ''``; those two values arrive here as
        # ``championship_id`` and ``user_id`` (the orchestrator resolves the
        # ``or ''`` fallback before calling, preserving the historical value).
        db = self.dm.db
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            # Ensure table exists
            if db.db_type in ["postgresql", "postgres"]:
                raw = cursor._cursor if hasattr(cursor, "_cursor") else cursor
                raw.execute("""
                    CREATE TABLE IF NOT EXISTS player_favorites (
                        id SERIAL PRIMARY KEY,
                        championship_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        player_id TEXT NOT NULL,
                        synced_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(championship_id, user_id, player_id)
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS player_favorites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        championship_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        player_id TEXT NOT NULL,
                        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(championship_id, user_id, player_id)
                    )
                """)

            # Clear existing favorites for this user+championship
            sql_del = "DELETE FROM player_favorites WHERE championship_id = ? AND user_id = ?"
            sql_del = db.adapt_params(sql_del)
            cursor.execute(sql_del, (championship_id, user_id))

            # Insert new favorites
            if player_ids:
                if db.db_type in ["postgresql", "postgres"]:
                    from psycopg2.extras import execute_values
                    raw = cursor._cursor if hasattr(cursor, "_cursor") else cursor
                    values = [(championship_id, user_id, pid) for pid in player_ids]
                    execute_values(raw, """
                        INSERT INTO player_favorites (championship_id, user_id, player_id)
                        VALUES %s
                        ON CONFLICT (championship_id, user_id, player_id) DO NOTHING
                    """, values)
                else:
                    for pid in player_ids:
                        cursor.execute(
                            "INSERT OR IGNORE INTO player_favorites (championship_id, user_id, player_id) VALUES (?, ?, ?)",
                            (championship_id, user_id, pid)
                        )

    def update_sync_metadata(
        self,
        championship_id: str,
        data_type: str,
        last_sync_id: Optional[str] = None,
        last_sync_date: Optional[datetime] = None,
        last_sync_matchday: Optional[int] = None,
        records_synced: int = 0,
        sync_duration_seconds: Optional[float] = None,
        sync_status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        # Delegated verbatim to DataManagerV2 (BR2.2). The former inline calls
        # passed every argument by keyword; that convention is preserved. Only
        # the keyword arguments those calls actually supplied are forwarded; the
        # rest keep DataManagerV2's defaults, so the persisted row is unchanged.
        kwargs: Dict = {
            "championship_id": championship_id,
            "data_type": data_type,
        }
        if last_sync_id is not None:
            kwargs["last_sync_id"] = last_sync_id
        if last_sync_date is not None:
            kwargs["last_sync_date"] = last_sync_date
        if last_sync_matchday is not None:
            kwargs["last_sync_matchday"] = last_sync_matchday
        kwargs["records_synced"] = records_synced
        if sync_duration_seconds is not None:
            kwargs["sync_duration_seconds"] = sync_duration_seconds
        kwargs["sync_status"] = sync_status
        if error_message is not None:
            kwargs["error_message"] = error_message
        self.dm.update_sync_metadata(**kwargs)
