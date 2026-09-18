"""Unit tests for the pure prize calculator (new-contract phase, test-after).

These tests exercise :func:`app.services.prizes.calculator.calculate_round_prizes`
in isolation — no DB, no network, no sleeps — covering the new tie-splitting
contract (FR1 / BR3.1 / BR3.2) and the no-regression cases (FR1.3). They
complement the characterization safety net in
``test_prizes_characterization.py``.
"""

from app.services.prizes import (
    PrizeConfig,
    RoundTeamEntry,
    calculate_round_prizes,
)


def _config(*, money_per_ranking=3_000_000, ranking_mode="flop",
            users_to_rank=-1, money_per_point=0, mvp_bonus=0,
            dream_team_bonus=0):
    return PrizeConfig(
        money_per_ranking=money_per_ranking,
        ranking_mode=ranking_mode,
        users_to_rank=users_to_rank,
        money_per_point=money_per_point,
        mvp_bonus=mvp_bonus,
        dream_team_bonus=dream_team_bonus,
    )


def _by_team(results):
    return {r.team_id: r for r in results}


def test_no_tie_reproduces_current_per_position_formula():
    """No-regression: without ties, each team gets its exact position prize
    (same flop formula as before the change, FR1.3)."""
    config = _config(money_per_ranking=3_000_000, ranking_mode="flop")
    entries = [
        RoundTeamEntry("A", round_points=100),
        RoundTeamEntry("B", round_points=90),
        RoundTeamEntry("C", round_points=80),
        RoundTeamEntry("D", round_points=70),
    ]
    results = _by_team(calculate_round_prizes(config, entries,
                                              award_round_prizes=True))
    # total_pct = 4*5/2 = 10; flop prize(pos) = round(3M*pos/10)
    assert results["A"].ranking_prize == 300_000
    assert results["B"].ranking_prize == 600_000
    assert results["C"].ranking_prize == 900_000
    assert results["D"].ranking_prize == 1_200_000


def test_two_tied_teams_equal_split_jornada_5_example():
    """Jornada-5 reference example (championship 592416daa3a2dd871a7a9956):
    two teams tie occupying positions 3 (1.285.714) and 4 (1.714.286); the
    3.000.000 sum is split -> 1.500.000 each (FR1.2, BR3.1)."""
    # money_per_ranking=12M, 7 active members -> total_pct = 7*8/2 = 28.
    # flop prize(3) = round(12M*3/28) = 1285714,
    # flop prize(4) = round(12M*4/28) = 1714286; sum = 3000000.
    config = _config(money_per_ranking=12_000_000, ranking_mode="flop")
    entries = [
        RoundTeamEntry("T1", round_points=100),
        RoundTeamEntry("T2", round_points=90),
        RoundTeamEntry("A", round_points=80),   # tied, position 3
        RoundTeamEntry("B", round_points=80),   # tied, position 4
        RoundTeamEntry("T5", round_points=70),
        RoundTeamEntry("T6", round_points=60),
        RoundTeamEntry("T7", round_points=50),
    ]
    results = _by_team(calculate_round_prizes(config, entries,
                                              award_round_prizes=True))
    assert results["A"].ranking_prize == 1_500_000
    assert results["B"].ranking_prize == 1_500_000
    # Non-tied teams keep their exact single-position prize.
    assert results["T1"].ranking_prize == round(12_000_000 * 1 / 28)


def test_two_tied_teams_split_is_order_independent():
    """The equal split does not depend on the arbitrary API order among the
    tied teams: swapping A and B yields identical prizes (BR3.1)."""
    config = _config(money_per_ranking=3_000_000, ranking_mode="flop")
    forward = [
        RoundTeamEntry("W", round_points=100),
        RoundTeamEntry("X", round_points=90),
        RoundTeamEntry("A", round_points=80),
        RoundTeamEntry("B", round_points=80),
    ]
    reversed_ties = [
        RoundTeamEntry("W", round_points=100),
        RoundTeamEntry("X", round_points=90),
        RoundTeamEntry("B", round_points=80),
        RoundTeamEntry("A", round_points=80),
    ]
    r1 = _by_team(calculate_round_prizes(config, forward,
                                         award_round_prizes=True))
    r2 = _by_team(calculate_round_prizes(config, reversed_ties,
                                         award_round_prizes=True))
    assert r1["A"].ranking_prize == r1["B"].ranking_prize == 1_050_000
    assert r2["A"].ranking_prize == r2["B"].ranking_prize == 1_050_000


