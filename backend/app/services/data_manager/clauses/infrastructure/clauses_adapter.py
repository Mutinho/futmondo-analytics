"""Infrastructure adapter for ``clauses`` — the only module with SQL (BR1.3).

Implements :class:`ClausesDataPort` by hosting the raw SQL and HTML parsing
formerly inline in the ``DataManagerV2`` clause methods, moved **verbatim**
including the ``if db_type in ["postgresql", "postgres"]: ... else: (SQLite)``
engine branch (BR1.2/FR1.4) and the legacy broad/bare ``except`` and
``return None`` paths (BR3.2). Cross-responsibility helpers still owned by the
facade (``parse_clause_text``, ``get_user_id_by_name``,
``ensure_championship_exists``) are reached live through ``self.dm`` so the
production result is byte-for-byte identical (BR3.1); no nested delegation is
introduced.

Constructor injection with a default (the ``analytics`` pattern): the adapter
defaults to a fresh ``DataManagerV2(skip_init=True)`` so production behavior is
unchanged; tests drive it with the in-memory fake via an injected facade.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.services.data_manager.clauses.domain.ports import ClausesDataPort

logger = logging.getLogger(__name__)


class ClausesAdapter(ClausesDataPort):
    """Adapt the clauses SQL/parsing (verbatim) to :class:`ClausesDataPort`."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        # Read the connection live from the facade so a test that reassigns
        # ``dm.db`` (the in-memory fake) is honored.
        return self.dm.db

    def parse_clause_text(self, text: str) -> Optional[Dict[str, str]]:
        """Parse clause text to extract payer, receiver, amount, and player name

        Example: "El equipo <strong>Santi Sesma</strong> ha pagado <strong>21.377.932</strong> propiedad de <strong>Patxo Torre</strong> como clausula de <strong>Virgili</strong>"

        Returns:
            Dict with 'payer_name', 'receiver_name', 'amount', 'player_name' or None if parsing fails
        """
        if not text:
            return None

        # Pattern: "El equipo <strong>[PAYER]</strong> ha pagado <strong>[AMOUNT]</strong> propiedad de <strong>[RECEIVER]</strong> como clausula de <strong>[PLAYER]</strong>"
        # Try with HTML tags first (more reliable)
        pattern_with_html = r"El equipo\s+<strong>([^<]+)</strong>\s+ha pagado\s+<strong>([\d.]+)</strong>\s+propiedad de\s+<strong>([^<]+)</strong>\s+como clausula de\s+<strong>([^<]+)</strong>"
        match = re.search(pattern_with_html, text, re.IGNORECASE)

        if not match:
            # Fallback: pattern without HTML tags
            text_clean = re.sub(r"<[^>]+>", "", text)
            pattern = r"El equipo\s+([^h]+?)\s+ha pagado\s+([\d.]+)\s+propiedad de\s+([^c]+?)\s+como clausula de\s+(.+)"
            match = re.search(pattern, text_clean, re.IGNORECASE)

        if match:
            payer_name = match.group(1).strip()
            amount_str = match.group(2).strip().replace(".", "")  # Remove dots from number
            receiver_name = match.group(3).strip()
            player_name = match.group(4).strip()

            try:
                amount = int(amount_str)
            except ValueError:
                logger.warning(f"Could not parse amount: {amount_str}")
                return None

            return {
                "payer_name": payer_name,
                "receiver_name": receiver_name,
                "amount": amount,
                "player_name": player_name,
            }

        return None

    def save_clauses(self, championship_id: str, news_items: List[Dict]):
        """Save clauses from locker news

        Each news item has:
        - _id: news ID (for pagination)
        - styp: "clause"
        - txt: HTML text with clause information
        - created: date
        """
        if not news_items:
            return

        # First, parse all clauses and get/create users (outside transaction to avoid locks)
        parsed_clauses = []
        for news_item in news_items:
            news_id = news_item.get("_id")
            styp = news_item.get("styp")
            txt = news_item.get("txt", "")
            created = news_item.get("created", "")

            # Only process clause types
            if styp != "clause":
                continue

            if not news_id or not txt:
                continue

            # Parse clause text
            clause_data = self.dm.parse_clause_text(txt)
            if not clause_data:
                logger.warning(f"Could not parse clause text: {txt[:100]}")
                continue

            payer_name = clause_data.get("payer_name")
            receiver_name = clause_data.get("receiver_name")
            amount = clause_data.get("amount")
            player_name = clause_data.get("player_name")

            # Get user_id and team_id for payer and receiver (will create if not found)
            # Use retry logic for user creation
            payer_info = None
            receiver_info = None

            max_user_retries = 3
            for user_attempt in range(max_user_retries):
                try:
                    payer_info = self.dm.get_user_id_by_name(payer_name)
                    receiver_info = self.dm.get_user_id_by_name(receiver_name)
                    break
                except Exception as e:
                    if "locked" in str(e).lower() and user_attempt < max_user_retries - 1:
                        import time

                        time.sleep(0.1 * (user_attempt + 1))
                        continue
                    else:
                        logger.warning(
                            f"Error getting user info for {payer_name}/{receiver_name}: {e}"
                        )
                        break

            if not payer_info:
                logger.warning(f"Could not find or create user/team for payer: {payer_name}")
                continue

            if not receiver_info:
                logger.warning(f"Could not find or create user/team for receiver: {receiver_name}")
                continue

            payer_user_id = payer_info.get("user_id")
            payer_team_id = payer_info.get("team_id")
            receiver_user_id = receiver_info.get("user_id")
            receiver_team_id = receiver_info.get("team_id")

            # Parse date
            try:
                if created:
                    created_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                else:
                    created_date = datetime.now()
            except:
                created_date = datetime.now()

            parsed_clauses.append(
                {
                    "news_id": news_id,
                    "payer_user_id": payer_user_id,
                    "payer_team_id": payer_team_id,
                    "payer_name": payer_name,
                    "receiver_user_id": receiver_user_id,
                    "receiver_team_id": receiver_team_id,
                    "receiver_name": receiver_name,
                    "player_name": player_name,
                    "amount": amount,
                    "created_date": created_date,
                }
            )

        # Now save all parsed clauses in a single transaction
        if not parsed_clauses:
            return

        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                with self.db.get_connection() as conn:
                    cursor = self.db.get_cursor(conn)

                    # Ensure championship exists in the same transaction
                    self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

                    for clause_data in parsed_clauses:
                        # Insert or update clause
                        if self.db.db_type in ["postgresql", "postgres"]:
                            sql = """
                                INSERT INTO clauses 
                                (championship_id, news_id, payer_user_id, payer_team_id, payer_name, 
                                 receiver_user_id, receiver_team_id, receiver_name, player_name, amount, created_date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (news_id) DO NOTHING
                            """
                        else:
                            sql = """
                                INSERT OR IGNORE INTO clauses 
                                (championship_id, news_id, payer_user_id, payer_team_id, payer_name, 
                                 receiver_user_id, receiver_team_id, receiver_name, player_name, amount, created_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """
                            sql = self.db.adapt_params(sql)

                        cursor.execute(
                            sql,
                            (
                                championship_id,
                                clause_data["news_id"],
                                clause_data["payer_user_id"],
                                clause_data["payer_team_id"],
                                clause_data["payer_name"],
                                clause_data["receiver_user_id"],
                                clause_data["receiver_team_id"],
                                clause_data["receiver_name"],
                                clause_data["player_name"],
                                clause_data["amount"],
                                clause_data["created_date"],
                            ),
                        )

                    # Commit all at once
                    conn.commit()
                    return  # Success, exit retry loop

            except Exception as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    import time

                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.warning(f"Failed to save clauses: {e}")
                    raise

    def get_user_clauses_stats(self, championship_id: str) -> Dict[str, Dict]:
        """Get clause statistics grouped by user_id/team_id

        Returns:
            Dict with user_id/team_id as key and stats as value:
            {
                user_id_or_team_id: {
                    "clauses_paid": int,  # Number of clauses paid
                    "clauses_received": int,  # Number of clauses received
                    "total_paid": int,  # Total amount paid
                    "total_received": int  # Total amount received
                }
            }
        """
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    SELECT 
                        COALESCE(payer_team_id, payer_user_id) as payer_key,
                        COALESCE(receiver_team_id, receiver_user_id) as receiver_key,
                        payer_team_id,
                        payer_user_id,
                        receiver_team_id,
                        receiver_user_id,
                        COUNT(*) as count,
                        SUM(amount) as total
                    FROM clauses
                    WHERE championship_id = %s
                    GROUP BY COALESCE(payer_team_id, payer_user_id), COALESCE(receiver_team_id, receiver_user_id),
                             payer_team_id, payer_user_id, receiver_team_id, receiver_user_id
                """
            else:
                sql = """
                    SELECT 
                        COALESCE(payer_team_id, payer_user_id) as payer_key,
                        COALESCE(receiver_team_id, receiver_user_id) as receiver_key,
                        payer_team_id,
                        payer_user_id,
                        receiver_team_id,
                        receiver_user_id,
                        COUNT(*) as count,
                        SUM(amount) as total
                    FROM clauses
                    WHERE championship_id = ?
                    GROUP BY COALESCE(payer_team_id, payer_user_id), COALESCE(receiver_team_id, receiver_user_id),
                             payer_team_id, payer_user_id, receiver_team_id, receiver_user_id
                """
                sql = self.db.adapt_params(sql)

            cursor.execute(sql, (championship_id,))
            results = cursor.fetchall()

            user_clauses = {}

            for row in results:
                payer_key = row[0]
                receiver_key = row[1]
                payer_team_id = row[2]
                payer_user_id = row[3]
                receiver_team_id = row[4]
                receiver_user_id = row[5]
                count = row[6] if row[6] else 0
                total = row[7] if row[7] else 0

                # Use team_id as key if available, otherwise user_id
                payer_id = payer_team_id if payer_team_id else payer_user_id
                receiver_id = receiver_team_id if receiver_team_id else receiver_user_id

                # Initialize payer stats
                if payer_id not in user_clauses:
                    user_clauses[payer_id] = {
                        "clauses_paid": 0,
                        "clauses_received": 0,
                        "total_paid": 0,
                        "total_received": 0,
                    }

                # Initialize receiver stats
                if receiver_id not in user_clauses:
                    user_clauses[receiver_id] = {
                        "clauses_paid": 0,
                        "clauses_received": 0,
                        "total_paid": 0,
                        "total_received": 0,
                    }

                # Add to payer stats
                user_clauses[payer_id]["clauses_paid"] += count
                user_clauses[payer_id]["total_paid"] += total

                # Add to receiver stats
                user_clauses[receiver_id]["clauses_received"] += count
                user_clauses[receiver_id]["total_received"] += total

            return user_clauses

    def get_clauses_raw(self, championship_id: str, days: Optional[int] = None) -> List[Dict]:
        """Return raw clause payments"""
        params: List[Any] = [championship_id]
        condition = ""
        if days:
            condition = " AND created_date >= ?"
            params.append(datetime.now() - timedelta(days=days))

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)
            sql = f"""
                SELECT payer_user_id, payer_team_id, receiver_user_id, receiver_team_id,
                       amount, created_date, player_name
                FROM clauses
                WHERE championship_id = ?{condition}
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        clauses = []
        for row in rows:
            clauses.append(
                {
                    "payer_user_id": row[0],
                    "payer_team_id": row[1],
                    "receiver_user_id": row[2],
                    "receiver_team_id": row[3],
                    "amount": row[4],
                    "created_date": row[5],
                    "player_name": row[6],
                }
            )
        return clauses

    def get_clausulable_player_stats(self, championship_id: str) -> List[Dict]:
        """Retrieve stored clause metrics for clausulable player ranking."""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            sql = """
                SELECT 
                    pcs.player_id,
                    COALESCE(p.name, 'Unknown') AS player_name,
                    pcs.owner_team_id,
                    pcs.owner_team_name,
                    pcs.owner_user_id,
                    pcs.clause_price,
                    pcs.suggested_clause,
                    pcs.average_last_five,
                    pcs.average_overall,
                    pcs.clause_date
                FROM player_championship_stats pcs
                LEFT JOIN players p ON p.player_id = pcs.player_id
                WHERE pcs.championship_id = ?
            """
            sql = self.db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            rows = cursor.fetchall()

        results: List[Dict] = []
        for row in rows:
            results.append(
                {
                    "player_id": row[0],
                    "player_name": row[1],
                    "owner_team_id": row[2],
                    "owner_team_name": row[3],
                    "owner_user_id": row[4],
                    "clause_price": row[5],
                    "suggested_clause": row[6],
                    "average_last_five": row[7],
                    "average_overall": row[8],
                    "clause_date": row[9],
                }
            )
        return results
