"""Infrastructure adapter implementing :class:`TransactionsSyncDataPort` (BR2.2).

This is the ONLY module in the ``transactions`` sync context that touches
``DataManagerV2`` or its raw ``db`` connection. It wraps the current facade (this
wave does not decompose ``data_manager`` — that is a later wave), so the
production result stays identical (BR1.2, BR2.2). The raw SQL that used to run
inline on ``self.dm.db`` — the idempotent column ALTERs, the competing-bids
UPDATE, the enrichment SELECT and per-row UPDATE — is moved here VERBATIM: not
rewritten, not moved into ``data_manager_v2.py``.

The ``except Exception`` / ``pass`` guard on the column-ALTER block is preserved
EXACTLY (R-03): it tolerates the columns already existing and is NOT narrowed to
a bare ``except:`` (that would reintroduce E722 and swallow more than intended).

``enrich_market_values`` keeps the historical single-connection lifecycle: one
connection/cursor is held open across the whole enrichment loop, exactly as the
former inline ``_enrich_market_values`` did. The orchestrator supplies a
``resolve_market_value`` callback that performs the client fetch, the
0.5s/5s throttling, the per-player caching, and the pure pricing — so this
adapter owns only the SQL and the orchestrator owns only the orchestration.
"""

import json as _json
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional

from app.services.data_manager_v2 import DataManagerV2
from app.services.sync.transactions.domain.ports import TransactionsSyncDataPort

logger = logging.getLogger(__name__)


class DataManagerTransactionsAdapter(TransactionsSyncDataPort):
    """Adapt ``DataManagerV2`` (and its raw ``db``) to ``TransactionsSyncDataPort``."""

    def __init__(self, dm: Optional[DataManagerV2] = None) -> None:
        """Create the adapter.

        Args:
            dm: The data manager to delegate persistence to. Defaults to a fresh
                ``DataManagerV2(skip_init=True)`` to preserve the historical
                behavior (the facade never re-inits the schema per instance).
        """
        self.dm = dm if dm is not None else DataManagerV2(skip_init=True)

    def ensure_transaction_columns(self) -> None:
        # Raw SQL moved VERBATIM from DataSyncService.sync_transactions (BR2.2).
        # The ``except Exception: pass`` guard is preserved EXACTLY (R-03): the
        # ALTERs are idempotent and already-existing columns are the expected,
        # tolerated outcome; it is NOT narrowed to a bare ``except:`` (E722).
        try:
            db = self.dm.db
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                if db.db_type in ["postgresql", "postgres"]:
                    raw = cursor._cursor if hasattr(cursor, "_cursor") else cursor
                    raw.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS market_value_at_purchase INTEGER")
                    raw.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS bids_json TEXT")
                else:
                    cursor.execute("ALTER TABLE transactions ADD COLUMN market_value_at_purchase INTEGER")
                    cursor.execute("ALTER TABLE transactions ADD COLUMN bids_json TEXT")
        except Exception:
            pass  # Columns already exist

    def get_last_sync_metadata(
        self, championship_id: str, data_type: str
    ) -> Optional[Dict]:
        # Delegated verbatim to DataManagerV2 (BR2.2).
        return self.dm.get_last_sync_metadata(championship_id, data_type)

    def save_pressroom_transactions(
        self, championship_id: str, transaction_items: List[Dict]
    ) -> None:
        # Delegated verbatim to DataManagerV2 (BR2.2).
        self.dm.save_pressroom_transactions(championship_id, transaction_items)

    def store_bids(self, transaction_items: list) -> None:
        # Raw SQL moved VERBATIM from DataSyncService._store_bids (BR2.2).
        db = self.dm.db
        updates = []
        for item in transaction_items:
            bids = item.get("bids", [])
            api_id = item.get("_id", "")
            if bids and api_id:
                bids_data = [{"name": b.get("u", {}).get("name", "?"), "bid": b.get("bid", 0)} for b in bids]
                updates.append((_json.dumps(bids_data), api_id))

        if not updates:
            return

        try:
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                sql = "UPDATE transactions SET bids_json = ? WHERE api_transaction_id = ?"
                sql = db.adapt_params(sql)
                for bids_json, api_id in updates:
                    cursor.execute(sql, (bids_json, api_id))
        except Exception as e:
            logger.debug(f"Could not store bids: {e}")

    def enrich_market_values(
        self,
        championship_id: str,
        resolve_market_value: Callable[[str, object, bool], Optional[int]],
    ) -> int:
        """Fill market_value_at_purchase using a resolver callback (BR2.2).

        Owns the historical single-connection lifecycle: one connection/cursor is
        held open across the whole loop, exactly as the former inline
        ``_enrich_market_values`` did. The raw SELECT and per-row UPDATE are
        preserved VERBATIM; the per-row market-value computation (client fetch,
        throttle, caching, pure pricing) is delegated to ``resolve_market_value``
        so no orchestration leaks into the adapter.

        Args:
            championship_id: The championship whose transactions are enriched.
            resolve_market_value: Callback invoked as
                ``resolve_market_value(player_id, txn_date, is_market_purchase)``
                returning the market value, or None to skip the row.

        Returns:
            Number of transactions enriched.
        """
        db = self.dm.db
        enriched = 0

        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            # Find transactions missing market value
            sql = """
                SELECT transaction_id, player_id, transaction_date, buyer_team_id 
                FROM transactions 
                WHERE championship_id = ? 
                AND market_value_at_purchase IS NULL
                ORDER BY transaction_date DESC
            """
            sql = db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            rows = cursor.fetchall()

            if not rows:
                return 0

            logger.info(f"Enriching {len(rows)} transactions with market value...")

            for row in rows:
                txn_id, player_id, txn_date, buyer_team_id = row[0], row[1], row[2], row[3]

                # Purchases from market use previous day's value; sales use same day
                is_market_purchase = buyer_team_id != "market_team"

                try:
                    market_value = resolve_market_value(
                        player_id, txn_date, is_market_purchase
                    )
                    if market_value is None:
                        continue

                    # Update transaction
                    update_sql = "UPDATE transactions SET market_value_at_purchase = ? WHERE transaction_id = ?"
                    update_sql = db.adapt_params(update_sql)
                    cursor.execute(update_sql, (market_value, txn_id))
                    enriched += 1

                except Exception as e:
                    logger.debug(f"Could not enrich transaction {txn_id}: {e}")
                    continue

        return enriched

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
        # Delegated verbatim to DataManagerV2 (BR2.2). The former inline calls
        # passed every argument by keyword; that convention is preserved here.
        # Only the keyword arguments those calls actually supplied are forwarded;
        # the rest keep DataManagerV2's own defaults, so the persisted row is
        # unchanged.
        kwargs: Dict = {
            "championship_id": championship_id,
            "data_type": data_type,
        }
        if last_sync_id is not None:
            kwargs["last_sync_id"] = last_sync_id
        if last_sync_date is not None:
            kwargs["last_sync_date"] = last_sync_date
        if last_sync_matchday is not None:
            kwargs["last_sync_matchday"] = last_sync_matchday
        kwargs["records_synced"] = records_synced
        if sync_duration_seconds is not None:
            kwargs["sync_duration_seconds"] = sync_duration_seconds
        kwargs["sync_status"] = sync_status
        if error_message is not None:
            kwargs["error_message"] = error_message
        self.dm.update_sync_metadata(**kwargs)
