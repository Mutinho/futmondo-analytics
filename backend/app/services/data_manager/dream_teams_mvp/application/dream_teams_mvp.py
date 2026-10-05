"""Thin orchestrator for the ``dream-teams-mvp`` responsibility (BR1.3).

Delegates to an injected :class:`DreamTeamsMvpDataPort`; no SQL (BR1.3).
"""

from typing import Dict, List, Optional

from app.services.data_manager.dream_teams_mvp.domain.ports import DreamTeamsMvpDataPort


class DreamTeamsMvpService:
    """Coordinate dream-team/MVP persistence over a ``DreamTeamsMvpDataPort``."""

    def __init__(self, port: DreamTeamsMvpDataPort) -> None:
        self.port = port

    def save_dream_team_mvp(
        self,
        championship_id: str,
        round_id: str,
        matchday: int,
        dream_team_players: List[str],
        mvp_player_id: Optional[str] = None,
        player_details: Optional[Dict[str, Dict]] = None,
    ) -> None:
        return self.port.save_dream_team_mvp(
            championship_id,
            round_id,
            matchday,
            dream_team_players,
            mvp_player_id=mvp_player_id,
            player_details=player_details,
        )

    def get_dream_team_bonus_stats(self, championship_id: str) -> Dict[str, Dict[str, int]]:
        return self.port.get_dream_team_bonus_stats(championship_id)
