"""Pure prize calculation for matchday prizes.

This package hosts the pure, side-effect-free prize calculation extracted from
``data_sync_service.sync_prizes`` (Q1=A). It contains no I/O and no SQL: the
orchestrator (``sync_prizes``) handles ingestion from the Futmondo API and
persistence to ``team_prizes``, and delegates the math to :mod:`.calculator`.
"""

from app.services.prizes.calculator import (
    PrizeConfig,
    RoundTeamEntry,
    TeamRoundPrize,
    calculate_round_prizes,
)

__all__ = [
    "PrizeConfig",
    "RoundTeamEntry",
    "TeamRoundPrize",
    "calculate_round_prizes",
]
