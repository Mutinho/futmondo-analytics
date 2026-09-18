"""Pure calculation of matchday prizes (no I/O, no SQL).

This module implements :func:`calculate_round_prizes`, the pure function that
computes every prize term for a single round from already-materialized inputs.
It is deterministic (same inputs -> same outputs) and has no dependency on the
database or the Futmondo API client, which makes it testable in isolation at
zero cost (NFR1/NFR3).

Business rules implemented (see functional-design/rules.md):

  * BR1.1  points_prize is always paid.
  * BR1.2  ranking / MVP / dream-team prizes are only awarded when the round is
           fully closed (``award_round_prizes``).
  * BR2.1  only active teams (round_points > 0) enter the ranking, limited by
           ``users_to_rank`` when configured.
  * BR2.2  per-position prize follows the proportional flop/top formula
           (reproduced EXACTLY from the previous in-line implementation).
  * BR3.1  NEW: teams tied on round_points share the summed prizes of the
           contiguous positions their tie group occupies, split equally.
  * BR3.2  each split part is rounded with ``round()`` (a +/-1 remainder from a
           non-integer division is accepted, OQ1).

Naming disambiguates the two senses of "points": ``*_points`` is the sporting
metric and ``*_prize`` is a monetary amount (team practice / NFR4).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class PrizeConfig:
    """Championship prize configuration for a round."""

    money_per_ranking: int
    ranking_mode: str  # "flop" | "top"
    users_to_rank: int  # number of ranked positions; -1 means all
    money_per_point: int
    mvp_bonus: int
    dream_team_bonus: int


@dataclass(frozen=True)
class RoundTeamEntry:
    """A team's entry in a round ranking (calculation input)."""

    team_id: str
    round_points: int
    # Raw index-order position as returned by the API. Preserved so the
    # display/persistence position matches the previous behavior for teams that
    # are outside the ranked/active set.
    api_position: int = 0


@dataclass(frozen=True)
class TeamRoundPrize:
    """Per-team prize result for a round (calculation output)."""

    team_id: str
    ranking_prize: int
    mvp_prize: int
    points_prize: int
    dream_team_prize: int
    display_position: int


def _position_prize(position: int, active_members: int, total_pct: int,
                    money_per_ranking: int, ranking_mode: str) -> int:
    """Base prize for a single ranked position (BR2.2).

    Reproduces EXACTLY the previous in-line formula:
      flop: ratio = position / total_pct
      top:  ratio = (active_members - position + 1) / total_pct
      prize = round(money_per_ranking * ratio)
    """
    if total_pct <= 0 or money_per_ranking <= 0:
        return 0
    if ranking_mode == "flop":
        ratio = position / total_pct
    else:
        ratio = (active_members - position + 1) / total_pct
    return round(money_per_ranking * ratio)


def calculate_round_prizes(
    config: PrizeConfig,
    entries: List[RoundTeamEntry],
    award_round_prizes: bool,
    mvp_team_id: Optional[str] = None,
    dream_team_counts: Optional[Dict[str, int]] = None,
) -> List[TeamRoundPrize]:
    """Compute every prize term for a round.

    Args:
        config: championship prize configuration.
        entries: one :class:`RoundTeamEntry` per team in the round, in the
            order the API returned them (the tie-splitting result does NOT
            depend on the order among tied teams — BR3.1).
        award_round_prizes: gating flag (BR1.2). When ``False``, ranking, MVP
            and dream-team prizes are all 0; points_prize still applies.
        mvp_team_id: team that owns the round MVP player, if any.
        dream_team_counts: per-team count of dream-team players, if any.

    Returns:
        One :class:`TeamRoundPrize` per input entry, preserving input order.
    """
    dream_team_counts = dream_team_counts or {}

    # BR2.1 — eligibility: active teams (round_points > 0), in API order,
    # limited by users_to_rank when configured. This mirrors the previous
    # ``active_position_map`` construction exactly.
    members = (
        config.users_to_rank
        if config.users_to_rank > 0
        else len([e for e in entries if e.round_points > 0])
    )
    active_entries = [e for e in entries if e.round_points > 0]
    active_members = min(len(active_entries), members)
    total_pct = active_members * (active_members + 1) // 2

    # Position among active members (1-based, API order), only up to `members`.
    active_position_map: Dict[str, int] = {}
    for idx, entry in enumerate(active_entries):
        position = idx + 1
        if position <= members:
            active_position_map[entry.team_id] = position

    # BR3.1 — group the ranked (premiable) teams by round_points. Each group of
    # N teams occupies the contiguous positions p..p+N-1. The equal split is
    # computed once per group so it never depends on the arbitrary API order
    # among tied teams.
    ranking_prize_map: Dict[str, int] = {}
    if award_round_prizes and total_pct > 0 and config.money_per_ranking > 0:
        ranked = [
            (active_position_map[e.team_id], e.team_id)
            for e in active_entries
            if e.team_id in active_position_map
        ]
        # Points keyed by team for grouping.
        points_by_team = {e.team_id: e.round_points for e in active_entries}
        # Group by shared round_points. Because positions are assigned in the
        # points order the API already sorted, teams with equal points occupy
        # contiguous positions; we group by points value directly so the result
        # is independent of the order among equals.
        groups: Dict[int, List[int]] = {}
        for position, team_id in ranked:
            groups.setdefault(points_by_team[team_id], []).append(position)

        prize_by_position: Dict[int, int] = {}
        for points_value, positions in groups.items():
            positions_sorted = sorted(positions)
            n = len(positions_sorted)
            sum_positions = sum(
                _position_prize(
                    pos, active_members, total_pct,
                    config.money_per_ranking, config.ranking_mode,
                )
                for pos in positions_sorted
            )
            # BR3.1 / BR3.2: equal split, rounded per part. N=1 collapses to the
            # exact single-position prize (no regression, FR1.3).
            share = round(sum_positions / n)
            for pos in positions_sorted:
                prize_by_position[pos] = share

        for position, team_id in ranked:
            ranking_prize_map[team_id] = prize_by_position[position]

    results: List[TeamRoundPrize] = []
    for entry in entries:
        team_id = entry.team_id

        ranking_prize = ranking_prize_map.get(team_id, 0)

        mvp_prize = (
            config.mvp_bonus
            if (team_id == mvp_team_id and award_round_prizes)
            else 0
        )

        # BR1.1 — points_prize is always paid.
        points_prize = (
            round(entry.round_points * config.money_per_point)
            if config.money_per_point > 0
            else 0
        )

        dream_team_prize = 0
        if config.dream_team_bonus > 0 and award_round_prizes:
            dt_count = dream_team_counts.get(team_id, 0)
            dream_team_prize = round(dt_count * config.dream_team_bonus)

        # Display/persist position: the assigned ranking position when active,
        # otherwise the raw API position (mirrors the previous behavior).
        active_position = active_position_map.get(team_id)
        display_position = active_position if active_position else entry.api_position

        results.append(
            TeamRoundPrize(
                team_id=team_id,
                ranking_prize=ranking_prize,
                mvp_prize=mvp_prize,
                points_prize=points_prize,
                dream_team_prize=dream_team_prize,
                display_position=display_position,
            )
        )

    return results
