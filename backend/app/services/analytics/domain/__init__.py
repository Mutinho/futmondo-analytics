"""Analytics domain layer: consumer-owned ports (no infrastructure, no SQL)."""

from app.services.analytics.domain.ports import AnalyticsDataPort

__all__ = ["AnalyticsDataPort"]
