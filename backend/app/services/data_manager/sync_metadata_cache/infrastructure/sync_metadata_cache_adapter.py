"""Infrastructure adapter for ``sync-metadata-cache`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in ``DataManagerV2.get_last_sync_metadata`` /
``update_sync_metadata`` plus the pure ``should_update_cache`` predicate, moved
**verbatim** including the engine branch (BR1.2/FR1.4). ``ensure_championship_exists``
is reached live via ``self.dm`` so production behavior is byte-for-byte identical
(BR3.1).
"""

from datetime import datetime
from typing import Any, Dict, Optional

from app.services.data_manager.sync_metadata_cache.domain.ports import (
    SyncMetadataCacheDataPort,
)


class SyncMetadataCacheAdapter(SyncMetadataCacheDataPort):
    """Adapt the sync-metadata/cache SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

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
                    "updated_at": row[5],
                }
            return None

    def update_sync_metadata(
        self,
        championship_id: str,
        data_type: str,
        last_sync_id: str = None,
        last_sync_date: datetime = None,
        last_sync_matchday: int = None,
        records_synced: int = 0,
        sync_duration_seconds: float = None,
        sync_status: str = "success",
        error_message: str = None,
    ):
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
            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
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
                """
            else:
                sql = """
                    INSERT OR REPLACE INTO sync_metadata 
                    (championship_id, data_type, last_sync_id, last_sync_date, last_sync_matchday,
                     records_synced, sync_duration_seconds, sync_status, error_message, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

            now = datetime.now()
            cursor.execute(
                sql,
                (
                    championship_id,
                    data_type,
                    last_sync_id,
                    last_sync_date or now,
                    last_sync_matchday,
                    records_synced,
                    sync_duration_seconds,
                    sync_status,
                    error_message,
                    now,
                ),
            )
            conn.commit()

    def should_update_cache(self, data_type: str) -> bool:
        """Check if cache should be updated (always true for fresh data in V2)"""
        return True  # Always update in V2 for historical accuracy
