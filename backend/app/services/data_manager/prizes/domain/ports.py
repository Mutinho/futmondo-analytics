"""Consumer-owned data port for the ``prizes`` responsibility (BR1.3).

Structural :class:`typing.Protocol`; no SQL, no framework (BR1.3). This is the
read side (``get_prizes_by_team``); the authoritative prize writer stays in
``prizes/team_prizes_writer.py`` and is untouched here.
"""

from typing import Dict, Protocol


class PrizesReadDataPort(Protocol):
    """Structural type of the read surface prizes consumes."""

    def get_prizes_by_team(self, championship_id: str) -> Dict[str, Dict[str, int]]:
        """Return accumulated prizes per team from the ``team_prizes`` table."""
        ...
