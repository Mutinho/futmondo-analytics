"""Application orchestrator for the ``prizes`` sync context (BR2.3, BR4.1).

Uniformises the orchestration formerly inline in ``DataSyncService.sync_prizes``:
the config read (via the port's ``get_prize_config``), the early-return
no-config / no-prizes / no-standings / no-teams / no-rounds short-circuits, the
per-round ingestion from the injected Futmondo client, the advanced-pseudo-round
handling, the ``round_fully_played`` gating, the MVP/dream-team attribution, the
pure prize math (via ``prizes.calculator`` — UNCHANGED), the atomic persistence
(via the port's ``replace_team_prizes`` — the writer UNCHANGED), the
throttling, the typed-exception propagation (``IntegrationBanError`` fatal;
``IntegrationTimeout/Unparseable/Request`` escalate-at-write and PROPAGATE), and
the final error safety net. The observable ``SyncResult`` payload is preserved
byte-for-byte (FR5.3) — including the ``rounds_processed`` / ``records_synced`` /
``stale_prizes_removed`` keys and the special early-return statuses.

The structured ``_log_integration_failure`` NEVER emits a password/token (BR4.2):
the typed exception only holds ``failure_mode``/``status``/``endpoint`` by
construction, and ``reason`` is ``str(exc)`` composed from those fields alone.
"""

import logging
import time
from typing import Optional

from app.services.futmondo_client import FutmondoClient
from app.services.integration_errors import (
    IntegrationBanError,
    IntegrationError,
    IntegrationRequestError,
    IntegrationTimeoutError,
    IntegrationUnparseableError,
)
from app.services.prizes import (
    PrizeConfig,
    RoundTeamEntry,
    calculate_round_prizes,
)
from app.services.sync.prizes.domain.ports import PrizesSyncDataPort
from app.services.sync.prizes.infrastructure.prizes_adapter import (
    DataManagerPrizesAdapter,
)

logger = logging.getLogger(__name__)


def _log_integration_failure(
    level: int,
    sync_step: str,
    exc: "IntegrationError",
    *,
    task_id: Optional[str] = None,
) -> None:
    """Emit a single-line structured key=value integration-failure log (NFR1).

    Fields: ``sync_step``, ``failure_mode``, ``status``, ``endpoint``,
    ``task_id``, ``reason`` — the non-sensitive context carried by the typed
    exception. It NEVER receives or emits a password/token (BR4.2/NFR3): the
    exception itself only holds ``failure_mode``/``status``/``endpoint`` by
    construction, and ``reason`` is ``str(exc)``, which is composed from those
    fields alone. WARNING for recoverable, ERROR for fatal (caller-chosen).
    """
    status = "" if exc.status is None else exc.status
    endpoint = "" if exc.endpoint is None else exc.endpoint
    tid = "" if task_id is None else task_id
    logger.log(
        level,
        "integration failure "
        "sync_step=%s failure_mode=%s status=%s endpoint=%s task_id=%s reason=%r",
        sync_step,
        exc.failure_mode,
        status,
        endpoint,
        tid,
        str(exc),
    )


