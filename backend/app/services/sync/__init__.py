"""Sync bounded contexts (Wave 3 of the god-file decomposition).

Per-domain application modules extracted from ``data_sync_service.py`` following
the DDD layering already used by ``analytics/``, ``assistant/`` and ``prizes/``.
The god-file ``DataSyncService`` remains the public facade; each ``sync_*``
method delegates to a domain orchestrator here while preserving the exact
observable ``SyncResult`` payload (BR1.1, FR5).

This wave establishes the extractable pattern and lands the pilot domain
``match_odds`` end-to-end (lightweight shape: port + adapter + orchestrator).
"""
