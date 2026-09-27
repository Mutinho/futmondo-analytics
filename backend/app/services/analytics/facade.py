"""Thin ``AnalyticsService`` application-service facade (BR2.5, BR2.6).

Preserves the exact public surface of the former god-file (the 11 ``get_*``
methods and the no-argument constructor) and only delegates to
:class:`~app.services.analytics.application.calculations.AnalyticsCalculations`,
which operates over an injected :class:`AnalyticsDataPort`.

Constructor injection with a default (BR2.6, OCP): ``AnalyticsService()`` with no
arguments builds the production
:class:`~app.services.analytics.infrastructure.data_manager_adapter.DataManagerAnalyticsAdapter`
over a fresh ``DataManagerV2`` — identical to the historical behavior the
endpoint relies on (``Depends(get_service)`` calls ``AnalyticsService()``). Tests
inject a stub port via ``AnalyticsService(data=stub_port)`` (no monkeypatching).

The observable ``_team_cache`` / ``_player_cache`` attributes are exposed on the
facade as the very same dict objects the calculations mutate (FR2.3), and
``dm`` remains readable for backward compatibility with callers that inspected
the former attribute.
"""

from typing import Dict, List, Optional

from app.services.analytics.application.calculations import AnalyticsCalculations
from app.services.analytics.domain.ports import AnalyticsDataPort
from app.services.analytics.infrastructure.data_manager_adapter import (
    DataManagerAnalyticsAdapter,
)


class AnalyticsService:
    """Provides high-level analytics derived from historical Futmondo data."""

    def __init__(self, data: Optional[AnalyticsDataPort] = None) -> None:
        port: AnalyticsDataPort = data if data is not None else DataManagerAnalyticsAdapter()
        self._calc = AnalyticsCalculations(port)
        # Backward-compatible observable attributes (FR2.3): the same dict
        # objects the calculations mutate, and the underlying data manager when
        # the port exposes one.
        self._team_cache = self._calc._team_cache
        self._player_cache = self._calc._player_cache
        self.dm = getattr(port, "dm", port)

    # --- Championship analytics -------------------------------------------
    def get_championship_trends(self, championship_id: str, window: Optional[int] = None) -> Dict:
        return self._calc.get_championship_trends(championship_id, window=window)

    def get_championship_custom_classification(
        self,
        championship_id: str,
        window: Optional[int] = None,
        exclude_matchdays: Optional[List[int]] = None,
    ) -> Dict:
        return self._calc.get_championship_custom_classification(
            championship_id, window=window, exclude_matchdays=exclude_matchdays
        )

    def get_championship_heatmap(self, championship_id: str) -> Dict:
        return self._calc.get_championship_heatmap(championship_id)

    # --- Player analytics -------------------------------------------------
    def get_player_form(self, championship_id: str, window: int = 5) -> Dict:
        return self._calc.get_player_form(championship_id, window=window)

    def get_player_value_trend(self, championship_id: str, window: int = 30) -> Dict:
        return self._calc.get_player_value_trend(championship_id, window=window)

    # --- User analytics ---------------------------------------------------
    def get_user_consistency(self, championship_id: str, window: Optional[int] = None) -> Dict:
        return self._calc.get_user_consistency(championship_id, window=window)

    def get_user_market_activity(self, championship_id: str, window_days: int = 30) -> Dict:
        return self._calc.get_user_market_activity(championship_id, window_days=window_days)

    # --- Market insights --------------------------------------------------
    def get_market_watchlist(self, championship_id: str, limit: int = 20) -> Dict:
        return self._calc.get_market_watchlist(championship_id, limit=limit)

    def get_clause_network(self, championship_id: str) -> Dict:
        return self._calc.get_clause_network(championship_id)

    def get_opportunity_streaks(
        self, championship_id: str, min_streak: int = 3, threshold: float = 6.0
    ) -> Dict:
        return self._calc.get_opportunity_streaks(
            championship_id, min_streak=min_streak, threshold=threshold
        )

    # --- Projections ------------------------------------------------------
    def get_matchday_projections(
        self, championship_id: str, matchday: Optional[int] = None, window: int = 5
    ) -> Dict:
        return self._calc.get_matchday_projections(
            championship_id, matchday=matchday, window=window
        )
