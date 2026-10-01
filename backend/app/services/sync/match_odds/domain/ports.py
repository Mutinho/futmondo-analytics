"""Consumer-owned data port for the ``match_odds`` sync context (BR2.1, BR2.3).

``MatchOddsSyncDataPort`` is a structural :class:`typing.Protocol` describing
ONLY the persistence operations the ``match_odds`` orchestrator consumes. It
lives in the domain layer, imports neither ``infrastructure/`` nor any
framework, and contains no SQL (BR2.1, BR2.2). The orchestrator depends on this
abstraction, not on the concrete ``DataManagerV2`` (dependency inversion,
BR2.3); the concrete
:class:`~app.services.sync.match_odds.infrastructure.match_odds_adapter.DataManagerMatchOddsAdapter`
implements it.

Both methods mirror the existing ``DataManagerV2`` surface verbatim; the adapter
delegates to it unchanged (Wave 3 does not decompose ``data_manager`` — BR2.2).
"""

from datetime import datetime
from typing import Dict, List, Optional, Protocol


class MatchOddsSyncDataPort(Protocol):
    """Structural type of the persistence surface the match_odds sync consumes."""

    def save_match_odds(
        self,
        championship_id: str,
        matches: List[Dict],
        round_id: Optional[str] = None,
        matchday: Optional[int] = None,
    ) -> None:
        """Persist the match-odds rows for a round (delegates to DataManagerV2)."""
        ...

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
        """Record sync metadata for a data type (delegates to DataManagerV2)."""
        ...
