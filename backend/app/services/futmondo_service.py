#!/usr/bin/env python3
"""
Futmondo Service - Main service class that orchestrates all operations
"""

import logging
from typing import Dict, List
from app.services.futmondo_client import FutmondoClient
from app.core.config import (
    FUTMONDO_EMAIL, FUTMONDO_PASSWORD, CHAMPIONSHIP_ID,
    MAX_PLAYERS_TO_ANALYZE, REQUEST_DELAY_SECONDS
)

logger = logging.getLogger(__name__)

class FutmondoService:
    """Main service class that orchestrates all Futmondo operations"""

    def __init__(self):
        self.client = FutmondoClient(FUTMONDO_EMAIL, FUTMONDO_PASSWORD)
        # Legacy analyzers are currently unsupported; keep placeholders to avoid attribute errors
        self.data_manager = None
        self.transaction_analyzer = None
        self.user_profit_analyzer = None
        self.team_analyzer = None

    def login(self) -> bool:
        """Login to Futmondo API"""
        return self.client.login()

    def update_player_data(self, force_refresh: bool = False) -> bool:
        """Legacy method retained for compatibility. Currently not implemented."""
        logger.warning("update_player_data is deprecated in favor of DataSyncService.")
        return False

    def analyze_player_profits(self) -> List[Dict]:
        """Analyze player transaction profits"""
        raise NotImplementedError("Legacy analysis features are not supported in the current version.")

    def analyze_user_profits(self, force_refresh: bool = False) -> List[Dict]:
        """Analyze user profits from transactions"""
        raise NotImplementedError("Legacy analysis features are not supported in the current version.")

    def get_user_detailed_analysis(self, user_id: str) -> Dict:
        """Get detailed analysis for a specific user by ID"""
        raise NotImplementedError("Legacy analysis features are not supported in the current version.")

    def get_user_detailed_analysis_by_username(self, username: str) -> Dict:
        """Get detailed analysis for a specific user by username (convenience method)"""
        raise NotImplementedError("Legacy analysis features are not supported in the current version.")

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        raise NotImplementedError("Legacy analysis features are not supported in the current version.")

    def analyze_team_financial_status(self) -> List[Dict]:
        """Analyze team financial status"""
        raise NotImplementedError("Legacy analysis features are not supported in the current version.")

    def get_team_detailed_analysis(self, team_id: str) -> Dict:
        """Get detailed analysis for a specific team"""
        raise NotImplementedError("Legacy analysis features are not supported in the current version.")

    def _dataclass_to_dict(self, obj) -> Dict:
        """Convert dataclass object to dictionary"""
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        if hasattr(obj, '_asdict'):  # For namedtuple
            return obj._asdict()
        return dict(obj)

    def full_analysis(self, force_refresh: bool = False) -> Dict:
        """Perform full analysis including data update and profit analysis"""
        logger.info("Starting full analysis...")
        raise NotImplementedError("Legacy analysis features are not supported in the current version.")
