"""Read-from-sync layer for ``GET /api/v1/favorites/my`` (BR2.1, BR2.2, BR3.1).

Serves the user's favorited free-agent players from the already-synced Neon
tables, replacing the heavy live ``get_championship_players`` catalog download.

Data sources (all synced, no live call on the normal path):
- ``player_favorites`` — the user's favorite ``player_id`` set.
- ``players`` + ``player_championship_stats`` — the synced player rows; a
  favorite is a *free agent* when its ``owner_team_id`` is NULL.
- ``market_today`` — the rich per-player stats (``value``/``change``/averages/
  ``matches``/``points``/``team``/``team_logo``/position) looked up by
  ``player_id`` for today's market date. Free agents are precisely what
  ``market_today`` holds, so in the normal case every visible field is exact.
- ``sofascore_cache`` — via the existing ``_sofascore_helpers``.

The response dicts match the current endpoint contract byte-for-byte (same
keys, order, types); when a favorite is not in today's ``market_today`` the few
numeric fields fall back to the SAME defaults the live route produces
(``change=0``, ``home_average=None``, ``away_average=None``, ``matches=0``,
``rating=0``, ``status=''``) — see BR6.1 and the characterization tests.

All SQL here is parameterized through ``db.adapt_params`` (the ``balances.py``
pattern); nothing lives in the router or the god-files (BR1.1).
"""

import logging
from datetime import date
from typing import Dict, List, Tuple

from app.api.v1.endpoints._helpers import clean_float
from app.api.v1.endpoints._sofascore_helpers import (
    build_sofascore_map,
    lookup_sofascore,
)

logger = logging.getLogger(__name__)

# Same ordering map the live route uses (BR2.2).
POSITION_ORDER = {"portero": 0, "defensa": 1, "centrocampista": 2, "delantero": 3}


