from datetime import datetime
from typing import Dict, List, Any, Optional

from app.services.data_manager_v2 import DataManagerV2


NAME_ALIAS_MAP = {
    "pedro argüero solaeche": ["Pedro", "Pedrito", "Pedro Mari"],
    "lucas pratto": ["Lucas", "Luke", "Luckie"],
    "hulio united fc": ["Bruno", "Beni", "Hulio"],
    "javier perez irigoyen": ["Perez", "Perico", "JP"],
    "jorge ugalde": ["Jorge", "George", "Ugalde"],
    "alvaro marquez": ["Marquez", "Marqui", "AM"],
    "antón fernández": ["Anton", "Toni", "El Mercader"],
    "anton fernandez": ["Anton", "Toni", "El Mercader"],
    "vic.chicharro": ["Victor", "Vic", "Tort"],
    "victor chicharro": ["Victor", "Vic", "Tort"],
    "pablo paredes lapeña": ["Peu", "Pablo", "Paredes"],
    "pablo paredes lapena": ["Peu", "Pablo", "Paredes"],
    "santi sesma": ["Santi", "El gemelo malo", "SS"],
    "bayern de los caídos": ["Sesma", "Sexman", "JS"],
    "bayern de los caidos": ["Sesma", "Sexman", "JS"],
    "borja domingo": ["Borja", "Borch", "Borjita"],
    "gonzalo cadarso ruiz": ["Gonzalo", "Cadarso", "Gon"],
    "diego b.": ["Boter", "Diego", "Bout"],
    "diego b": ["Boter", "Diego", "Bout"],
    "patxo torre": ["Patxo", "Patxete", "El gran jefe"],
}


class MatchdayHumorDataAssembler:
    """
    Aggregates rich contextual data for a given championship matchday.
    The resulting payload feeds the humor article generator with
    performance summaries, timelines, and recent form metrics.
    """

    def __init__(self, data_manager: Optional[DataManagerV2] = None):
        self.dm = data_manager or DataManagerV2(skip_init=True)

    def build_dataset(self, championship_id: str, matchday: int) -> Dict[str, Any]:
        teams = self._fetch_team_points(championship_id, matchday)
        self._assign_overall_ranks(teams)
        self._assign_matchday_ranks(teams)
        # Remove raw rank hints before passing to model (only keep for debug)
        for info in teams.values():
            info.pop("raw_overall_start_rank", None)
            info.pop("raw_overall_end_rank", None)

        return {
            "championship_id": championship_id,
            "matchday": matchday,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "teams": list(teams.values())
        }

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _fetch_team_points(self, championship_id: str, matchday: int) -> Dict[str, Dict[str, Any]]:
        query = '''
            SELECT
                ts.team_id,
                t.team_name,
                t.user_id,
                ts.position AS position_end,
                ts.points AS points_total,
                ts.points_this_matchday AS points_earned,
                COALESCE(prev.points, 0) AS points_start,
                COALESCE(prev.position, ts.position) AS position_start
            FROM team_standings ts
            JOIN teams t ON t.team_id = ts.team_id
            LEFT JOIN team_standings prev
                ON prev.championship_id = ts.championship_id
               AND prev.team_id = ts.team_id
               AND prev.matchday = ts.matchday - 1
            WHERE ts.championship_id = ?
              AND ts.matchday = ?
            ORDER BY ts.position ASC
        '''
        query = self.dm.db.adapt_params(query)

        teams: Dict[str, Dict[str, Any]] = {}
        with self.dm.db.get_connection() as conn:
            cursor = self.dm.db.get_cursor(conn)
            cursor.execute(query, (championship_id, matchday))
            for row in cursor.fetchall():
                if isinstance(row, tuple):
                    (
                        team_id,
                        team_name,
                        user_id,
                        position_end,
                        points_total,
                        points_earned,
                        points_start,
                        position_start
                    ) = row
                else:
                    team_id = row["team_id"]
                    team_name = row["team_name"]
                    user_id = row["user_id"]
                    position_end = row["position_end"]
                    points_total = row["points_total"]
                    points_earned = row["points_earned"]
                    points_start = row["points_start"]
                    position_start = row["position_start"]

                total_start = points_start or 0
                matchday_points = points_earned or 0
                total_end = points_total or total_start

                teams[team_id] = {
                    "team_id": team_id,
                    "team_name": team_name,
                    "user_id": user_id,
                    "raw_overall_start_rank": position_start,
                    "raw_overall_end_rank": position_end,
                    # Points tracking
                    "total_points_start": total_start,
                    "total_points_end": total_end,
                    "matchday_points": matchday_points,
                    "points_start": total_start,
                    "points_earned": matchday_points,
                    "points_total": total_end,
                }
        return teams

    @staticmethod
    def _lookup_aliases(name: Optional[str]) -> Optional[List[str]]:
        if not name:
            return None
        return NAME_ALIAS_MAP.get(name.lower())

    @staticmethod
    def _preferred_name(name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        aliases = NAME_ALIAS_MAP.get(name.lower())
        if aliases:
            return aliases[0]
        return name

    @staticmethod
    def _position_delta(start: Optional[int], end: Optional[int]) -> Optional[int]:
        if start is None or end is None:
            return None
        return (start or 0) - (end or 0)

    @staticmethod
    def _assign_overall_ranks(teams: Dict[str, Dict[str, Any]]):
        start_ranking = sorted(
            [(team_id, info.get("total_points_start", 0)) for team_id, info in teams.items()],
            key=lambda item: item[1],
            reverse=True
        )
        end_ranking = sorted(
            [(team_id, info.get("total_points_end", 0)) for team_id, info in teams.items()],
            key=lambda item: item[1],
            reverse=True
        )

        def _assign(ranking):
            rank_map = {}
            current_rank = 0
            last_points = None
            for index, (team_id, points) in enumerate(ranking, start=1):
                if last_points is None or points != last_points:
                    current_rank = index
                    last_points = points
                rank_map[team_id] = current_rank
            return rank_map

        start_map = _assign(start_ranking)
        end_map = _assign(end_ranking)

        for team_id, info in teams.items():
            info["overall_start_rank"] = start_map.get(team_id)
            info["overall_end_rank"] = end_map.get(team_id)
            info["position_change"] = (
                info["overall_start_rank"] - info["overall_end_rank"]
                if info.get("overall_start_rank") is not None and info.get("overall_end_rank") is not None
                else None
            )

    @staticmethod
    def _assign_matchday_ranks(teams: Dict[str, Dict[str, Any]]):
        ranking = sorted(
            [(team_id, info.get("matchday_points", 0)) for team_id, info in teams.items()],
            key=lambda item: item[1],
            reverse=True
        )
        rank_map: Dict[str, int] = {}
        current_rank = 0
        last_points = None
        for index, (team_id, points) in enumerate(ranking, start=1):
            if last_points is None or points != last_points:
                current_rank = index
                last_points = points
            rank_map[team_id] = current_rank

        for team_id, info in teams.items():
            info["matchday_rank"] = rank_map.get(team_id)

