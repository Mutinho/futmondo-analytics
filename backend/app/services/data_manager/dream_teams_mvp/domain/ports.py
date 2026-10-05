"""Consumer-owned data port for the ``dream-teams-mvp`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3).
"""

from typing import Dict, List, Optional, Protocol


class DreamTeamsMvpDataPort(Protocol):
    """Structural type of the surface dream-teams-mvp consumes."""

    def save_dream_team_mvp(
        self,
        championship_id: str,
        round_id: str,
        matchday: int,
        dream_team_players: List[str],
        mvp_player_id: Optional[str] = None,
        player_details: Optional[Dict[str, Dict]] = None,
    ) -> None:
        """Persist dream-team members and MVP for a round."""
        ...

    def get_dream_team_bonus_stats(self, championship_id: str) -> Dict[str, Dict[str, int]]:
        """Return dream-team appearance and MVP counts per team."""
        ...
