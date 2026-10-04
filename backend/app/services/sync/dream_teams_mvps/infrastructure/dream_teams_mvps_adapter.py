"""Infrastructure adapter implementing :class:`DreamTeamsMvpsSyncDataPort` (BR2.2).

This is the ONLY module in the ``dream_teams_mvps`` sync context that touches
``DataManagerV2``. It wraps the current facade, delegating the three persistence
calls verbatim, so the production result stays identical (BR1.2, BR2.2). No SQL
is rewritten and no method is added to ``data_manager_v2.py``.
"""

from datetime import datetime
from typing import Dict, List, Optional

from app.services.data_manager_v2 import DataManagerV2
from app.services.sync.dream_teams_mvps.domain.ports import DreamTeamsMvpsSyncDataPort


class DataManagerDreamTeamsMvpsAdapter(DreamTeamsMvpsSyncDataPort):
    """Adapt ``DataManagerV2`` to ``DreamTeamsMvpsSyncDataPort``."""

    def __init__(self, dm: Optional[DataManagerV2] = None) -> None:
        """Create the adapter.

        Args:
            dm: The data manager to delegate persistence to. Defaults to a fresh
                ``DataManagerV2(skip_init=True)`` to preserve the historical
                behavior (the facade never re-inits the schema per instance).
        """
        self.dm = dm if dm is not None else DataManagerV2(skip_init=True)

    def get_last_sync_metadata(
        self, championship_id: str, data_type: str
    ) -> Optional[Dict]:
        # Delegated verbatim to DataManagerV2 (BR2.2).
        return self.dm.get_last_sync_metadata(championship_id, data_type)

    def save_dream_team_mvp(
        self,
        championship_id: str,
        round_id: str,
        matchday: int,
        dream_team_players: List,
        mvp_id,
        player_details: Optional[Dict] = None,
    ) -> None:
        # Delegated verbatim to DataManagerV2 (BR2.2): same positional shape plus
        # the ``player_details`` keyword as the former inline call.
        self.dm.save_dream_team_mvp(
            championship_id,
            round_id,
            matchday,
            dream_team_players,
            mvp_id,
            player_details=player_details,
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
        # the keyword arguments those calls actually supplied are forwarded (a
        # zero ``last_sync_matchday`` IS forwarded — ``0`` is not ``None``);
        # the rest keep DataManagerV2's defaults, so the persisted row is unchanged.
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