def read_favorites(
    db, championship_id: str, user_id: str
) -> Tuple[List[Dict], bool]:
    """Read the user's favorite free-agent players from synced data.

    Args:
        db: db-connection handle honoring ``get_connection``/``get_cursor``/
            ``adapt_params``.
        championship_id: championship scope.
        user_id: the authenticated user's id.

    Returns:
        ``(players, has_synced)``:
        - ``players``: list of contract dicts, ordered ``position_order`` asc then
          ``value`` desc. Empty list when the user has no favorites at all.
        - ``has_synced``: ``True`` when at least one synced free-agent favorite row
          was found. ``False`` signals the router to fall back to the live route
          (sync-miss, BR3.1). An empty favorites set returns
          ``([], True)`` — that is a correct empty answer, NOT a sync-miss.

    Never returns an empty result purely because ``market_today`` is empty: the
    free-agent set comes from ``players``/``player_championship_stats``, and
    ``market_today`` only enriches it.
    """
    today = date.today().isoformat()

    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)

        # 1) Favorite player ids (cheap).
        sql_fav = db.adapt_params(
            "SELECT player_id FROM player_favorites WHERE championship_id = ? AND user_id = ?"
        )
        cursor.execute(sql_fav, (championship_id, user_id))
        fav_ids = [row[0] for row in cursor.fetchall()]

        # No favorites → correct empty answer (not a sync-miss). Matches the
        # live route's early ``{players: [], total: 0}`` return (BR6.1).
        if not fav_ids:
            return [], True

        placeholders = ",".join("?" for _ in fav_ids)

        # 2) Synced free-agent favorites: players JOIN stats where owner is NULL.
        #    This is the authoritative "synced + free-agent" set that decides
        #    has_synced (BR2.1). owner_team_id IS NULL == free agent.
        #    value / average come from the ALWAYS-synced tables (players,
        #    player_championship_stats), which cover every player — not just the
        #    ~30 in today's market_today. market_today only supplements
        #    change/home/away/matches/points below.
        sql_players = db.adapt_params(
            f"""
            SELECT p.player_id, p.name, p.role, p.role2, p.slug, p.real_team_name,
                   p.value, pcs.average_overall
            FROM player_championship_stats pcs
            JOIN players p ON p.player_id = pcs.player_id
            WHERE pcs.championship_id = ?
              AND pcs.owner_team_id IS NULL
              AND p.player_id IN ({placeholders})
            """
        )
        cursor.execute(sql_players, (championship_id, *fav_ids))
        player_rows = cursor.fetchall()

        # Sync-miss: 0 synced free-agent rows for the favorites → fall back live.
        if not player_rows:
            return [], False

        # 3) market_today lookup by player_id for today's date (rich stats). Left
        #    lookup: a favorite not in today's market keeps the live defaults.
        market_by_id: Dict[str, Dict] = {}
        sql_market = db.adapt_params(
            f"""
            SELECT player_id, player_name, slug, position, position2, team, team_logo,
                   value, change, average, home_average, away_average, matches_played, points
            FROM market_today
            WHERE championship_id = ? AND market_date = ?
              AND player_id IN ({placeholders})
            """
        )
        cursor.execute(sql_market, (championship_id, today, *fav_ids))
        for mr in cursor.fetchall():
            market_by_id[mr[0]] = {
                "player_name": mr[1],
                "slug": mr[2],
                "position": mr[3],
                "position2": mr[4],
                "team": mr[5],
                "team_logo": mr[6],
                "value": mr[7],
                "change": mr[8],
                "average": mr[9],
                "home_average": mr[10],
                "away_average": mr[11],
                "matches": mr[12],
                "points": mr[13],
            }

    # 3b) Points per player from player_performance (always-synced, aggregated),
    #     covering players not present in today's market_today.
    points_by_id: Dict[str, int] = {}
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql_points = db.adapt_params(
            f"""
            SELECT player_id, COALESCE(SUM(points), 0)
            FROM player_performance
            WHERE championship_id = ? AND player_id IN ({placeholders})
            GROUP BY player_id
            """
        )
        try:
            cursor.execute(sql_points, (championship_id, *fav_ids))
            for pr in cursor.fetchall():
                points_by_id[pr[0]] = pr[1] or 0
        except Exception:
            # player_performance missing/empty is non-fatal: points default to 0
            # (same as the live route when performance data is absent).
            points_by_id = {}

    # 4) Sofascore enrichment via the existing helper (reads sofascore_cache).
    sofascore_map = build_sofascore_map(db, championship_id)

    players: List[Dict] = []
    for prow in player_rows:
        player_id, name, role, role2, slug, real_team_name, pval, avg_overall = prow
        role = role or ""
        mt = market_by_id.get(player_id, {})

        # Team: prefer market_today; fall back to players.real_team_name (synced
        # for every player). team_logo only exists in market_today.
        team = mt.get("team") or real_team_name or ""
        team_logo = mt.get("team_logo") or ""
        sf = lookup_sofascore(sofascore_map, name, team)

        # value/average/points from the ALWAYS-synced tables (cover every player);
        # change/home/away/matches only exist in market_today, so they supplement
        # when the favorite is in today's market, else default (as the live route
        # does when absent). BR6.1.
        value = (mt.get("value") if mt.get("value") not in (None, 0) else pval) or 0
        average = clean_float(mt.get("average") if mt else None, None)
        if average is None:
            average = clean_float(avg_overall, 0)
        points = points_by_id.get(player_id)
        if points is None:
            points = mt.get("points", 0) if mt else 0
        if points is None:
            points = 0
        change = mt.get("change", 0) if mt else 0
        if change is None:
            change = 0
        home_average = clean_float(mt.get("home_average"), None) if mt else None
        away_average = clean_float(mt.get("away_average"), None) if mt else None
        matches = mt.get("matches", 0) if mt else 0
        if matches is None:
            matches = 0

        players.append({
            "player_id": player_id,
            "name": name or "",
            "slug": mt.get("slug") or slug or "",
            "position": role,
            "position2": (mt.get("position2") if mt.get("position2") is not None else role2) or "",
            "team": team,
            "team_logo": team_logo,
            "value": value,
            "change": change,
            "points": points,
            "average": average,
            "home_average": home_average,
            "away_average": away_average,
            "matches": matches,
            # `rating` (flat) and `status` have no synced source; the front does
            # not render them. Freeze the live route's defaults (BR6.1).
            "rating": 0,
            "sofascore_rating": sf.get("rating"),
            "sofascore_url": sf.get("url"),
            "starter_pct": sf.get("starter_pct"),
            "status": "",
            "position_order": POSITION_ORDER.get(role.lower(), 9),
        })

    # 5) Sort: position_order asc, then value desc (BR2.2).
    players.sort(key=lambda x: (x["position_order"], -x["value"]))

    return players, True
