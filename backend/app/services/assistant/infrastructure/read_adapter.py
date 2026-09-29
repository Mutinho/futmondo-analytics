"""Infrastructure read adapter implementing :class:`AssistantReadPort`.

This is the ONLY place in the assistant context with raw read SQL (BR2.2,
BR3.2). Every ``SELECT`` here is moved verbatim from the former inline reads in
``assistant_service.py`` (the ``_factual_*`` handlers, ``_get_user_identity``,
and the ``_ctx_*`` context builders), so the returned rows are identical and the
characterization tests stay green.

The DB boundary is injected via ``db_factory`` (defaulting to the global
``db_connection.get_db`` singleton), exactly like the analytics adapter, so
production behavior is unchanged and tests run against the in-memory SQLite fake.
All statements use ``db.adapt_params`` + ``?`` placeholders.
"""

import json as json_mod
import logging
from datetime import date
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DataManagerAssistantReadAdapter:
    """Adapt the raw assistant reads/writes to :class:`AssistantReadPort`."""

    def __init__(self, db_factory=None) -> None:
        self._db_factory = db_factory

    def _get_db(self):
        if self._db_factory is not None:
            return self._db_factory()
        from app.services.db_connection import get_db

        return get_db()

    # --- User identity ----------------------------------------------------
    def get_user_identity(self, user_id: str, championship_id: str) -> Dict:
        """Load the user's identity dict. Verbatim from ``_get_user_identity``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            cursor.execute(
                db.adapt_params("SELECT display_name FROM app_users WHERE id = ?"),
                (user_id,),
            )
            user_row = cursor.fetchone()
            user_name = user_row[0] if user_row else "Usuario"

            cursor.execute(
                db.adapt_params(
                    "SELECT name, futmondo_team_id, is_pro FROM user_championships "
                    "WHERE user_id = ? AND championship_id = ?"
                ),
                (user_id, championship_id),
            )
            champ_row = cursor.fetchone()

            if champ_row:
                championship_name = champ_row[0] or "Campeonato"
                team_id = champ_row[1] or ""
                is_pro = bool(champ_row[2]) if champ_row[2] is not None else False
            else:
                championship_name = "Campeonato"
                team_id = ""
                is_pro = False

            team_name = "Desconocido"
            if team_id:
                cursor.execute(
                    db.adapt_params("SELECT team_name FROM teams WHERE team_id = ?"),
                    (team_id,),
                )
                team_row = cursor.fetchone()
                if team_row:
                    team_name = team_row[0]

        return {
            "user_name": user_name,
            "team_name": team_name,
            "team_id": team_id,
            "championship_name": championship_name,
            "is_pro": is_pro,
        }

    # --- Factual reads ----------------------------------------------------
    def get_balance_data(self, user_id: str, championship_id: str, team_id: str) -> Dict:
        """Load the raw figures behind the balance answer. Verbatim from ``_factual_balance``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            cursor.execute(
                db.adapt_params(
                    "SELECT COALESCE(SUM(price), 0) FROM transactions "
                    "WHERE championship_id = ? AND buyer_team_id = ?"
                ),
                (championship_id, team_id),
            )
            total_spent = cursor.fetchone()[0] or 0

            cursor.execute(
                db.adapt_params(
                    "SELECT COALESCE(SUM(price), 0) FROM transactions "
                    "WHERE championship_id = ? AND seller_team_id = ?"
                ),
                (championship_id, team_id),
            )
            total_income = cursor.fetchone()[0] or 0

            cursor.execute(
                db.adapt_params(
                    "SELECT initial_budget FROM user_championships "
                    "WHERE user_id = ? AND championship_id = ?"
                ),
                (user_id, championship_id),
            )
            config_row = cursor.fetchone()
            initial_budget = config_row[0] if config_row else 200_000_000

            cursor.execute(
                db.adapt_params(
                    "SELECT COALESCE(SUM(ranking_prize + mvp_prize + COALESCE(points_prize, 0) "
                    "+ COALESCE(dream_team_prize, 0)), 0) FROM team_prizes "
                    "WHERE championship_id = ? AND team_id = ?"
                ),
                (championship_id, team_id),
            )
            prizes = cursor.fetchone()[0] or 0

            cursor.execute(
                db.adapt_params(
                    "SELECT COALESCE(SUM(p.value), 0) FROM player_championship_stats pcs "
                    "JOIN players p ON pcs.player_id = p.player_id "
                    "WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?"
                ),
                (championship_id, team_id),
            )
            team_value = cursor.fetchone()[0] or 0

        return {
            "total_spent": total_spent,
            "total_income": total_income,
            "initial_budget": initial_budget,
            "prizes": prizes,
            "team_value": team_value,
        }

    def get_roster_rows(self, championship_id: str, team_id: str) -> List[tuple]:
        """Load roster rows. Verbatim from ``_factual_roster`` (7-column read)."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                db.adapt_params(
                    """
                SELECT p.player_id, p.name, p.role, p.value, pcs.average_overall, pcs.average_last_five,
                       sc.rating
                FROM player_championship_stats pcs
                JOIN players p ON pcs.player_id = p.player_id
                LEFT JOIN sofascore_cache sc ON LOWER(p.name) = LOWER(sc.player_name)
                WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?
                ORDER BY p.value DESC
            """
                ),
                (championship_id, team_id),
            )
            return cursor.fetchall()

    def get_standings(self, championship_id: str) -> Tuple[Optional[int], List[tuple]]:
        """Load standings. Verbatim from ``_factual_standings`` / ``_ctx_standings``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                db.adapt_params(
                    "SELECT MAX(matchday) FROM team_standings WHERE championship_id = ?"
                ),
                (championship_id,),
            )
            max_md_row = cursor.fetchone()
            if not max_md_row or not max_md_row[0]:
                return None, []
            max_matchday = max_md_row[0]

            cursor.execute(
                db.adapt_params(
                    """
                SELECT t.team_name, ts.points, ts.position
                FROM team_standings ts
                JOIN teams t ON ts.team_id = t.team_id
                WHERE ts.championship_id = ? AND ts.matchday = ?
                ORDER BY ts.position ASC
            """
                ),
                (championship_id, max_matchday),
            )
            return max_matchday, cursor.fetchall()

    def get_team_value(self, championship_id: str, team_id: str) -> Tuple[int, int]:
        """Load ``(total_value, player_count)``. Verbatim from ``_factual_team_value``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                db.adapt_params(
                    "SELECT COALESCE(SUM(p.value), 0), COUNT(*) FROM player_championship_stats pcs "
                    "JOIN players p ON pcs.player_id = p.player_id "
                    "WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?"
                ),
                (championship_id, team_id),
            )
            row = cursor.fetchone()
            return (row[0] or 0), (row[1] or 0)

    # --- Context reads (populated in Step 10) -----------------------------
    def get_roster_rows_ctx(self, championship_id: str, team_id: str) -> List[tuple]:
        """Load roster rows for context (8-column read). Verbatim from ``_ctx_roster``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                db.adapt_params(
                    """
                SELECT p.player_id, p.name, p.role, p.value, pcs.average_overall, pcs.average_last_five,
                       sc.rating, sc.matches_started
                FROM player_championship_stats pcs
                JOIN players p ON pcs.player_id = p.player_id
                LEFT JOIN sofascore_cache sc ON LOWER(p.name) = LOWER(sc.player_name)
                WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?
                ORDER BY p.value DESC
            """
                ),
                (championship_id, team_id),
            )
            return cursor.fetchall()

    def get_free_agents(self, championship_id: str) -> List[tuple]:
        """Load top free agents. Verbatim from ``_ctx_free_agents``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                db.adapt_params(
                    """
                SELECT p.name, p.role, p.value, pcs.average_overall, pcs.average_last_five,
                       sc.rating
                FROM player_championship_stats pcs
                JOIN players p ON pcs.player_id = p.player_id
                LEFT JOIN sofascore_cache sc ON LOWER(p.name) = LOWER(sc.player_name)
                WHERE pcs.championship_id = ? AND (pcs.owner_team_id IS NULL OR pcs.owner_team_name = 'Free Agent')
                AND pcs.average_overall > 0
                ORDER BY pcs.average_overall DESC
                LIMIT 30
            """
                ),
                (championship_id,),
            )
            return cursor.fetchall()

    def get_clausulables(self, championship_id: str) -> List[tuple]:
        """Load top clausulables. Verbatim from ``_ctx_clausulables``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                db.adapt_params(
                    """
                SELECT p.name, p.role, p.value, pcs.average_overall, pcs.clause_price,
                       pcs.owner_team_name, sc.rating
                FROM player_championship_stats pcs
                JOIN players p ON pcs.player_id = p.player_id
                LEFT JOIN sofascore_cache sc ON LOWER(p.name) = LOWER(sc.player_name)
                WHERE pcs.championship_id = ? AND pcs.clause_price > 0
                AND pcs.owner_team_id IS NOT NULL AND pcs.owner_team_name != 'Free Agent'
                AND pcs.average_overall > 0
                ORDER BY (pcs.average_overall / (CAST(pcs.clause_price AS FLOAT) / 1000000.0)) DESC
                LIMIT 15
            """
                ),
                (championship_id,),
            )
            return cursor.fetchall()

    def get_transactions(self, championship_id: str, team_id: str) -> List[tuple]:
        """Load recent transactions. Verbatim from ``_ctx_transactions``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                db.adapt_params(
                    """
                SELECT p.name, t.price, t.transaction_date,
                       CASE WHEN t.buyer_team_id = ? THEN 'COMPRA' ELSE 'VENTA' END as type
                FROM transactions t
                JOIN players p ON t.player_id = p.player_id
                WHERE t.championship_id = ? AND (t.buyer_team_id = ? OR t.seller_team_id = ?)
                ORDER BY t.transaction_date DESC
                LIMIT 15
            """
                ),
                (team_id, championship_id, team_id, team_id),
            )
            return cursor.fetchall()

    def get_budget_data(self, user_id: str, championship_id: str, team_id: str) -> Dict:
        """Load budget figures for context. Same reads as ``_ctx_budget``."""
        return self.get_balance_data(user_id, championship_id, team_id)

    def get_next_matches(
        self, championship_id: str, team_id: str
    ) -> Tuple[Optional[int], List[tuple], List[tuple]]:
        """Load ``(next_matchday, match_rows, my_player_rows)``. Verbatim from ``_ctx_next_matches``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                db.adapt_params("SELECT MAX(matchday) FROM match_odds WHERE championship_id = ?"),
                (championship_id,),
            )
            row = cursor.fetchone()
            if not row or not row[0]:
                return None, [], []
            next_matchday = row[0]

            cursor.execute(
                db.adapt_params(
                    """
                SELECT home_team_id, home_team_name, away_team_id, away_team_name,
                       odds_home, odds_draw, odds_away, match_date
                FROM match_odds
                WHERE championship_id = ? AND matchday = ?
                ORDER BY match_date ASC
            """
                ),
                (championship_id, next_matchday),
            )
            matches = cursor.fetchall()

            cursor.execute(
                db.adapt_params(
                    """
                SELECT p.name, p.real_team_id, p.role
                FROM player_championship_stats pcs
                JOIN players p ON pcs.player_id = p.player_id
                WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?
            """
                ),
                (championship_id, team_id),
            )
            my_players = cursor.fetchall()

        return next_matchday, matches, my_players

    def get_is_pro(self, championship_id: str) -> bool:
        """Load PRO mode flag. Verbatim from ``_ctx_formations``."""
        db = self._get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                db.adapt_params(
                    "SELECT is_pro FROM user_championships WHERE championship_id = ? LIMIT 1"
                ),
                (championship_id,),
            )
            row = cursor.fetchone()
            return bool(row[0]) if row and row[0] else False

    def get_market_today(self, championship_id: str) -> List[tuple]:
        """Read today's cached computer-market rows. Verbatim from ``_ctx_market_from_db``.

        Returns an empty list on any error (table may not exist yet) — preserving
        the former defensive ``except Exception: return ""`` degradation (BR3.3).
        """
        today = date.today().isoformat()
        db = self._get_db()
        try:
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                cursor.execute(
                    db.adapt_params(
                        "SELECT player_name, position, value, average, matches_played "
                        "FROM market_today WHERE championship_id = ? AND market_date = ? "
                        "AND is_computer = TRUE"
                    ),
                    (championship_id, today),
                )
                return cursor.fetchall()
        except Exception:
            return []  # Table might not exist yet

    def save_market_today(self, championship_id: str, players: List[Dict]) -> None:
        """Persist today's market snapshot. Verbatim from ``_save_market_to_db``.

        Hosts the SECOND ``CREATE TABLE IF NOT EXISTS market_today`` DDL (reviewer
        note R-04, FR4.1/FR4.2) and strips the requesting user's private ``bid``
        before caching (shared per championship/date). Swallows errors with a
        warning, preserving the former degradation.
        """
        today = date.today().isoformat()
        db = self._get_db()
        try:
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS market_today (
                        id SERIAL PRIMARY KEY,
                        championship_id TEXT NOT NULL,
                        market_date TEXT NOT NULL,
                        player_id TEXT,
                        player_name TEXT,
                        slug TEXT,
                        position TEXT,
                        position2 TEXT,
                        team TEXT,
                        team_logo TEXT,
                        value INTEGER,
                        market_price INTEGER,
                        change INTEGER DEFAULT 0,
                        average REAL,
                        home_average REAL,
                        away_average REAL,
                        matches_played INTEGER,
                        points INTEGER DEFAULT 0,
                        photo TEXT,
                        expiration TEXT,
                        is_computer BOOLEAN DEFAULT TRUE,
                        raw_json TEXT
                    )
                """
                )
                cursor.execute(
                    db.adapt_params(
                        "DELETE FROM market_today WHERE championship_id = ? AND market_date = ?"
                    ),
                    (championship_id, today),
                )

                for p in players:
                    avg_data = p.get("average", {})
                    avg = avg_data.get("average", 0) if isinstance(avg_data, dict) else 0
                    home_avg = avg_data.get("homeAverage") if isinstance(avg_data, dict) else None
                    away_avg = avg_data.get("awayAverage") if isinstance(avg_data, dict) else None
                    matches = avg_data.get("matches", 0) if isinstance(avg_data, dict) else 0

                    # SECURITY: 'bid' is the requesting user's private bid. This cache
                    # is shared per (championship, date), so strip it before storing to
                    # avoid leaking one user's bids to another. Per-user bids are fetched
                    # live in the market endpoint.
                    p_cached = {k: v for k, v in p.items() if k != "bid"}

                    cursor.execute(
                        db.adapt_params(
                            """
                        INSERT INTO market_today (championship_id, market_date, player_id, player_name, slug,
                            position, position2, team, team_logo, value, market_price, change,
                            average, home_average, away_average, matches_played, points, photo, expiration, is_computer, raw_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                        ),
                        (
                            championship_id,
                            today,
                            p.get("id", ""),
                            p.get("name", ""),
                            p.get("slug", ""),
                            p.get("role", ""),
                            p.get("role2", ""),
                            p.get("team", ""),
                            p.get("logo", ""),
                            p.get("value", 0),
                            p.get("price", p.get("value", 0)),
                            p.get("change", 0),
                            avg,
                            float(home_avg) if home_avg and home_avg != "NaN" else None,
                            float(away_avg) if away_avg and away_avg != "NaN" else None,
                            matches,
                            p.get("points", 0),
                            p.get("photo", ""),
                            p.get("expirationDate", ""),
                            p.get("computer", False),
                            json_mod.dumps(p_cached, ensure_ascii=False),
                        ),
                    )

                conn.commit()
                logger.info(f"Saved {len(players)} market players to DB for {championship_id}")
        except Exception as e:
            logger.warning(f"Could not save market to DB: {e}")
