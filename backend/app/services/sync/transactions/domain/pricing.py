"""Pure price-matching helper for the ``transactions`` sync context.

``find_price_at_date`` is the pure function extracted verbatim from the former
private ``DataSyncService._find_price_at_date``. It performs NO I/O (no network,
no DB, no logging) — it only inspects an in-memory price-history list and returns
the social price at or near a transaction date. Keeping it pure makes it
directly unit-testable and keeps the orchestrator free of date arithmetic
(single responsibility).

The matching logic is byte-for-byte the historical one (FR5): same date
normalization, same ``diff < 0 or diff > 3`` window, same "prefer ideal_diff then
closest" tie-break, same ``social`` → ``classic`` → ``0`` fallback.
"""

from typing import Optional


def find_price_at_date(
    prices: list, txn_date, prefer_previous_day: bool = False
) -> Optional[int]:
    """Find the social price at or near a transaction date.

    Args:
        prices: List of {date, social, classic} dicts from fullprofile.
        txn_date: Transaction date (datetime or string).
        prefer_previous_day: If True, prefer the day before (for market
            purchases). If False, prefer same day (for sales).

    Returns:
        The social price value, or None if not found.
    """
    from datetime import datetime as dt

    # Normalize txn_date to date
    if isinstance(txn_date, str):
        try:
            txn_dt = dt.fromisoformat(txn_date.replace("Z", "+00:00")).date()
        except Exception:
            return None
    elif hasattr(txn_date, "date"):
        txn_dt = txn_date.date()
    else:
        txn_dt = txn_date

    best_price = None
    best_diff = None
    ideal_diff = 1 if prefer_previous_day else 0

    for entry in prices:
        try:
            entry_date_str = entry.get("date", "")
            entry_dt = dt.fromisoformat(entry_date_str.replace("Z", "+00:00")).date()
            diff = (txn_dt - entry_dt).days  # Positive = entry is before txn

            # Only consider entries from before or same day (not future)
            if diff < 0 or diff > 3:
                continue

            # Prefer ideal_diff, then closest
            if best_diff is None:
                best_diff = diff
                best_price = entry.get("social", entry.get("classic", 0))
            elif abs(diff - ideal_diff) < abs(best_diff - ideal_diff):
                best_diff = diff
                best_price = entry.get("social", entry.get("classic", 0))
        except Exception:
            continue

    return best_price
