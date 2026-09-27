"""Analytics infrastructure layer: the only place with raw SQL (BR2.2)."""

from app.services.analytics.infrastructure.data_manager_adapter import (
    DataManagerAnalyticsAdapter,
)

__all__ = ["DataManagerAnalyticsAdapter"]