class PrizesSyncOrchestrator:
    """Coordinate the per-round prize computation and atomic persistence."""

    def __init__(
        self,
        client: FutmondoClient,
        championship_id: str,
        user_id: str = "",
        data: Optional[PrizesSyncDataPort] = None,
    ) -> None:
        """Create the orchestrator.

        Args:
            client: The Futmondo client used for ingestion (injected by the
                facade, so tests pass a fake — no network).
            championship_id: The championship whose prizes are synced.
            user_id: The optional per-user task id used only for structured
                integration-failure logging (injected from the facade).
            data: The persistence port. Defaults to the production
                ``DataManagerPrizesAdapter``; tests inject a stub port.
        """
        self.client = client
        self.championship_id = championship_id
        self.user_id = user_id
        self.data: PrizesSyncDataPort = (
            data if data is not None else DataManagerPrizesAdapter()
        )

    def sync(self) -> dict:
        """Sync team prizes for completed matchdays (equivalent to the former method)."""
        start_time = time.time()
        logger.info("Starting prizes sync...")

        try:
            # Get championship config for prize calculation (raw SELECT via port).
            row = self.data.get_prize_config(self.championship_id)

            if not row:
                return {"status": "no_config", "records_synced": 0, "duration_seconds": time.time() - start_time}

            money_per_ranking = row[0] or 0
            mvp_bonus = row[1] or 0
            ranking_mode = row[2] or "flop"
            users_to_rank = row[3] if row[3] is not None else -1
            money_per_point = row[4] or 0
            dream_team_bonus = row[5] or 0

            if money_per_ranking <= 0 and mvp_bonus <= 0 and money_per_point <= 0 and dream_team_bonus <= 0:
                return {"status": "no_prizes_configured", "records_synced": 0, "duration_seconds": time.time() - start_time}

            # Get teams from standings
            standings_data = self.client.get_matchday_standings(self.championship_id)
            if not standings_data:
                return {"status": "no_standings", "records_synced": 0, "duration_seconds": time.time() - start_time}

            team_list = standings_data.get("teams", standings_data.get("ranking", []))
            if not team_list:
                return {"status": "no_teams", "records_synced": 0, "duration_seconds": time.time() - start_time}

            # Get a sample userteam_id for API calls
            sample_userteam_id = team_list[0].get("teamid") or team_list[0].get("id")
            all_team_ids = []
            for t in team_list:
                tid = t.get("teamid") or t.get("id")
                if tid:
                    all_team_ids.append(tid)

            # Get rounds
            rounds_info = self.client.get_userteam_rounds(self.championship_id, sample_userteam_id) or []
            # Process ALL rounds (not just closed) — points_prize is paid immediately,
            # ranking_prize only when the round is fully closed
            all_rounds = [r for r in rounds_info if r.get("number")]
            closed_statuses = {"closed"}

            if not all_rounds:
                return {"status": "no_rounds", "records_synced": 0, "duration_seconds": time.time() - start_time}

            # Check which rounds already have prizes synced — skip none, always recalculate
            # (positions from API may have changed or been stored incorrectly)

            records_synced = 0
            rounds_processed = 0
            valid_matchdays = set()
            all_prizes_to_save = []

            for round_info in all_rounds:
                raw_number = round_info.get("number")
                round_id = round_info.get("id") or round_info.get("_id")
                is_closed = round_info.get("status") in closed_statuses

                if not raw_number or not round_id:
                    continue

                # Futmondo can report "advanced" pseudo-rounds with a non-integer
                # number (e.g. 0.5) for a game brought forward. These are NOT a
                # real matchday: they only have the advanced match(es) played, so
                # they must NEVER award ranking/MVP/dream-team prizes. However,
                # Futmondo DOES pay points_prize immediately for the points scored
                # in the already-finished matches, so we still process them for
                # points only.
                #
                # The `matchday` column is an integer and Postgres rounds a float
                # on insert (0.5 -> 1), which would collide with and corrupt the
                # real matchday 1. To avoid any collision with real matchdays
                # (1..38) we store advanced pseudo-rounds under a dedicated
                # negative synthetic matchday derived from the number
                # (e.g. 0.5 -> -5), which is unique per pseudo-round and never
                # clashes with a real one. Aggregations SUM across all matchdays,
                # so the points_prize is still counted in balances/finances.
                try:
                    matchday_f = float(raw_number)
                except (TypeError, ValueError):
                    logger.info(f"Skipping round with non-numeric number {raw_number!r}")
                    continue

                is_advanced_pseudo_round = matchday_f != int(matchday_f)
                if is_advanced_pseudo_round:
                    matchday = -int(round(matchday_f * 10))  # 0.5 -> -5
                    logger.info(
                        f"Advanced pseudo-round number={raw_number!r} stored as "
                        f"synthetic matchday {matchday} (points_prize only)"
                    )
                else:
                    matchday = int(matchday_f)

                # A round can be reported as "closed" by Futmondo even when it
                # still has postponed/unplayed matches (e.g. a matchday with only
                # an advanced game). Ranking/MVP/dream-team prizes must only be
                # awarded once EVERY match of the round is finished (status "F").
                # points_prize is still paid immediately for whatever points exist.
                round_fully_played = is_closed
                if is_closed and not is_advanced_pseudo_round:
                    matches_data = self.client.get_round_matches(self.championship_id, round_id, sample_userteam_id)
                    matches = []
                    if isinstance(matches_data, dict):
                        matches = matches_data.get("matches", [])
                    elif isinstance(matches_data, list):
                        matches = matches_data
                    if matches:
                        round_fully_played = all(m.get("status") == "F" for m in matches)
                        if not round_fully_played:
                            logger.info(
                                "Round %s is 'closed' but has unfinished/postponed matches; "
                                "paying points_prize only (no ranking/MVP/dream-team prizes yet)",
                                matchday,
                            )
                    time.sleep(0.2)

                # Effective flag used for ranking/MVP/dream-team prizes.
                # Advanced pseudo-rounds never award them (points_prize only).
                award_round_prizes = is_closed and round_fully_played and not is_advanced_pseudo_round

                # Get ranking directly from API
                ranking_data = self.client.get_round_ranking(
                    championship_id=self.championship_id,
                    round_number=matchday,
                    round_id=round_id,
                    userteam_id=sample_userteam_id
                )
                ranking_list = []
                if isinstance(ranking_data, dict):
                    ranking_list = ranking_data.get("ranking", ranking_data.get("teams", []))
                elif isinstance(ranking_data, list):
                    ranking_list = ranking_data
                time.sleep(0.3)

                if not ranking_list:
                    logger.info(f"No ranking data for round {matchday}, skipping")
                    continue

                # Get dream team to find MVP and count dream team players per team (only for closed rounds)
                mvp_team_id = None
                dream_team_counts = {}
                if (mvp_bonus > 0 or dream_team_bonus > 0) and award_round_prizes:
                    dream_data = self.client.get_dream_team(self.championship_id, round_id=round_id)
                    mvp_player_id = None
                    dream_team_player_ids = set()
                    if dream_data and isinstance(dream_data, dict):
                        mvp_player_id = dream_data.get("mvp")
                        dream_team_players = dream_data.get("players", [])
                        for p in dream_team_players:
                            pid = p.get("id") if isinstance(p, dict) else p
                            if pid:
                                dream_team_player_ids.add(pid)

                    if mvp_player_id or (dream_team_bonus > 0 and dream_team_player_ids):
                        # Check each team's lineup to find who had the MVP and count dream team players
                        for tid in all_team_ids:
                            lineup = self.client.get_round_lineup(self.championship_id, round_id, tid)
                            if lineup:
                                lineup_ids = [p.get("id") for p in lineup]
                                if mvp_player_id and mvp_player_id in lineup_ids and mvp_team_id is None:
                                    mvp_team_id = tid
                                    logger.info(f"Round {matchday} MVP ({mvp_player_id}) belongs to team {tid}")
                                if dream_team_bonus > 0 and dream_team_player_ids:
                                    count = sum(1 for pid in lineup_ids if pid in dream_team_player_ids)
                                    if count > 0:
                                        dream_team_counts[tid] = count
                            time.sleep(0.2)

                # Materialize the round entries for the pure calculator.
                # The orchestrator only orchestrates: ingestion (above) and
                # persistence (below); the prize math (including the tie-split
                # rule, FR1) lives in app.services.prizes.calculator (NFR4).
                round_entries = []
                for entry in ranking_list:
                    team_id = entry.get("id") or entry.get("teamid")
                    if not team_id:
                        continue
                    round_entries.append(RoundTeamEntry(
                        team_id=team_id,
                        round_points=entry.get("points", 0) or 0,
                        api_position=entry.get("position", 0) or 0,
                    ))

                prize_config = PrizeConfig(
                    money_per_ranking=money_per_ranking,
                    ranking_mode=ranking_mode,
                    users_to_rank=users_to_rank,
                    money_per_point=money_per_point,
                    mvp_bonus=mvp_bonus,
                    dream_team_bonus=dream_team_bonus,
                )
                computed_prizes = calculate_round_prizes(
                    config=prize_config,
                    entries=round_entries,
                    award_round_prizes=award_round_prizes,
                    mvp_team_id=mvp_team_id,
                    dream_team_counts=dream_team_counts,
                )

                # Map each computed TeamRoundPrize to a team_prizes row.
                # display_position is persisted in the `position` column (R-03).
                prizes_to_save = []
                for prize in computed_prizes:
                    prizes_to_save.append((
                        self.championship_id, prize.team_id, matchday,
                        prize.ranking_prize, prize.mvp_prize,
                        prize.display_position, prize.points_prize,
                        prize.dream_team_prize,
                    ))

                # Accumulate rows for a single atomic replacement (NFR2, BR5.1):
                # the persistence happens once, after the loop, inside one
                # transaction via team_prizes_writer.replace_team_prizes.
                if prizes_to_save:
                    all_prizes_to_save.extend(prizes_to_save)
                    records_synced += len(prizes_to_save)
                    rounds_processed += 1
                    valid_matchdays.add(matchday)
                    logger.info(f"Round {matchday}: computed {len(prizes_to_save)} prize records")

                time.sleep(0.3)

            # Atomic replacement (NFR2, BR5.1): upsert every computed row AND
            # delete stale matchdays in a SINGLE transaction behind a narrow,
            # testable function outside this god-file. A failure rolls back the
            # whole thing (all-or-nothing) and PROPAGATES — the previous set stays
            # intact and the write-point failure is fatal (BR2.3/BR3.2), no longer
            # swallowed by a warning that left a mixed state.
            stale_deleted = 0
            if all_prizes_to_save or valid_matchdays:
                stale_deleted = self.data.replace_team_prizes(
                    self.championship_id, all_prizes_to_save, valid_matchdays
                )

            duration = time.time() - start_time
            status = "success" if rounds_processed > 0 else "no_new_data"

            logger.info(f"Prizes sync complete: {rounds_processed} rounds, {records_synced} records in {duration:.2f}s")

            return {
                "status": status,
                "rounds_processed": rounds_processed,
                "records_synced": records_synced,
                "stale_prizes_removed": stale_deleted,
                "duration_seconds": duration
            }

        except IntegrationBanError as ban_err:
            # FATAL (BR2.2/BR3.2): a ban aborts the step clean and PROPAGATES;
            # no half-written data (the atomic writer guarantees all-or-nothing).
            duration = time.time() - start_time
            _log_integration_failure(
                logging.ERROR, "prizes", ban_err, task_id=self.user_id or None
            )
            raise
        except (
            IntegrationTimeoutError,
            IntegrationUnparseableError,
            IntegrationRequestError,
        ) as rec_err:
            # RECOVERABLE by default (BR2.1). Inside sync_prizes the integration
            # calls that reach here happen at/around the team_prizes write point,
            # so BR2.3 (escalation-at-write) applies: PROPAGATE so the sync route
            # aborts clean rather than degrade-and-continue over a write that
            # could corrupt data. The structured WARNING records the recoverable
            # nature; the route decides DEGRADED vs abort with the step context.
            duration = time.time() - start_time
            _log_integration_failure(
                logging.WARNING, "prizes", rec_err, task_id=self.user_id or None
            )
            raise
        except Exception as e:
            # Final safety net (BR2.2): never masks the typed branches above.
            duration = time.time() - start_time
            logger.error(f"Prizes sync failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "records_synced": 0,
                "duration_seconds": duration
            }
