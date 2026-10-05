"""Consumer-owned data port for the ``punishments-bonuses`` responsibility (BR1.3).

Structural :class:`typing.Protocol` describing ONLY the persistence operations
the orchestrator consumes. No SQL, no framework (BR1.3).
"""

from typing import Dict, List, Protocol


class PunishmentsBonusesDataPort(Protocol):
    """Structural type of the surface punishments-bonuses consumes."""

    def save_punishments_bonuses(self, championship_id: str, news_items: List[Dict]) -> None:
        """Persist punishments/bonuses parsed from locker-room news items."""
        ...

    def get_user_punishments_bonuses(self, championship_id: str) -> Dict[str, Dict]:
        """Aggregate punishments/bonuses grouped by user/team."""
        ...
