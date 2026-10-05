"""Infrastructure adapter for ``match-odds`` — the only module with SQL (BR1.3).

Implements :class:`MatchOddsDataPort` by hosting the raw SQL formerly inline in
``DataManagerV2.save_match_odds`` / ``get_match_odds``, moved **verbatim**
including the ``if db_type in ["postgresql", "postgres"]: ... else: (SQLite)``
engine branch (BR1.2/FR1.4). It reuses the facade's ``DBConnection`` (``dm.db``)
and the shared ``ensure_championship_exists`` helper (still owned by the facade
until the schema-lifecycle module is extracted), so the production result is
byte-for-byte identical (BR3.1).

Constructor injection with a default (the ``analytics`` pattern): the adapter
defaults to a fresh ``DataManagerV2(skip_init=True)`` so production behavior is
unchanged; tests drive it with the in-memory fake via an injected facade.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.data_manager.match_odds.domain.ports import MatchOddsDataPort


class MatchOddsAdapter(MatchOddsDataPort):
    """Adapt the match-odds SQL (verbatim) to :class:`MatchOddsDataPort`."""

    def __init__(self, dm: Optional[Any] = None) -> None:
        if dm is None:
            from app.services.data_manager_v2 import DataManagerV2

            dm = DataManagerV2(skip_init=True)
        self.dm = dm

    @property
    def db(self):
        # Read the connection live from the facade so a test that reassigns
        # ``dm.db`` (the in-memory fake) is honored, exactly as the former
        # method read ``self.db`` on the facade.
        return self.dm.db

    def save_match_odds(
        self,
        championship_id: str,
        matches: List[Dict],
        round_id: Optional[str] = None,
        matchday: Optional[int] = None,
    ) -> None:
        """Persist betting odds for upcoming matches"""
        if not matches:
            return

        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            self.dm.ensure_championship_exists(championship_id, conn=conn, cursor=cursor)

            if self.db.db_type in ["postgresql", "postgres"]:
                sql = """
                    INSERT INTO match_odds (
                        championship_id, match_id, round_id, matchday, match_date,
                        home_team_id, home_team_name, away_team_id, away_team_name,
                        odds_home, odds_draw, odds_away,
                        best_bookmaker_home, best_bookmaker_draw, best_bookmaker_away,
                        fetched_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (championship_id, match_id) DO UPDATE SET
                        round_id = EXCLUDED.round_id,
                        matchday = EXCLUDED.matchday,
                        match_date = EXCLUDED.match_date,
                        home_team_id = EXCLUDED.home_team_id,
                        home_team_name = EXCLUDED.home_team_name,
                        away_team_id = EXCLUDED.away_team_id,
                        away_team_name = EXCLUDED.away_team_name,
                        odds_home = EXCLUDED.odds_home,
                        odds_draw = EXCLUDED.odds_draw,
                        odds_away = EXCLUDED.odds_away,
                        best_bookmaker_home = EXCLUDED.best_bookmaker_home,
                        best_bookmaker_draw = EXCLUDED.best_bookmaker_draw,
                        best_bookmaker_away = EXCLUDED.best_bookmaker_away,
                        fetched_at = EXCLUDED.fetched_at
                """
            else:
                sql = """
                    INSERT OR REPLACE INTO match_odds (
                        championship_id, match_id, round_id, matchday, match_date,
                        home_team_id, home_team_name, away_team_id, away_team_name,
                        odds_home, odds_draw, odds_away,
                        best_bookmaker_home, best_bookmaker_draw, best_bookmaker_away,
                        fetched_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                sql = self.db.adapt_params(sql)

            now = datetime.now()

            for match in matches:
                match_id = match.get("id") or match.get("_id")
                if not match_id:
                    continue

                match_date_str = match.get("date") or match.get("matchDate")
                match_date = None
                if match_date_str:
                    try:
                        match_date = datetime.fromisoformat(match_date_str.replace("Z", "+00:00"))
                    except Exception:
                        match_date = None

                odds_info = match.get("odds", {})
                sels = odds_info.get("sels", []) if isinstance(odds_info, dict) else []

                odds_home = odds_draw = odds_away = None
                bookmaker_home = bookmaker_draw = bookmaker_away = None

                for sel in sels:
                    selection_name = sel.get("sn", "").lower()
                    odds_list = sel.get("odds", [])
                    if not odds_list:
                        continue
                    best = max(odds_list, key=lambda o: o.get("c", 0) or 0)
                    price = best.get("c") or best.get("f")
                    bookmaker = best.get("bid")
                    if "draw" in selection_name or selection_name in ("empate", "tie"):
                        odds_draw = price
                        bookmaker_draw = bookmaker
                    elif (
                        selection_name == match.get("homeTeam", {}).get("name", "").lower()
                        or sel.get("ssn") == "1"
                    ):
                        odds_home = price
                        bookmaker_home = bookmaker
                    else:
                        odds_away = price
                        bookmaker_away = bookmaker

                cursor.execute(
                    sql,
                    (
                        championship_id,
                        match_id,
                        round_id or match.get("roundId"),
                        matchday,
                        match_date,
                        match.get("homeTeam", {}).get("id"),
                        match.get("homeTeam", {}).get("name"),
                        match.get("awayTeam", {}).get("id"),
                        match.get("awayTeam", {}).get("name"),
                        odds_home,
                        odds_draw,
                        odds_away,
                        bookmaker_home,
                        bookmaker_draw,
                        bookmaker_away,
                        now,
                    ),
                )

    def get_match_odds(
        self, championship_id: str, matchday: Optional[int] = None, upcoming_only: bool = False
    ) -> List[Dict]:
        """Retrieve stored match odds, optionally filtered by matchday or future date"""
        with self.db.get_connection() as conn:
            cursor = self.db.get_cursor(conn)

            base_sql = """
                SELECT match_id, round_id, matchday, match_date,
                       home_team_id, home_team_name,
                       away_team_id, away_team_name,
                       odds_home, odds_draw, odds_away,
                       best_bookmaker_home, best_bookmaker_draw, best_bookmaker_away,
                       fetched_at
                FROM match_odds
                WHERE championship_id = ?
            """
            params: List[Any] = [championship_id]

            if matchday is not None:
                base_sql += " AND matchday = ?"
                params.append(matchday)

            if upcoming_only:
                base_sql += " AND (match_date IS NULL OR match_date >= ? )"
                params.append(datetime.now())

            base_sql += " ORDER BY match_date"
            if self.db.db_type in ["postgresql", "postgres"]:
                base_sql += " NULLS LAST"
            base_sql = self.db.adapt_params(base_sql)

            cursor.execute(base_sql, tuple(params))
            rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append(
                {
                    "match_id": row[0],
                    "round_id": row[1],
                    "matchday": row[2],
                    "match_date": row[3],
                    "home_team_id": row[4],
                    "home_team_name": row[5],
                    "away_team_id": row[6],
                    "away_team_name": row[7],
                    "odds_home": row[8],
                    "odds_draw": row[9],
                    "odds_away": row[10],
                    "best_bookmaker_home": row[11],
                    "best_bookmaker_draw": row[12],
                    "best_bookmaker_away": row[13],
                    "fetched_at": row[14],
                }
            )
        return results
