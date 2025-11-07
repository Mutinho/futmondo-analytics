#!/usr/bin/env python3
"""
Data Synchronization Script
Runs incremental and full data synchronization from Futmondo API to database
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.data_sync_service import DataSyncService
from app.services.futmondo_client import FutmondoClient
from app.core.config import FUTMONDO_EMAIL, FUTMONDO_PASSWORD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main sync function"""
    try:
        logger.info("=" * 60)
        logger.info("Starting data synchronization")
        logger.info("=" * 60)
        
        # Initialize Futmondo client and authenticate
        client = FutmondoClient(FUTMONDO_EMAIL, FUTMONDO_PASSWORD)
        if not client.is_authenticated():
            logger.info("Authenticating...")
            if not client.login():
                logger.error("Failed to authenticate")
                sys.exit(1)
            logger.info("Authentication successful")
        
        # Create sync service
        sync_service = DataSyncService(futmondo_client=client)
        
        # Run all syncs
        results = sync_service.sync_all()
        
        # Print summary
        logger.info("=" * 60)
        logger.info("Synchronization Summary:")
        logger.info("=" * 60)
        
        for sync_type, result in results.items():
            status = result.get("status", "unknown")
            records = result.get("records_synced", 0)
            duration = result.get("duration_seconds", 0)
            
            if status == "error":
                error = result.get("error", "Unknown error")
                logger.error(f"  {sync_type}: ERROR - {error}")
            else:
                logger.info(f"  {sync_type}: {status} - {records} records in {duration:.2f}s")
        
        logger.info("=" * 60)
        logger.info("Synchronization complete")
        logger.info("=" * 60)
        
        # Exit with error code if any sync failed
        for result in results.values():
            if result.get("status") == "error":
                sys.exit(1)
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Synchronization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

