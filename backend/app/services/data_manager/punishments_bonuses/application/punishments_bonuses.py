"""Thin orchestrator for the ``punishments-bonuses`` responsibility (BR1.3).

Delegates to an injected :class:`PunishmentsBonusesDataPort`; no SQL (BR1.3).
"""

from typing import Dict, List

from app.services.data_manager.punishments_bonuses.domain.ports import (
    PunishmentsBonusesDataPort,
)


class PunishmentsBonusesService:
    """Coordinate punishments/bonuses over a ``PunishmentsBonusesDataPort``."""

    def __init__(self, port: PunishmentsBonusesDataPort) -> None:
        self.port = port

    def save_punishments_bonuses(self, championship_id: str, news_items: List[Dict]) -> None:
        return self.port.save_punishments_bonuses(championship_id, news_items)

    def get_user_punishments_bonuses(self, championship_id: str) -> Dict[str, Dict]:
        return self.port.get_user_punishments_bonuses(championship_id)
