"""Infrastructure adapter for ``punishments-bonuses`` — the only module with SQL (BR1.3).

Hosts the raw SQL formerly inline in the ``DataManagerV2`` punishment/bonus
methods, moved **verbatim** including the engine branch (BR1.2/FR1.4) and the
legacy broad ``except`` / retry paths (BR3.2). Cross-responsibility helpers
(``get_user_id_by_name``, ``ensure_championship_exists``) are reached live via
``self.dm`` so production behavior is byte-for-byte identical (BR3.1).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_manager.punishments_bonuses.domain.ports import (
    PunishmentsBonusesDataPort,
)

logger = logging.getLogger(__name__)


class PunishmentsBonusesAdapter(PunishmentsBonusesDataPort):
    """Adapt the punishments/bonuses SQL (verbatim) to the port."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        return self.dm.db

    def save_punishments_bonuses(self, championship_id: str, news_items: List[Dict]):
        """Save punishments and bonuses from locker news

        Each news item has:
        - _id: news ID (for pagination)
        - styp: "punish" or "bonus"
        - data: dict with "quantity", "to" (user name), "admin"
        - created: date
        """
        if not news_items:
            return

        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                with self.db.get_connection() as conn:
                    cursor = self.db.get_cursor(conn)

                    # Ensure championship exists in the same transaction
                    self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

                    for news_item in news_items:
                        news_id = news_item.get("_id")
                        styp = news_item.get("styp")
                        data = news_item.get("data", {})
                        created = news_item.get("created", "")

                        # Only process punish and bonus types
                        if styp not in ["punish", "bonus"]:
                            continue

                        if not news_id or not data:
                            continue

                        quantity = data.get("quantity", 0)
                        user_name = data.get("to", "")
                        admin_name = data.get("admin", "")

                        if not user_name or quantity == 0:
                            continue

                        # Get user_id and team_id by name
                        user_info = self.dm.get_user_id_by_name(user_name)
                        if not user_info:
                            logger.warning(f"Could not find user/team for name: {user_name}")
                            continue

                        user_id = user_info.get("user_id")
                        team_id = user_info.get("team_id")

                        # Parse date
                        try:
                            if created:
                                created_date = datetime.fromisoformat(
                                    created.replace("Z", "+00:00")
                                )
                            else:
                                created_date = datetime.now()
                        except:
                            created_date = datetime.now()

                        # Insert or update punishment/bonus
                        if self.db.db_type in ["postgresql", "postgres"]:
                            sql = """
                                INSERT INTO punishments_bonuses 
                                (championship_id, news_id, user_id, team_id, user_name, type, amount, admin_name, created_date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (news_id) DO NOTHING
                            """
                        else:
                            sql = """
                                INSERT OR IGNORE INTO punishments_bonuses 
                                (championship_id, news_id, user_id, team_id, user_name, type, amount, admin_name, created_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """
                            sql = self.db.adapt_params(sql)

                        cursor.execute(
                            sql,
                            (
                                championship_id,
                                news_id,
                                user_id,
                                team_id,
                                user_name,
                                styp,
                                quantity,
                                admin_name,
                                created_date,
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
                    logger.warning(f"Failed to save punishments/bonuses: {e}")
                    raise

    def get_user_punishments_bonuses(self, championship_id: str) -> Dict[str, Dict]:
        """Get all punishments and bonuses grouped by user_id/team_id"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    SELECT 
                        COALESCE(team_id, user_id) as user_key,
                        user_id,
                        team_id,
                        MAX(user_name) as user_name,
                        type,
                        SUM(amount) as total_amount,
                        COUNT(*) as count
                    FROM punishments_bonuses
                    WHERE championship_id = %s
                    GROUP BY COALESCE(team_id, user_id), user_id, team_id, type
                """
                params = (championship_id,)
            else:
                sql = """
                    SELECT 
                        COALESCE(team_id, user_id) as user_key,
                        user_id,
                        team_id,
                        MAX(user_name) as user_name,
                        type,
                        SUM(amount) as total_amount,
                        COUNT(*) as count
                    FROM punishments_bonuses
                    WHERE championship_id = ?
                    GROUP BY COALESCE(team_id, user_id), user_id, team_id, type
                """
                sql = self.db.adapt_params(sql)
                params = (championship_id,)

            cursor.execute(sql, params)
            results = cursor.fetchall()

            user_adjustments: Dict[str, Dict] = {}

            for row in results:
                user_key = row[0]
                row_user_id = row[1]
                row_team_id = row[2]
                row_user_name = row[3]
                adjustment_type = row[4]
                total_amount = row[5] if row[5] else 0
                count = row[6] if row[6] else 0

                key = row_team_id if row_team_id else row_user_id
                if key not in user_adjustments:
                    user_adjustments[key] = {
                        "total_punishments": 0,
                        "total_bonuses": 0,
                        "net_adjustment": 0,
                        "punishment_count": 0,
                        "bonus_count": 0,
                        "user_id": row_user_id,
                        "team_id": row_team_id,
                        "user_name": row_user_name,
                    }

                if adjustment_type == "punish":
                    user_adjustments[key]["total_punishments"] += total_amount
                    user_adjustments[key]["punishment_count"] += count
                elif adjustment_type == "bonus":
                    user_adjustments[key]["total_bonuses"] += total_amount
                    user_adjustments[key]["bonus_count"] += count

            for key, data in user_adjustments.items():
                data["net_adjustment"] = data["total_bonuses"] - data["total_punishments"]

            return user_adjustments
