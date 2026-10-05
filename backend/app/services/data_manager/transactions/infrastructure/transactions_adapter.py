"""Infrastructure adapter for ``transactions`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in the ``DataManagerV2`` transaction methods,
moved **verbatim** including the engine branch (BR1.2/FR1.4), the PostgreSQL
``execute_values`` batch path, the SQLite ``executemany`` fallback, and the
legacy broad ``except`` paths (BR3.2). Production behavior is byte-for-byte
identical (BR3.1).
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.services.data_manager.transactions.domain.ports import TransactionsDataPort

logger = logging.getLogger(__name__)


class TransactionsAdapter(TransactionsDataPort):
    """Adapt the transactions SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def save_player_transactions(self, player_id: str, owners_history: List[Dict]):
        """Legacy hook kept for compatibility with older scripts."""
        logger.debug("save_player_transactions skipped for player %s (legacy method)", player_id)
        return

    def save_pressroom_transactions(self, championship_id: str, transactions: List[Dict]):
        """Save transactions from pressroom endpoint (batch optimized for PostgreSQL).

        Each transaction has:
        - _id: transaction ID (for pagination)
        - _player: player info with _id and name
        - _buyer: buyer info with _id and name (or None if from market)
        - _seller: seller info with _id and name (or None if to market)
        - price: transaction price
        - created: transaction date
        """
        if not transactions:
            return

        MARKET_USER_ID = "market_user"
        MARKET_TEAM_ID = "market_team"

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            now = datetime.now()

            # --- Phase 1: Collect all users, teams, players that need to exist ---
            users_to_upsert = {}  # user_id -> username
            teams_to_upsert = {}  # team_id -> (user_id, team_name)
            players_to_upsert = {}  # player_id -> (name, position, teamId, team, slug, photo)

            # Always ensure market user/team exist
            users_to_upsert[MARKET_USER_ID] = "Market"
            teams_to_upsert[MARKET_TEAM_ID] = (MARKET_USER_ID, "Mercado")

            transaction_rows = []

            for txn in transactions:
                player_info = txn.get("_player", {})
                player_id = player_info.get("_id") if player_info else None
                if not player_id:
                    continue

                api_transaction_id = txn.get("_id", "")
                if not api_transaction_id:
                    continue

                # Collect player
                players_to_upsert[player_id] = (
                    player_info.get("name", "Unknown"),
                    player_info.get("position", ""),
                    player_info.get("teamId", ""),
                    player_info.get("team", ""),
                    player_info.get("slug", ""),
                    player_info.get("photo", ""),
                )

                buyer_info = txn.get("_buyer")
                seller_info = txn.get("_seller")
                price = txn.get("price", 0)
                created = txn.get("created", "")
                matchday = txn.get("matchday") or txn.get("roundNumber") or txn.get("round")

                if created:
                    try:
                        transaction_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    except Exception:
                        transaction_date = now
                else:
                    transaction_date = now

                buyer_user_id = None
                seller_user_id = None
                buyer_team_id = None
                seller_team_id = None

                if buyer_info and seller_info:
                    bid = buyer_info.get("_id")
                    bname = buyer_info.get("name", "Unknown")
                    sid = seller_info.get("_id")
                    sname = seller_info.get("name", "Unknown")
                    users_to_upsert[bid] = bname
                    users_to_upsert[sid] = sname
                    teams_to_upsert[bid] = (bid, bname)
                    teams_to_upsert[sid] = (sid, sname)
                    buyer_user_id, buyer_team_id = bid, bid
                    seller_user_id, seller_team_id = sid, sid
                elif buyer_info:
                    bid = buyer_info.get("_id")
                    bname = buyer_info.get("name", "Unknown")
                    users_to_upsert[bid] = bname
                    teams_to_upsert[bid] = (bid, bname)
                    buyer_user_id, buyer_team_id = bid, bid
                    seller_user_id, seller_team_id = MARKET_USER_ID, MARKET_TEAM_ID
                elif seller_info:
                    sid = seller_info.get("_id")
                    sname = seller_info.get("name", "Unknown")
                    users_to_upsert[sid] = sname
                    teams_to_upsert[sid] = (sid, sname)
                    seller_user_id, seller_team_id = sid, sid
                    buyer_user_id, buyer_team_id = MARKET_USER_ID, MARKET_TEAM_ID
                else:
                    continue

                transaction_rows.append(
                    (
                        championship_id,
                        api_transaction_id,
                        player_id,
                        seller_user_id,
                        buyer_user_id,
                        seller_team_id,
                        buyer_team_id,
                        int(price) if price is not None else 0,
                        transaction_date,
                        matchday,
                        now,
                    )
                )

            if not transaction_rows:
                return

            # --- Phase 2: Batch upsert users, teams, players ---
            if self.db.db_type in ["postgresql", "postgres"]:
                from psycopg2.extras import execute_values

                raw_cursor = cursor._cursor if hasattr(cursor, "_cursor") else cursor

                # Batch upsert users
                user_values = [(uid, uname, now) for uid, uname in users_to_upsert.items()]
                execute_values(
                    raw_cursor,
                    """
                    INSERT INTO users (user_id, username, last_updated)
                    VALUES %s
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        last_updated = EXCLUDED.last_updated
                """,
                    user_values,
                    page_size=100,
                )

                # Batch upsert teams
                team_values = [
                    (tid, uid, tname, 270000000, now)
                    for tid, (uid, tname) in teams_to_upsert.items()
                ]
                execute_values(
                    raw_cursor,
                    """
                    INSERT INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                    VALUES %s
                    ON CONFLICT (team_id) DO NOTHING
                """,
                    team_values,
                    page_size=100,
                )

                # Batch upsert players
                player_values = [
                    (pid, name, pos, tid, team, slug, photo, now)
                    for pid, (name, pos, tid, team, slug, photo) in players_to_upsert.items()
                ]
                execute_values(
                    raw_cursor,
                    """
                    INSERT INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES %s
                    ON CONFLICT (player_id) DO NOTHING
                """,
                    player_values,
                    page_size=100,
                )

                # --- Phase 3: Batch insert transactions ---
                execute_values(
                    raw_cursor,
                    """
                    INSERT INTO transactions 
                        (championship_id, api_transaction_id, player_id, seller_user_id, buyer_user_id,
                         seller_team_id, buyer_team_id, price, transaction_date, matchday, recorded_at)
                    VALUES %s
                    ON CONFLICT (api_transaction_id) DO NOTHING
                """,
                    transaction_rows,
                    page_size=100,
                )
            else:
                # SQLite/Turso fallback — executemany
                cursor.executemany(
                    """
                    INSERT OR REPLACE INTO users (user_id, username, last_updated) VALUES (?, ?, ?)
                """,
                    [(uid, uname, now) for uid, uname in users_to_upsert.items()],
                )

                cursor.executemany(
                    """
                    INSERT OR IGNORE INTO teams (team_id, user_id, team_name, initial_budget, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    [
                        (tid, uid, tname, 270000000, now)
                        for tid, (uid, tname) in teams_to_upsert.items()
                    ],
                )

                cursor.executemany(
                    """
                    INSERT OR IGNORE INTO players (player_id, name, role, real_team_id, real_team_name, slug, photo_url, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    [
                        (pid, name, pos, tid, team, slug, photo, now)
                        for pid, (name, pos, tid, team, slug, photo) in players_to_upsert.items()
                    ],
                )

                cursor.executemany(
                    """
                    INSERT OR IGNORE INTO transactions 
                        (championship_id, api_transaction_id, player_id, seller_user_id, buyer_user_id,
                         seller_team_id, buyer_team_id, price, transaction_date, matchday, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    transaction_rows,
                )

    def get_all_player_transactions(self, championship_id: str) -> Dict[str, List[Dict]]:
        """Get all transactions grouped by player_id"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    SELECT 
                        player_id,
                        price,
                        transaction_date,
                        buyer_user_id,
                        seller_user_id
                    FROM transactions
                    WHERE championship_id = %s OR championship_id = ''
                    ORDER BY player_id, transaction_date
                """
            else:
                sql = """
                    SELECT 
                        player_id,
                        price,
                        transaction_date,
                        buyer_user_id,
                        seller_user_id
                    FROM transactions
                    WHERE championship_id = ? OR championship_id = ''
                    ORDER BY player_id, transaction_date
                """

            cursor.execute(sql, (championship_id,))
            results = cursor.fetchall()

            transactions_by_player = {}
            for row in results:
                player_id = row[0]
                if player_id not in transactions_by_player:
                    transactions_by_player[player_id] = []

                transactions_by_player[player_id].append(
                    {
                        "price": row[1],
                        "transaction_date": row[2].isoformat() if row[2] else None,
                        "buyer_user_id": row[3],
                        "seller_user_id": row[4],
                    }
                )

            return transactions_by_player

    def get_user_transactions(self, championship_id: str, user_id: str = None) -> Dict[str, Dict]:
        """Get all transactions grouped by user_id/team_id (buyer and seller)

        Returns a dict with user_id/team_id as key and transaction summary as value.
        The key can be either a user_id (UUID) or team_id, depending on what's available.

        {
            user_id_or_team_id: {
                "total_spent": int,  # Money spent on purchases
                "total_received": int,  # Money received from sales
                "transaction_profit": int,  # total_received - total_spent
                "transaction_count": int
            }
        }
        """
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            # First, get a mapping of username -> team_id from teams table
            username_to_team_id = {}
            team_id_to_user_id = {}

            sql_teams = "SELECT team_id, user_id, team_name FROM teams"
            cursor.execute(sql_teams)
            team_rows = cursor.fetchall()
            for team_row in team_rows:
                team_id = team_row[0]
                user_id_from_team = team_row[1]
                team_name = team_row[2]

                if team_id:
                    team_id_to_user_id[team_id] = user_id_from_team or team_id
                    # Also map by team_name (username might be same as team_name)
                    if team_name:
                        username_to_team_id[team_name] = team_id

            # Also get username -> user_id mapping from users table
            username_to_user_id = {}
            sql_users = "SELECT user_id, username FROM users"
            cursor.execute(sql_users)
            user_rows = cursor.fetchall()
            for user_row in user_rows:
                user_id_from_db = user_row[0]
                username = user_row[1]
                if username:
                    username_to_user_id[username] = user_id_from_db

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    SELECT 
                        buyer_user_id,
                        seller_user_id,
                        buyer_team_id,
                        seller_team_id,
                        price,
                        transaction_date
                    FROM transactions
                    WHERE championship_id = %s
                """
                params = (championship_id,)
                if user_id:
                    sql += " AND (buyer_user_id = %s OR seller_user_id = %s OR buyer_team_id = %s OR seller_team_id = %s)"
                    params = (championship_id, user_id, user_id, user_id, user_id)
                sql += " ORDER BY transaction_date"
            else:
                sql = """
                    SELECT 
                        buyer_user_id,
                        seller_user_id,
                        buyer_team_id,
                        seller_team_id,
                        price,
                        transaction_date
                    FROM transactions
                    WHERE championship_id = ?
                """
                params = (championship_id,)
                if user_id:
                    sql += " AND (buyer_user_id = ? OR seller_user_id = ? OR buyer_team_id = ? OR seller_team_id = ?)"
                    params = (championship_id, user_id, user_id, user_id, user_id)
                sql += " ORDER BY transaction_date"

            cursor.execute(sql, params)
            results = cursor.fetchall()

            # Helper to get team_id from user_id (UUID)
            def get_team_id_from_user_id(uuid_str: str) -> str:
                if not uuid_str:
                    return None

                # First, check if uuid_str is already a team_id
                if uuid_str in team_id_to_user_id:
                    return uuid_str

                # Try to find user by UUID and get their team_id
                # Reverse lookup: find team_id where user_id matches
                for tid, uid in team_id_to_user_id.items():
                    if uid == uuid_str:
                        return tid

                # Try to find by username (if user_id is actually a username)
                if uuid_str in username_to_team_id:
                    return username_to_team_id[uuid_str]

                # Also check username_to_user_id and then map to team_id
                if uuid_str in username_to_user_id:
                    user_id_from_username = username_to_user_id[uuid_str]
                    # Now find team_id for this user_id
                    for tid, uid in team_id_to_user_id.items():
                        if uid == user_id_from_username:
                            return tid

                # If not found, return the UUID itself (will be used as fallback)
                return uuid_str

            user_transactions = {}

            for row in results:
                buyer_user_id = row[0]
                seller_user_id = row[1]
                buyer_team_id = row[2]
                seller_team_id = row[3]
                price = row[4] if row[4] else 0

                # Map user_ids to team_ids for better matching
                if not buyer_team_id:
                    buyer_team_id = (
                        get_team_id_from_user_id(buyer_user_id) if buyer_user_id else None
                    )
                if not seller_team_id:
                    seller_team_id = (
                        get_team_id_from_user_id(seller_user_id) if seller_user_id else None
                    )

                # Use team_id as key if available and different from user_id, otherwise use user_id
                # This ensures all transactions for the same user are grouped together
                if buyer_team_id and buyer_team_id != buyer_user_id:
                    buyer_key = buyer_team_id
                else:
                    buyer_key = buyer_user_id

                if seller_team_id and seller_team_id != seller_user_id:
                    seller_key = seller_team_id
                else:
                    seller_key = seller_user_id

                # Skip market transactions (seller is "Market")
                if seller_user_id and seller_user_id.lower() != "market" and seller_key:
                    # This is a sale - seller receives money
                    if seller_key not in user_transactions:
                        user_transactions[seller_key] = {
                            "total_spent": 0,
                            "total_received": 0,
                            "transaction_count": 0,
                        }
                    user_transactions[seller_key]["total_received"] += price
                    user_transactions[seller_key]["transaction_count"] += 1

                # Buyer spends money
                if buyer_key:
                    if buyer_key not in user_transactions:
                        user_transactions[buyer_key] = {
                            "total_spent": 0,
                            "total_received": 0,
                            "transaction_count": 0,
                        }
                    # Buyer always spends money (whether from market or another user)
                    user_transactions[buyer_key]["total_spent"] += price
                    user_transactions[buyer_key]["transaction_count"] += 1

            # Calculate profit for each user
            for user_key, data in user_transactions.items():
                data["transaction_profit"] = data["total_received"] - data["total_spent"]

            return user_transactions

    def get_transactions_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        """Return raw transactions optionally filtered by recent days"""
        params: List[Any] = [championship_id]
        condition = ""
        if days:
            condition = " AND transaction_date >= ?"
            params.append(datetime.now() - timedelta(days=days))

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f"""
                SELECT api_transaction_id, player_id, seller_user_id, buyer_user_id,
                       seller_team_id, buyer_team_id, price, transaction_date, matchday
                FROM transactions
                WHERE championship_id = ?{condition}
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        items = []
        for row in rows:
            items.append(
                {
                    "transaction_id": row[0],
                    "player_id": row[1],
                    "seller_user_id": row[2],
                    "buyer_user_id": row[3],
                    "seller_team_id": row[4],
                    "buyer_team_id": row[5],
                    "price": row[6],
                    "transaction_date": row[7],
                    "matchday": row[8],
                }
            )
        return items
