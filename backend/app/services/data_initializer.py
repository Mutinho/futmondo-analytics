#!/usr/bin/env python3
"""Data Initializer - modernized with DataSyncService"""

import logging
from typing import Dict

from app.services.futmondo_client import FutmondoClient
from app.services.data_sync_service import DataSyncService
from app.core.config import CHAMPIONSHIP_ID, FUTMONDO_EMAIL, FUTMONDO_PASSWORD

logger = logging.getLogger(__name__)


class DataInitializer:
    """Wrapper around DataSyncService for legacy initialization endpoint."""

    def __init__(self) -> None:
        self.client = FutmondoClient(email=FUTMONDO_EMAIL, password=FUTMONDO_PASSWORD)
        self.championship_id = CHAMPIONSHIP_ID
        self.sync_service = DataSyncService(futmondo_client=self.client)

    def initialize_all_data(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """Run a full synchronization pipeline.

        Args:
            force_refresh: Kept for backward compatibility. The new sync pipeline
                always performs incremental updates, so this flag is ignored but
                retained to avoid breaking callers.

        Returns:
            Dictionary keyed by sync type with status metadata.
        """

        if not self.client.is_authenticated():
            logger.info("Logging in...")
            if not self.client.login():
                logger.error("Failed to authenticate with Futmondo")
                return {"error": "Authentication failed"}

        logger.info("🚀 Starting data initialization via DataSyncService...")

        try:
            results = self.sync_service.sync_all()
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"❌ Data synchronization failed: {exc}", exc_info=True)
            return {"error": str(exc)}

        logger.info("✅ Data initialization complete")
        return results

