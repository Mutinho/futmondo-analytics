"""Consumer-owned data port for the ``transactions`` sync context (BR2.1, BR2.3).

``TransactionsSyncDataPort`` is a structural :class:`typing.Protocol` describing
ONLY the persistence operations the ``transactions`` orchestrator consumes. It
lives in the domain layer, imports neither ``infrastructure/`` nor any framework,
and contains no SQL (BR2.1, BR2.2). The orchestrator depends on this abstraction,
not on the concrete ``DataManagerV2`` (dependency inversion, BR2.3); the concrete
:class:`~app.services.sync.transactions.infrastructure.transactions_adapter.DataManagerTransactionsAdapter`
implements it.

The two metadata/save methods mirror the existing ``DataManagerV2`` surface
verbatim. The four remaining methods wrap raw SQL that used to run inline on
``self.dm.db`` (column ALTERs, bids UPDATE, the enrichment SELECT and UPDATE);
that SQL moves VERBATIM into the adapter — never into ``data_manager_v2.py`` and
never rewritten (BR2.2).
"""

from datetime import datetime
from typing import Callable, Dict, List, Optional, Protocol


class TransactionsSyncDataPort(Protocol):
    """Structural type of the persistence surface the transactions sync consumes."""

    def ensure_transaction_columns(self) -> None:
        """Idempotently add the market_value_at_purchase/bids_json columns.

        Wraps the historical ALTER block whose ``except Exception: pass`` guard
        tolerates the columns already existing (preserved verbatim in the
        adapter — never narrowed to a bare ``except:``).
        """
        ...

    def get_last_sync_metadata(
        self, championship_id: str, data_type: str
    ) -> Optional[Dict]:
        """Return the last sync metadata for a data type (delegates to DataManagerV2)."""
        ...

    def save_pressroom_transactions(
        self, championship_id: str, transaction_items: List[Dict]
    ) -> None:
        """Persist the filtered transaction rows (delegates to DataManagerV2)."""
        ...

    def store_bids(self, transaction_items: List[Dict]) -> None:
        """Persist the competing-bids JSON for transactions that carry bids."""
        ...

    def enrich_market_values(
        self,
        championship_id: str,
        resolve_market_value: Callable[[str, object, bool], Optional[int]],
    ) -> int:
        """Fill ``market_value_at_purchase`` for pending transactions.

        Owns the historical single-connection lifecycle (SELECT pending rows,
        then per-row UPDATE within the same cursor); the per-row value
        computation is delegated to the ``resolve_market_value`` callback, which
        performs the client fetch, throttling, caching and pure pricing. Returns
        the number of transactions enriched.
        """
        ...

    def update_sync_metadata(
        self,
        championship_id: str,
        data_type: str,
        last_sync_id: Optional[str] = None,
        last_sync_date: Optional[datetime] = None,
        last_sync_matchday: Optional[int] = None,
        records_synced: int = 0,
        sync_duration_seconds: Optional[float] = None,
        sync_status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        """Record sync metadata for a data type (delegates to DataManagerV2)."""
        ...