def test_three_tied_teams_sum_of_three_positions_divided_by_three():
    """Three teams tied share the summed prizes of their three contiguous
    positions, split by 3 (round() per part, BR3.2 / OQ1)."""
    config = _config(money_per_ranking=3_000_000, ranking_mode="flop")
    entries = [
        RoundTeamEntry("W", round_points=100),
        RoundTeamEntry("A", round_points=50),   # tied, positions 2,3,4
        RoundTeamEntry("B", round_points=50),
        RoundTeamEntry("C", round_points=50),
    ]
    results = _by_team(calculate_round_prizes(config, entries,
                                              award_round_prizes=True))
    # total_pct = 4*5/2 = 10; flop prize(2)=600000, prize(3)=900000,
    # prize(4)=1200000; sum = 2700000; split by 3 -> 900000 each.
    assert results["A"].ranking_prize == 900_000
    assert results["B"].ranking_prize == 900_000
    assert results["C"].ranking_prize == 900_000
    assert results["W"].ranking_prize == 300_000  # position 1, no tie


def test_gating_off_zeroes_ranking_mvp_dream_but_keeps_points():
    """When the round is not awardable, ranking/MVP/dream-team are 0 while
    points_prize is still paid (BR1.2 / BR1.1)."""
    config = _config(money_per_ranking=3_000_000, ranking_mode="flop",
                     money_per_point=1_000, mvp_bonus=5_000_000,
                     dream_team_bonus=1_000_000)
    entries = [
        RoundTeamEntry("A", round_points=100),
        RoundTeamEntry("B", round_points=80),
    ]
    results = _by_team(calculate_round_prizes(
        config, entries, award_round_prizes=False,
        mvp_team_id="A", dream_team_counts={"A": 2}))
    assert results["A"].ranking_prize == 0
    assert results["A"].mvp_prize == 0
    assert results["A"].dream_team_prize == 0
    # points_prize still paid
    assert results["A"].points_prize == 100_000
    assert results["B"].points_prize == 80_000


def test_team_with_zero_points_is_out_of_ranking():
    """A team with 0 round_points is not active: ranking_prize = 0, and it does
    not occupy a ranked position (BR2.1)."""
    config = _config(money_per_ranking=3_000_000, ranking_mode="flop")
    entries = [
        RoundTeamEntry("A", round_points=100),
        RoundTeamEntry("B", round_points=50),
        RoundTeamEntry("Z", round_points=0, api_position=3),
    ]
    results = _by_team(calculate_round_prizes(config, entries,
                                              award_round_prizes=True))
    # active_members = 2, total_pct = 3; flop prize(1)=round(3M/3)=1000000,
    # prize(2)=round(3M*2/3)=2000000. Z is inactive.
    assert results["A"].ranking_prize == 1_000_000
    assert results["B"].ranking_prize == 2_000_000
    assert results["Z"].ranking_prize == 0
    # Z keeps its raw API position for display since it is not ranked.
    assert results["Z"].display_position == 3


def test_users_to_rank_limits_the_premiable_set():
    """Only the first users_to_rank positions are ranked; teams beyond the cut
    get ranking_prize = 0 (BR2.1)."""
    config = _config(money_per_ranking=3_000_000, ranking_mode="flop",
                     users_to_rank=2)
    entries = [
        RoundTeamEntry("A", round_points=100),
        RoundTeamEntry("B", round_points=90),
        RoundTeamEntry("C", round_points=80),  # beyond users_to_rank
    ]
    results = _by_team(calculate_round_prizes(config, entries,
                                              award_round_prizes=True))
    # active_members = min(3, 2) = 2, total_pct = 3.
    assert results["A"].ranking_prize == 1_000_000
    assert results["B"].ranking_prize == 2_000_000
    assert results["C"].ranking_prize == 0
