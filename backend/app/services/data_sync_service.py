"""
Data Sync Service - Handles incremental and full data synchronization
"""

import logging
from typing import Dict, Optional, Tuple

from app.services.data_manager_v2 import DataManagerV2
from app.services.futmondo_client import FutmondoClient
from app.core.config import (
    CHAMPIONSHIP_ID,
    LEAGUE_ID,
    FUTMONDO_EMAIL,
    FUTMONDO_PASSWORD,
)

logger = logging.getLogger(__name__)


class DataSyncService:
    """Service for synchronizing data from Futmondo API to database"""
    
    def __init__(self, futmondo_client: FutmondoClient = None):
        # Use skip_init=True so that schemas are not dropped/recreated on every
        # DataSyncService instantiation. The schema should be created once via
        # the reset endpoint or the dedicated init script.
        self.dm = DataManagerV2(skip_init=True)
        self.championship_id = CHAMPIONSHIP_ID
        self.league_id = LEAGUE_ID
        self.user_id = ""  # Set externally for per-user sync tracking
        
        # Ensure championship record exists before any sync runs
        try:
            self.dm.ensure_championship_exists(self.championship_id)
        except Exception as e:
            logger.debug(f"Could not ensure championship exists at init: {e}")

        if futmondo_client:
            self.client = futmondo_client
        else:
            # Instantiate FutmondoClient directly to avoid legacy service dependency
            self.client = FutmondoClient(FUTMONDO_EMAIL, FUTMONDO_PASSWORD)
            if not self.client.is_authenticated():
                login_ok = self.client.login()
                if not login_ok:
                    logger.error("Failed to authenticate Futmondo client for DataSyncService")

    def _find_championship(self) -> Tuple[Optional[Dict], Dict]:
        """Locate league (by LEAGUE_ID) and championship (by CHAMPIONSHIP_ID)."""
        leagues = self.client.get_league_list()
        if not leagues:
            raise Exception("Could not fetch league list")

        league_hint = None
        championship_match = None
        championship_league = None

        for league in leagues:
            if league.get("_id") == self.league_id:
                league_hint = league
            for champ in league.get("championships", []):
                if champ.get("_id") == self.championship_id:
                    championship_match = champ
                    championship_league = league
            if league_hint and championship_match:
                break

        if championship_match is None:
            for league in leagues:
                for champ in league.get("championships", []):
                    if champ.get("_id") == self.championship_id:
                        championship_match = champ
                        championship_league = league
                        break
                if championship_match:
                    break

        if championship_match is None:
            logger.warning(
                "Could not find championship %s (league hint %s) in league list",
                self.championship_id,
                self.league_id,
            )
            return league_hint or championship_league, None

        return league_hint or championship_league, championship_match
    
    def sync_transactions(self) -> Dict:
        """Sync transactions incrementally from pressroom endpoint.

        Thin delegation to the extracted ``transactions`` sync orchestrator
        (BR1.2). Same signature and same observable ``SyncResult`` payload as
        before (BR1.1, FR5). Ingestion/throttling/enrichment/error handling live
        in the orchestrator; persistence (including the idempotent column ALTERs,
        the bids UPDATE, and the enrichment SELECT/UPDATE) goes through a narrow
        port wrapping ``DataManagerV2`` and its raw ``db`` (BR2.2); the domain
        package is imported lazily so the facade import graph is unchanged.

        Returns:
            Dict with sync results (records_synced, last_sync_id, duration, status)
        """
        from app.services.sync.transactions import TransactionsSyncOrchestrator
        from app.services.sync.transactions.infrastructure.transactions_adapter import (
            DataManagerTransactionsAdapter,
        )

        orchestrator = TransactionsSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=DataManagerTransactionsAdapter(dm=self.dm),
        )
        return orchestrator.sync()

    def sync_clauses(self) -> Dict:
        """Sync clauses incrementally from locker news endpoint

        Thin delegation to the extracted ``clauses`` sync orchestrator
        (BR1.2). Same signature and same observable ``SyncResult`` payload as
        before (BR1.1, FR5). Ingestion/throttling/error handling live in the
        orchestrator; persistence goes through a narrow port wrapping
        ``DataManagerV2`` (BR2.2); the domain package is imported lazily so the
        facade import graph is unchanged.

        Returns:
            Dict with sync results
        """
        from app.services.sync.clauses import ClausesSyncOrchestrator
        from app.services.sync.clauses.infrastructure.clauses_adapter import (
            DataManagerClausesAdapter,
        )

        orchestrator = ClausesSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=DataManagerClausesAdapter(dm=self.dm),
        )
        return orchestrator.sync()

    def sync_punishments_bonuses(self) -> Dict:
        """Sync punishments and bonuses from locker news endpoint.

        Thin delegation to the extracted ``punishments_bonuses`` sync
        orchestrator (BR1.2). Same signature and same observable ``SyncResult``
        payload as before (BR1.1, FR5). Ingestion/throttling/error handling live
        in the orchestrator; persistence goes through a narrow port wrapping
        ``DataManagerV2`` (BR2.2); the domain package is imported lazily so the
        facade import graph is unchanged.
        """
        from app.services.sync.punishments_bonuses import (
            PunishmentsBonusesSyncOrchestrator,
        )
        from app.services.sync.punishments_bonuses.infrastructure.punishments_bonuses_adapter import (
            DataManagerPunishmentsBonusesAdapter,
        )

        orchestrator = PunishmentsBonusesSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=DataManagerPunishmentsBonusesAdapter(dm=self.dm),
        )
        return orchestrator.sync()
    
    def sync_dream_teams_mvps(self) -> Dict:
        """Sync dream teams and MVPs for new rounds only.

        Thin delegation to the extracted ``dream_teams_mvps`` sync orchestrator
        (BR1.2). Same signature and same observable ``SyncResult`` payload as
        before (BR1.1, FR5). ``_find_championship`` STAYS here and is injected as
        a callable so it is not duplicated (BR2.3). Persistence goes through a
        narrow port wrapping ``DataManagerV2`` (BR2.2); the domain package is
        imported lazily so the facade import graph is unchanged.

        Returns:
            Dict with sync results
        """
        from app.services.sync.dream_teams_mvps import DreamTeamsMvpsSyncOrchestrator
        from app.services.sync.dream_teams_mvps.infrastructure.dream_teams_mvps_adapter import (
            DataManagerDreamTeamsMvpsAdapter,
        )

        orchestrator = DreamTeamsMvpsSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            find_championship=self._find_championship,
            data=DataManagerDreamTeamsMvpsAdapter(dm=self.dm),
        )
        return orchestrator.sync()

    def sync_player_performance(self) -> Dict:
        """Sync player performance by matchday from round lineups.

        Thin delegation to the extracted ``player_performance`` sync orchestrator
        (BR1.2). Same signature and same observable ``SyncResult`` payload as
        before (BR1.1, FR5). Persistence goes through a narrow port wrapping
        ``DataManagerV2`` (BR2.2); the domain package is imported lazily so the
        facade import graph is unchanged.
        """
        from app.services.sync.player_performance import (
            PlayerPerformanceSyncOrchestrator,
        )
        from app.services.sync.player_performance.infrastructure.player_performance_adapter import (
            DataManagerPlayerPerformanceAdapter,
        )

        orchestrator = PlayerPerformanceSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=DataManagerPlayerPerformanceAdapter(dm=self.dm),
        )
        return orchestrator.sync()
    
    def sync_rosters(self) -> Dict:
        """Sync team rosters for new matchdays only.

        Thin delegation to the extracted ``rosters`` sync orchestrator (BR1.2).
        Same signature and same observable ``SyncResult`` payload as before
        (BR1.1, FR5). ``_find_championship`` STAYS here and is injected as a
        callable so it is not duplicated (BR2.3). Persistence goes through a
        narrow port wrapping ``DataManagerV2`` (BR2.2); the domain package is
        imported lazily so the facade import graph is unchanged.

        Returns:
            Dict with sync results
        """
        from app.services.sync.rosters import RostersSyncOrchestrator
        from app.services.sync.rosters.infrastructure.rosters_adapter import (
            DataManagerRostersAdapter,
        )

        orchestrator = RostersSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            find_championship=self._find_championship,
            data=DataManagerRostersAdapter(dm=self.dm),
        )
        return orchestrator.sync()
    
    def sync_round_rankings(self) -> Dict:
        """Sync team standings (round rankings) — always re-syncs all matchdays.

        Thin delegation to the extracted ``round_rankings`` sync orchestrator
        (BR1.2). Same signature and same observable ``SyncResult`` payload as
        before (BR1.1, FR5) — including the ``rounds_synced`` / ``last_matchday``
        keys and the ``team_standings`` data type. Persistence goes through a
        narrow port wrapping ``DataManagerV2`` (BR2.2); the domain package is
        imported lazily so the facade import graph is unchanged.
        """
        from app.services.sync.round_rankings import RoundRankingsSyncOrchestrator
        from app.services.sync.round_rankings.infrastructure.round_rankings_adapter import (
            DataManagerRoundRankingsAdapter,
        )

        orchestrator = RoundRankingsSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=DataManagerRoundRankingsAdapter(dm=self.dm),
        )
        return orchestrator.sync()
    
    def sync_players_full(self) -> Dict:
        """Sync all players (full update - players can change basic data).

        Thin delegation to the extracted ``players_full`` sync orchestrator
        (BR1.2). Same signature and same observable ``SyncResult`` payload as
        before (BR1.1, FR5). Persistence (including the ``_save_favorites`` raw
        SQL with its Postgres ``execute_values`` branch) goes through a narrow
        port wrapping ``DataManagerV2`` and its raw ``db`` (BR2.2); the domain
        package is imported lazily so the facade import graph is unchanged.

        Returns:
            Dict with sync results
        """
        from app.services.sync.players_full import PlayersFullSyncOrchestrator
        from app.services.sync.players_full.infrastructure.players_full_adapter import (
            DataManagerPlayersFullAdapter,
        )

        orchestrator = PlayersFullSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=DataManagerPlayersFullAdapter(dm=self.dm),
        )
        return orchestrator.sync()
    
    def sync_match_odds(self) -> Dict:
        """Sync match odds for upcoming matches.

        Thin delegation to the extracted ``match_odds`` sync orchestrator
        (Wave 3, BR1.2). Same signature and same observable ``SyncResult``
        payload as before (BR1.1, FR5). Persistence goes through a narrow port
        wrapping ``DataManagerV2`` (BR2.2); the domain package is imported
        lazily so the facade import graph is unchanged.
        """
        from app.services.sync.match_odds import MatchOddsSyncOrchestrator
        from app.services.sync.match_odds.infrastructure.match_odds_adapter import (
            DataManagerMatchOddsAdapter,
        )

        orchestrator = MatchOddsSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            data=DataManagerMatchOddsAdapter(dm=self.dm),
        )
        return orchestrator.sync()

    def sync_prizes(self) -> Dict:
        """Sync team prizes (ranking + MVP) for completed matchdays.

        Thin delegation to the extracted ``prizes`` sync orchestrator (BR1.2).
        Same signature, same observable ``SyncResult`` payload, and same raised
        exceptions as before (BR1.1, FR5): the typed-exception propagation
        (``IntegrationBanError`` fatal; ``IntegrationTimeout/Unparseable/Request``
        escalate-at-write and PROPAGATE) lives in the orchestrator. The config
        read (raw ``get_db()`` SQL) and the atomic ``team_prizes`` writer go
        through a narrow port (BR2.2); the pure calculator and the writer are
        reused UNCHANGED. The domain package is imported lazily so the facade
        import graph is unchanged.
        """
        from app.services.sync.prizes import PrizesSyncOrchestrator
        from app.services.sync.prizes.infrastructure.prizes_adapter import (
            DataManagerPrizesAdapter,
        )

        orchestrator = PrizesSyncOrchestrator(
            client=self.client,
            championship_id=self.championship_id,
            user_id=self.user_id,
            data=DataManagerPrizesAdapter(),
        )
        return orchestrator.sync()

    def sync_all(self) -> Dict:
        """Run all sync operations
        
        Returns:
            Dict with results for each sync type
        """
        logger.info("=" * 60)
        logger.info("Starting full data synchronization")
        logger.info("=" * 60)
        
        # Sync players first so other syncs (transactions, rosters, etc.) have
        # the necessary player records for foreign-key constraints.
        results = {
            "players": self.sync_players_full(),
            "transactions": self.sync_transactions(),
            "clauses": self.sync_clauses(),
            "punishments_bonuses": self.sync_punishments_bonuses(),
            "dream_teams": self.sync_dream_teams_mvps(),
            "player_performance": self.sync_player_performance(),
            "rosters": self.sync_rosters(),
            "team_standings": self.sync_round_rankings(),
            "match_odds": self.sync_match_odds(),
            "prizes": self.sync_prizes(),
        }
        
        logger.info("=" * 60)
        logger.info("Full synchronization complete")
        logger.info("=" * 60)
        
        return results

