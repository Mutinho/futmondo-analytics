"""Read-from-sync layer for ``GET /api/v1/market/today`` catalog (BR4.1, BR5.1).

The market catalog is already cached in ``market_today`` (per championship/date,
with the requesting user's private ``bid`` stripped). This module reads that
catalog so the router does not run the SELECT inline, and exposes the pure
``available_for_bids`` derivation so it is testable in isolation.

The single live call (``POST /1/market/players`` for the user's own bids) stays
in the router: it is irreducible without a schema change (the bids are not in
Neon, verified) and the response contract requires them. On its failure with a
catalog available, the router degrades bid fields to zero (BR3.2); it never
fails the whole response.

All SQL here is parameterized through ``db.adapt_params`` (BR1.1).
"""

import json as _json
import logging
from datetime import date
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def read_market_catalog(db, championship_id: str) -> Optional[List[Dict]]:
    """Read today's cached market catalog for a championship.

    Reads the full per-player ``raw_json`` rows persisted in ``market_today`` so
    the caller receives the SAME player dict shape the live route produces (the
    cache stores the live payload with only the private ``bid`` stripped).

    Args:
        db: db-connection handle.
        championship_id: championship scope.

    Returns:
        - a non-empty list of player dicts when today's catalog is cached;
        - ``None`` when there are 0 cached rows → the router must fall back to
          the live route and log a sync-miss (BR3.1).

    Never raises for an empty catalog; it returns ``None`` so the caller decides.
    """
    today = date.today().isoformat()
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(
            db.adapt_params(
                "SELECT raw_json FROM market_today WHERE championship_id = ? AND market_date = ?"
            ),
            (championship_id, today),
        )
        rows = cursor.fetchall()

    players = [_json.loads(r[0]) for r in rows if r and r[0]]
    if not players:
        return None
    return players


def available_for_bids(max_bid: int, active_bids_total: int) -> int:
    """Pure derivation of the user's spendable budget (BR5.1).

    ``available_for_bids = max_bid - active_bids_total``. ``max_bid`` is derived
    from synced BD data; ``active_bids_total`` is the live sum of the user's
    active bids (never cached), so the result always reflects the latest
    operation without version-skew.
    """
    return max_bid - active_bids_total
