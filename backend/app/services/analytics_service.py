"""Backward-compatible re-export shim for ``AnalyticsService``.

The analytics god-file was decomposed into the ``app.services.analytics``
bounded context (Wave 1). This module is kept only so the historical import path
``from app.services.analytics_service import AnalyticsService`` — used by the
analytics endpoint — keeps working unchanged. The implementation now lives in
``app.services.analytics.facade``.
"""

from app.services.analytics.facade import AnalyticsService

__all__ = ["AnalyticsService"]
