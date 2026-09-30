"""Infrastructure adapter implementing :class:`MatchOddsSyncDataPort` (BR2.2).

This is the ONLY module in the ``match_odds`` sync context that touches
``DataManagerV2``. It wraps the current facade (Wave 3 does not decompose
``data_manager`` — that is a later wave), delegating the two persistence calls
``save_match_odds`` and ``update_sync_metadata`` verbatim, so the production
result stays identical (BR1.2, BR2.2). No SQL is rewritten and no method is
added to ``data_manager_v2.py``.
"""

from datetime import datetime
from typing import Dict, List, Optional

from app.services.data_manager_v2 import DataManagerV2
from app.services.sync.match_odds.domain.ports import MatchOddsSyncDataPort


class DataManagerMatchOddsAdapter(MatchOddsSyncDataPort):
    """Adapt ``DataManagerV2`` to ``MatchOddsSyncDataPort``."""

    def __init__(self, dm: Optional[DataManagerV2] = None) -> None:
        """Create the adapter.

        Args:
            dm: The data manager to delegate persistence to. Defaults to a fresh
                ``DataManagerV2(skip_init=True)`` to preserve the historical
                behavior (the facade never re-inits the schema per instance).
        """
        self.dm = dm if dm is not None else DataManagerV2(skip_init=True)

    def save_match_odds(
        self,
        championship_id: str,
        matches: List[Dict],
        round_id: Optional[str] = None,
        matchday: Optional[int] = None,
    ) -> None:
        # Delegated verbatim to DataManagerV2 (BR2.2): same positional/keyword
        # shape as the former inline call in DataSyncService.sync_match_odds.
        self.dm.save_match_odds(championship_id, matches, round_id=round_id, matchday=matchday)

    def update_sync_metadata(
        self,
        championship_id: str,
        data_type: str,
        last_sync_matchday: Optional[int] = None,
        last_sync_date: Optional[datetime] = None,
        records_synced: Optional[int] = None,
        sync_duration_seconds: Optional[float] = None,
        sync_status: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        # Delegated verbatim to DataManagerV2 (BR2.2). The two former inline
        # calls passed every argument by keyword; that convention is preserved
        # here. Only the keyword arguments those calls actually supplied are
        # forwarded; the rest keep DataManagerV2's own defaults, so the
        # persisted row is unchanged.
        kwargs: Dict = {
            "championship_id": championship_id,
            "data_type": data_type,
        }
        if last_sync_matchday is not None:
            kwargs["last_sync_matchday"] = last_sync_matchday
        if last_sync_date is not None:
            kwargs["last_sync_date"] = last_sync_date
        if records_synced is not None:
            kwargs["records_synced"] = records_synced
        if sync_duration_seconds is not None:
            kwargs["sync_duration_seconds"] = sync_duration_seconds
        if sync_status is not None:
            kwargs["sync_status"] = sync_status
        if error_message is not None:
            kwargs["error_message"] = error_message
        self.dm.update_sync_metadata(**kwargs)
