"""Analytics endpoints exposing advanced championship insights."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.services.analytics_service import AnalyticsService
from app.core.config import CHAMPIONSHIP_ID


def get_service() -> AnalyticsService:
    return AnalyticsService()


router = APIRouter()


@router.get("/championship/trends")
async def championship_trends(
    window: int = Query(default=5, ge=1, le=38),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_championship_trends(championship_id=championship_id, window=window)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/championship/classification-full")
async def championship_classification_full(
    window: Optional[int] = Query(default=None, ge=1, le=38),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
):
    """Combined classification + momentum endpoint — single optimized query."""
    try:
        from app.services.db_connection import get_db
        import statistics

        db = get_db()

        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)

            # Get latest matchday
            cursor.execute(
                db.adapt_params("SELECT MAX(matchday) FROM team_standings WHERE championship_id = ?"),
                (championship_id,)
            )
            latest_matchday = cursor.fetchone()[0] or 0

            # Calculate window filter
            min_matchday = 1
            if window and latest_matchday:
                min_matchday = max(latest_matchday - window + 1, 1)

            # Single JOIN query: standings + team names
            sql = """
                SELECT ts.team_id, t.team_name, ts.matchday, ts.points_this_matchday
                FROM team_standings ts
                LEFT JOIN teams t ON ts.team_id = t.team_id
                WHERE ts.championship_id = %s AND ts.matchday >= %s
                ORDER BY ts.team_id, ts.matchday
            """
            cursor.execute(sql, (championship_id, min_matchday))
            rows = cursor.fetchall()

        # Group by team
        teams_data: dict = {}
        for row in rows:
            team_id, team_name, matchday, pts_md = row[0], row[1], row[2], row[3] or 0
            if team_id not in teams_data:
                teams_data[team_id] = {"team_id": team_id, "team_name": team_name or team_id, "points": []}
            teams_data[team_id]["points"].append(pts_md)

        # Calculate stats
        classification = []
        for team in teams_data.values():
            pts = team["points"]
            total = sum(pts)
            avg = statistics.mean(pts) if pts else 0
            max_p = max(pts) if pts else 0
            min_p = min(pts) if pts else 0
            trend = (pts[-1] - pts[-2]) if len(pts) >= 2 else 0
            momentum = 0.0
            if len(pts) >= 2:
                diffs = [b - a for a, b in zip(pts[:-1], pts[1:])]
                momentum = statistics.mean(diffs) if diffs else 0

            classification.append({
                "team_id": team["team_id"],
                "team_name": team["team_name"],
                "total_points": round(total, 2),
                "average_points": round(avg, 2),
                "matches_count": len(pts),
                "max_points": max_p,
                "min_points": min_p,
                "trend": round(trend, 2),
                "momentum": round(momentum, 2),
            })

        # Sort by total points desc and assign rank
        classification.sort(key=lambda x: x["total_points"], reverse=True)
        for idx, entry in enumerate(classification, 1):
            entry["rank"] = idx

        included = list(range(min_matchday, latest_matchday + 1))

        return {
            "championship_id": championship_id,
            "latest_matchday": latest_matchday,
            "window": window,
            "included_matchdays": included,
            "classification": classification,
        }
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/championship/custom-classification")
async def championship_custom_classification(
    window: Optional[int] = Query(default=5, ge=1, le=38),
    exclude_matchday: Optional[List[int]] = Query(default=None),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_championship_custom_classification(
            championship_id=championship_id,
            window=window,
            exclude_matchdays=exclude_matchday
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/championship/heatmap")
async def championship_heatmap(
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_championship_heatmap(championship_id=championship_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/players/form")
async def player_form(
    window: int = Query(default=5, ge=1, le=10),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_player_form(championship_id=championship_id, window=window)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/players/value-trend")
async def player_value_trend(
    window_days: int = Query(default=30, ge=1, le=180),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_player_value_trend(championship_id=championship_id, window=window_days)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/users/consistency")
async def user_consistency(
    window: int = Query(default=10, ge=1, le=38),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_user_consistency(championship_id=championship_id, window=window)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/users/market-activity")
async def user_market_activity(
    window_days: int = Query(default=30, ge=1, le=120),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_user_market_activity(championship_id=championship_id, window_days=window_days)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/market/watchlist")
async def market_watchlist(
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
):
    """Watchlist of free agents enriched with photo, position, sofascore, and trend."""
    try:
        from app.services.db_connection import get_db
        from app.api.v1.endpoints._sofascore_helpers import build_sofascore_map, lookup_sofascore
        from app.api.v1.endpoints._helpers import get_user_futmondo_client

        db = get_db()

        # Get user ID for favorites lookup
        user_id = None
        try:
            client = get_user_futmondo_client(request)
            user_id = client.user_id
        except Exception:
            pass

        # 1. Get free agent candidates with their stats
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = db.adapt_params('''
                SELECT pcs.player_id, p.name, pcs.average_last_five, pcs.average_overall,
                       p.role, p.role2, p.real_team_id, p.real_team_name, p.slug, p.value
                FROM player_championship_stats pcs
                LEFT JOIN players p ON p.player_id = pcs.player_id
                WHERE pcs.championship_id = ? AND (pcs.owner_team_id IS NULL OR pcs.owner_team_id = '')
            ''')
            cursor.execute(sql, (championship_id,))
            rows = cursor.fetchall()

        # 1b. Get user's favorite player IDs
        favorite_ids = set()
        if user_id:
            try:
                with db.get_connection() as conn:
                    cursor = db.get_cursor(conn)
                    sql = db.adapt_params("SELECT player_id FROM player_favorites WHERE championship_id = ? AND user_id = ?")
                    cursor.execute(sql, (championship_id, user_id))
                    favorite_ids = {row[0] for row in cursor.fetchall()}
            except Exception:
                pass

        # 2. Build sofascore lookup
        sofascore_map = build_sofascore_map(db, championship_id)

        # 3. LaLiga team map for resolving names
        LALIGA_TEAMS = {
            "504e581e4d8bec9a670000c6": "Real Madrid",
            "504e581e4d8bec9a670000c7": "Barcelona",
            "504e581e4d8bec9a670000c8": "Atlético de Madrid",
            "504e581e4d8bec9a670000c9": "Athletic de Bilbao",
            "504e581e4d8bec9a670000ca": "Rayo Vallecano",
            "504e581e4d8bec9a670000cb": "Valencia",
            "504e581e4d8bec9a670000cc": "Betis",
            "504e581e4d8bec9a670000cd": "Getafe",
            "504e581e4d8bec9a670000ce": "Real Sociedad",
            "504e581e4d8bec9a670000cf": "Levante",
            "504e581e4d8bec9a670000d0": "Espanyol",
            "504e581e4d8bec9a670000d1": "Osasuna",
            "504e581e4d8bec9a670000d5": "Sevilla",
            "504e581e4d8bec9a670000d6": "Málaga",
            "504e581e4d8bec9a670000d8": "Deportivo de la Coruña",
            "504e581e4d8bec9a670000d9": "Celta de Vigo",
            "51b889b1e401a15f2c0000f0": "Elche",
            "51b890f5b986415a2c000012": "Villarreal",
            "52038563b8d07d930b00008a": "Alavés",
            "520e4ee4a776cc826b00004b": "Racing",
        }

        # 4. Process players
        watchlist = []
        for row in rows:
            player_id, name, avg_last_five, avg_overall, role, role2, real_team_id, real_team_name, slug, value = row

            # Pick best available average, skip NaN
            average = None
            if avg_last_five is not None and avg_last_five == avg_last_five and avg_last_five > 0:
                average = avg_last_five
            elif avg_overall is not None and avg_overall == avg_overall and avg_overall > 0:
                average = avg_overall
            if not average:
                continue

            value = value or 0
            ratio = round(average / (value / 1_000_000), 3) if value > 0 else 0
            team_name = LALIGA_TEAMS.get(real_team_id or "", "") or real_team_name or ""

            # Sofascore enrichment
            sf = lookup_sofascore(sofascore_map, name or "", team_name)

            # Trend: avg_last_five - avg_overall (positive = improving recently)
            # Streak: indicator based on recent average performance (avg_last_five >= 8 = "en forma")
            streak = 0
            trend = 0.0
            if avg_last_five is not None and avg_last_five == avg_last_five and avg_last_five > 0:
                if avg_overall is not None and avg_overall == avg_overall and avg_overall > 0:
                    trend = round(avg_last_five - avg_overall, 1)
                if avg_last_five >= 8:
                    streak = 1  # en forma

            watchlist.append({
                "player_id": player_id,
                "name": name or player_id,
                "slug": slug or "",
                "position": role or "",
                "position2": role2 or "",
                "team": team_name,
                "real_team_id": real_team_id or "",
                "value": value,
                "change": 0,  # free agents don't have daily change in this context
                "average": round(average, 1),
                "ratio": ratio,
                "sofascore_rating": sf.get("rating"),
                "sofascore_url": sf.get("url"),
                "starter_pct": sf.get("starter_pct"),
                "is_favorite": player_id in favorite_ids,
                "streak": streak,
                "trend": trend,
            })

        # Sort by average descending
        watchlist.sort(key=lambda x: x["average"], reverse=True)
        return {
            "championship_id": championship_id,
            "total": len(watchlist),
            "players": watchlist,
        }
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/clauses/network")
async def clause_network(
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_clause_network(championship_id=championship_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/opportunities/streaks")
async def opportunity_streaks(
    min_streak: int = Query(default=3, ge=2, le=10),
    threshold: float = Query(default=6.0, ge=0),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_opportunity_streaks(championship_id=championship_id, min_streak=min_streak, threshold=threshold)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/projections/matchday")
async def matchday_projections(
    matchday: Optional[int] = Query(default=None, ge=1, le=38),
    window: int = Query(default=5, ge=1, le=10),
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: AnalyticsService = Depends(get_service)
):
    try:
        return service.get_matchday_projections(championship_id=championship_id, matchday=matchday, window=window)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


