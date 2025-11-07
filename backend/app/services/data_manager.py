#!/usr/bin/env python3
"""Deprecated DataManager stub.

The project migrated to `DataManagerV2`, but several legacy modules still import
the original dataclass definitions for typing purposes. This lightweight stub
keeps those symbols available without shipping the large, unmaintainable
implementation that previously lived here.
"""

from dataclasses import dataclass
from typing import Dict

import logging

logger = logging.getLogger(__name__)


@dataclass
class PlayerData:
    id: str
    name: str
    role: str
    team: str
    current_value: int
    current_points: int
    userteam_id: str | None = None
    userteam_name: str | None = None
    average_performance: Dict | None = None
    last_updated: str | None = None


@dataclass
class UserData:
    id: str
    username: str
    team_id: str
    team_name: str
    last_updated: str


@dataclass
class TransactionData:
    id: int
    player_id: str
    seller_user_id: str
    buyer_user_id: str
    seller_team_id: str
    buyer_team_id: str
    price: int
    date: str
    transaction_type: str


@dataclass
class UserProfitData:
    user_id: str
    username: str
    team_id: str
    team_name: str
    total_profit: float
    total_transactions: int
    successful_trades: int
    failed_trades: int
    best_profit: float
    worst_loss: float
    avg_profit_per_trade: float
    profit_percentage: float


class DataManager:  # pragma: no cover - maintained for backwards compatibility only
    """Legacy facade kept so imports from older modules do not crash.

    All new development should use `DataManagerV2`. Any attempt to instantiate
    this class will raise an exception to make the deprecation explicit.
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        raise RuntimeError(
            "DataManager is deprecated. Please migrate to DataManagerV2 before using this component."
        )
