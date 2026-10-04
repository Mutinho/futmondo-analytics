"""Application orchestrator for the ``players_full`` sync (BR2.3, BR4.1).

Hosts the orchestration formerly inline in ``DataSyncService.sync_players_full``:
the full player ingestion from the injected Futmondo client, the record/stat
payload assembly, the batch upsert, the orphan cleanup (non-critical), the
per-championship stats persistence (non-critical), the favorites selection and
persistence (non-critical), the error handling, and delegation to the persistence
port. The observable ``SyncResult`` payload is preserved byte-for-byte (FR5.3) —
including the ``players`` data type and the ``records_synced`` key, and the
``sync_all`` name-key divergence that routes this result under ``players``.

The favorites persistence resolves ``user_id`` as ``self.client.user_id or ''``
exactly as the former inline ``_save_favorites`` did, then delegates the raw SQL
to the adapter (BR2.2). No new credentials reach any log.

No credentials ever reach an exception message or log (BR4.2): the failure path
logs ``str(e)`` and stores it as ``error_message``, exactly as before.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from app.services.futmondo_client import FutmondoClient
from app.services.sync.players_full.domain.ports import PlayersFullSyncDataPort
from app.services.sync.players_full.infrastructure.players_full_adapter import (
    DataManagerPlayersFullAdapter,
)

logger = logging.getLogger(__name__)


class PlayersFullSyncOrchestrator:
    """Coordinate the full player ingestion, persistence, cleanup and favorites."""

    def __init__(
        self,
        client: FutmondoClient,
        championship_id: str,
        data: Optional[PlayersFullSyncDataPort] = None,
    ) -> None:
        """Create the orchestrator.

        Args:
            client: The Futmondo client used for ingestion (injected by the
                facade, so tests pass a fake — no network).
            championship_id: The championship whose players are synced.
            data: The persistence port. Defaults to the production
                ``DataManagerPlayersFullAdapter``; tests inject a stub port.
        """
        self.client = client
        self.championship_id = championship_id
        self.data: PlayersFullSyncDataPort = (
            data if data is not None else DataManagerPlayersFullAdapter()
        )

    def sync(self) -> Dict:
        """Sync all players (full update) (equivalent to the former method)."""
        start_time = time.time()
        logger.info("Starting full player sync...")

        try:
            # Get all championship players
            players_data = self.client.get_championship_players(self.championship_id)
            if not players_data or not players_data.get("players"):
                raise Exception("Could not fetch championship players")

            players = players_data.get("players", [])
            logger.info(f"Found {len(players)} players to sync")

            total_synced = 0
            stats_payload: List[Dict] = []
            player_records: List[Dict] = []

            for player in players:
                player_id = player.get("id")
                if not player_id:
                    continue

                # Collect player data for batch insert
                player_records.append({
                    "id": player_id,
                    "name": player.get("name", ""),
                    "role": player.get("role", ""),
                    "role2": player.get("role2", ""),
                    "teamId": player.get("teamId", ""),
                    "team": player.get("team", ""),
                    "slug": player.get("slug", ""),
                    "photo": player.get("photo", ""),
                    "value": player.get("value", 0),
                })

                clause_data = player.get("clause") or {}
                average_data = player.get("average") or {}
                owner_team_id = player.get("userteamId")
                owner_team_name = player.get("userteam")
                owner_user_id = (
                    player.get("userteamUserId")
                    or player.get("userId")
                    or owner_team_id
                )

                stats_payload.append({
                    "player_id": player_id,
                    "owner_team_id": owner_team_id,
                    "owner_team_name": owner_team_name,
                    "owner_user_id": owner_user_id,
                    "clause_price": clause_data.get("price"),
                    "suggested_clause": clause_data.get("suggestedClause"),
                    "clause_date": clause_data.get("date"),
                    "average_last_five": average_data.get("averageLastFive"),
                    "average_overall": average_data.get("average")
                })

            # Batch insert all players in one transaction
            total_synced = self.data.save_players_batch(player_records)

            # Remove stale players: not in the current API list AND with no history.
            # Keeps historical players (transactions/rosters/etc.); only drops junk.
            try:
                live_ids = [p["id"] for p in player_records if p.get("id")]
                orphans = self.data.delete_orphan_players(live_ids)
                if orphans:
                    logger.info(f"Removed {orphans} orphan players (no API entry, no history)")
            except Exception as orphan_err:
                logger.warning(f"Orphan player cleanup failed: {orphan_err}")

            if stats_payload:
                try:
                    self.data.save_player_championship_stats(self.championship_id, stats_payload)
                except Exception as stats_err:
                    logger.warning(f"Failed to persist player championship stats: {stats_err}")

            # Sync favorites — store which players the user has marked as fav
            try:
                favorites = []
                for player in players:
                    if player.get("fav") is True and not player.get("userteamId"):
                        favorites.append(player.get("id"))
                # Resolve user_id exactly as the former inline _save_favorites did.
                self.data.save_favorites(
                    self.championship_id, self.client.user_id or "", favorites
                )
                logger.info(f"Synced {len(favorites)} favorites")
            except Exception as fav_err:
                logger.warning(f"Failed to sync favorites: {fav_err}")

            duration = time.time() - start_time
            status = "success"

            # Update sync metadata
            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="players",
                last_sync_date=datetime.now(),
                records_synced=total_synced,
                sync_duration_seconds=duration,
                sync_status=status
            )

            logger.info(f"Player sync complete: {total_synced} players in {duration:.2f}s")

            # NOTE: futmondo_team_id is saved per-user at login (_auto_detect_championships),
            # never here — the sync runs with one user's credentials and must not write
            # another user's team into their row (that leaked one user's balance to others).

            return {
                "status": status,
                "records_synced": total_synced,
                "duration_seconds": duration
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Player sync failed: {e}", exc_info=True)

            self.data.update_sync_metadata(
                championship_id=self.championship_id,
                data_type="players",
                sync_status="error",
                error_message=str(e),
                sync_duration_seconds=duration
            )

            return {
                "status": "error",
                "error": str(e),
                "duration_seconds": duration
            }
