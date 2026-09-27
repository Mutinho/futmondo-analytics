"""Analytics bounded context (Wave 1 of the god-file decomposition).

This package extracts the former ``analytics_service.py`` god-file into a thin
DDD layering while preserving the exact public surface (the 11 ``get_*``
methods) and observable behavior (BR1.1):

- ``domain/ports.py``     — ``AnalyticsDataPort`` (the consumer-owned Protocol
                            describing ONLY the data analytics needs; no SQL,
                            no framework — BR2.1).
- ``application/calculations.py`` — the pure calculation logic and the
                            team/player resolution helpers, operating over the
                            port (dependency inversion — BR2.3).
- ``infrastructure/data_manager_adapter.py`` — ``DataManagerAnalyticsAdapter``,
                            the only place with raw SQL (BR2.2), implemented over
                            the current ``DataManagerV2`` facade.
- ``facade.py``           — ``AnalyticsService``, a thin application service that
                            preserves the public surface and only delegates
                            (BR2.5).

``app.services.analytics_service`` remains importable as a re-export shim so the
historical import path (used by the endpoint) keeps working unchanged.
"""

from app.services.analytics.facade import AnalyticsService

__all__ = ["AnalyticsService"]
