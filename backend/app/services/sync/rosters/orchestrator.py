"""Application orchestrator for the ``rosters`` sync (BR2.3, BR4.1).

Hosts the orchestration formerly inline in ``DataSyncService.sync_rosters``: the
round discovery (via the injected ``find_championship`` callable plus the
``get_matchday_standings`` / ``get_userteam_rounds`` mapping), the closed-round
selection, the new-round filtering by matchday, the per-team roster ingestion
from the injected Futmondo client (ONLY the ``players`` list, never ``bench``),
the ``time.sleep(0.1)`` throttling, the error handling, and delegation to the
persistence port. The observable ``SyncResult`` payload is preserved
byte-for-byte (FR5.3).

``find_championship`` is NOT re-implemented here (it stays in the facade and is
injected as a callable), so there is a single source of truth for it (BR2.3).

No credentials ever reach an exception message or log (BR4.2): the failure path
logs ``str(e)`` and stores it as ``error_message``, exactly as before.
"""

import logging
import time
from datetime import datetime
from typing import Callable, Dict, Optional, Tuple

from app.services.futmondo_client import FutmondoClient
from app.services.sync.rosters.domain.ports import RostersSyncDataPort
from app.services.sync.rosters.infrastructure.rosters_adapter import (
    DataManagerRostersAdapter,
)

logger = logging.getLogger(__name__)


class RostersSyncOrchestrator:
    """Coordinate the per-round, per-team roster ingestion and persistence."""

    def __init__(
        self,
        client: FutmondoClient,
        championship_id: str,
        find_championship: Callable[[], Tuple[Optional[Dict], Optional[Dict]]],
        data: Optional[RostersSyncDataPort] = None,
    ) -> None:
        """Create the orchestrator.

        Args:
            client: The Futmondo client used for ingestion (injected by the
                facade, so tests pass a fake — no network).
            championship_id: The championship whose rosters are synced.
            find_championship: Callable returning ``(league_data,
                championship_data)``; injected from the facade's
                ``_find_championship`` so it is not duplicated (BR2.3).
            data: The persistence port. Defaults to the production
                ``DataManagerRostersAdapter``; tests inject a stub port.
        """
        self.client = client
        self.championship_id = championship_id
        self.find_championship = find_championship
        self.data: RostersSyncDataPort = (
            data if data is not None else DataManagerRostersAdapter()
        )

    def sync(self) -> Dict:
        """Sync team rosters for new matchdays (equivalent to the former method)."""
        start_time = time.time()
        logger.info("Starting roster sync...")

        try:
            # Get last sync metadata
            last_sync = self.data.get_last_sync_metadata(self.championship_id, "rosters")
            last_matchday = last_sync.get("last_sync_matchday", 0) if last_sync else 0
            if not last_matchday:
                last_matchday = 0

            logger.info(f"Last synced matchday: {last_matchday}")

            league_data, championship_data = self.find_championship()

            rounds = []
            if league_data:
                rounds = league_data.get("rounds", []) or []
            if not rounds and championship_data:
                rounds = championship_data.get("rounds", []) or []

            round_numbers = {}
            try:
                sample_team = None
                standings_data = self.client.get_matchday_standings(self.championship_id)
                if standings_data:
                    team_list = standings_data.get("teams", standings_data.get("data", []))
                    if team_list:
                        sample_team = team_list[0]
                if sample_team:
                    sample_team_id = sample_team.get("id", sample_team.get("teamid"))
                    if sample_team_id:
                        user_rounds = self.client.get_userteam_rounds(self.championship_id, sample_team_id) or []
                        for idx, entry in enumerate(user_rounds, start=1):
                            round_id = entry.get("id")
                            number = entry.get("number") or idx
                            if round_id:
                                round_numbers[round_id] = number
            except Exception as map_err:
                logger.warning(f"Could not map round numbers for rosters: {map_err}")

            closed_statuses = {"closed", "finished", "completed", "complete", "past", "played"}
            closed_rounds = [
                r for r in rounds
                if str(r.get("status", "")).lower() in closed_statuses
            ]
            if not closed_rounds and round_numbers:
                closed_rounds = [
                    {"_id": round_id, "status": "closed", "number": number}
                    for round_id, number in sorted(round_numbers.items(), key=lambda x: x[1])
                ]

            rounds_to_sync = []
            for idx, r in enumerate(closed_rounds, start=1):
                round_id = r.get("_id")
                number = round_numbers.get(round_id, idx)
                if number > last_matchday:
                    rounds_to_sync.append({**r, "number": number})

            # Get teams
            championship_teams_data = self.client.get_matchday_standings(self.championship_id)
            teams = []
            if championship_teams_data:
                teams = championship_teams_data.get("teams", championship_teams_data.get("data", []))

            logger.info(f"Found {len(rounds_to_sync)} new rounds and {len(teams)} teams to sync")

            total_synced = 0
            max_matchday = last_matchday

            for round_data in rounds_to_sync:
                round_id = round_data.get("_id")
                matchday = round_data.get("number", 0)

                if not round_id:
                    continue

                for team in teams:
                    userteam_id = team.get("id", team.get("teamid", ""))
                    team_id = team.get("teamid", userteam_id)

                    if not userteam_id:
                        continue

                    try:
                        # Get roster for this round
                        roster_data = self.client.get_user_roundlineup(self.championship_id, round_id, userteam_id)
                        if not roster_data:
                            continue

                        # Get players from roster (ONLY from "players", NOT from "bench")
                        roster_players = roster_data.get("players", [])
                        if roster_players:
                            self.data.save_team_roster(self.championship_id, team_id, roster_players, matchday=matchday)
                            total_synced += 1

                        time.sleep(0.1)  # Rate limiting

                    except Exception as e:
                        logger.warning(f"Failed to fetch roster for team {userteam_id} in round {round_id}: {e}")
                        continue

                max_matchday = max(max_matchday, matchday)

            duration = time.time() - start_time
            status = "success" if total_synced > 0 or last_matchday == 0 else "no_new_data"

            # Update sync metadata
            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="rosters",
                last_sync_matchday=max_matchday,
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status,
            )

            logger.info(f"Roster sync complete: {total_synced} rosters in {duration:.2f}s")

            return {
                "status": status,
                "records_synced": total_synced,
                "last_sync_matchday": max_matchday,
                "duration_seconds": duration,
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Roster sync failed: {e}", exc_info=True)

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="rosters",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration,
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration,
            }
