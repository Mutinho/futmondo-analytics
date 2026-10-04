"""Consumer-owned data port for the ``prizes`` sync (BR2.1, BR2.3).

``PrizesSyncDataPort`` is a structural :class:`typing.Protocol` describing ONLY
the persistence operations the orchestrator consumes. It lives in the domain
layer, imports neither ``infrastructure/`` nor any framework, and contains no SQL
(BR2.1, BR2.2). ``get_prize_config`` wraps the raw ``get_db()`` SELECT, and
``replace_team_prizes`` wraps the atomic writer; both are moved VERBATIM into the
adapter — never into ``data_manager_v2.py`` and never rewritten.
"""

from typing import Iterable, Optional, Protocol, Sequence, Tuple


class PrizesSyncDataPort(Protocol):
    """Structural type of the persistence surface the prizes sync consumes."""

    def get_prize_config(self, championship_id: str) -> Optional[Tuple]:
        """Return the raw championship prize-config row, or None if absent.

        The row shape is the historical SELECT's column order:
        ``(money_per_ranking, mvp_bonus, ranking_mode, users_to_rank,
        money_per_point, dream_team_bonus)``.
        """
        ...

    def replace_team_prizes(
        self,
        championship_id: str,
        rows: Iterable[Sequence[object]],
        valid_matchdays: Iterable[int],
    ) -> int:
        """Atomically replace the ``team_prizes`` set; return stale rows deleted.

        Delegates to ``prizes.team_prizes_writer.replace_team_prizes`` UNCHANGED
        (NFR2, BR5.1): a failure PROPAGATES (never swallowed), so the write-point
        failure stays fatal and no mixed state survives.
        """
        ...
