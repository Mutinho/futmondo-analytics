"""Shared helpers for Sofascore data calculations."""

CURRENT_SEASON = "26/27"
PREVIOUS_SEASON = "25/26"
TOTAL_MATCHDAYS = 38  # LaLiga standard


def calculate_starter_pct(matches_started: int, season_name: str, current_matchday: int = 0, matches_started_prev: int = 0) -> int | None:
    """Calculate starter percentage with season blending.
    
    Logic:
    - Season not started (matchday=0) or data is from previous season: starts_prev / 38
    - Current season matchday 1-9: weighted blend of current + previous
      weight_current = matchday / 10, weight_prev = 1 - weight_current
    - Current season matchday 10+: pure current season (starts / matchday)
    
    Args:
        matches_started: matches started from the cached season (could be current or prev)
        season_name: season string from cache (e.g. "LaLiga 25/26" or "LaLiga 26/27")
        current_matchday: current matchday of the league (0 if not started)
        matches_started_prev: matches started from previous season (stored separately)
    
    Returns:
        Integer percentage or None
    """
    is_current = CURRENT_SEASON in (season_name or "")
    
    # If we have current season data
    if is_current and current_matchday > 0 and matches_started is not None:
        current_pct = (matches_started / current_matchday) * 100 if current_matchday > 0 else 0
        
        if current_matchday >= 10:
            # Pure current season — enough data
            return min(round(current_pct), 100)
        else:
            # Blend with previous season
            prev_pct = (matches_started_prev / TOTAL_MATCHDAYS) * 100 if matches_started_prev else current_pct
            weight_current = current_matchday / 10
            weight_prev = 1 - weight_current
            blended = current_pct * weight_current + prev_pct * weight_prev
            return min(round(blended), 100)
    
    # Previous season data or season not started
    if matches_started:
        return min(round((matches_started / TOTAL_MATCHDAYS) * 100), 100)
    
    # Try prev field directly
    if matches_started_prev:
        return min(round((matches_started_prev / TOTAL_MATCHDAYS) * 100), 100)
    
    return None


def get_current_matchday(db, championship_id: str) -> int:
    """Get the current matchday from team_standings.
    
    Returns 0 if season hasn't started.
    """
    try:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "SELECT MAX(matchday) FROM team_standings WHERE championship_id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            row = cursor.fetchone()
            return row[0] or 0 if row else 0
    except Exception:
        return 0


def build_sofascore_map(db, championship_id: str = None) -> dict:
    """Build sofascore lookup map from cache with proper starter_pct calculation.
    
    Returns dict keyed by lowercase player_name with rating, url, starter_pct.
    """
    current_matchday = get_current_matchday(db, championship_id) if championship_id else 0
    
    sofascore_map = {}
    try:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "SELECT player_name, rating, sofascore_url, matches_started, season, matches_started_prev FROM sofascore_cache"
            cursor.execute(sql)
            for row in cursor.fetchall():
                player_name = row[0]
                matches_started = row[3] or 0
                season_name = row[4] or ""
                matches_started_prev = row[5] or 0
                starter_pct = calculate_starter_pct(matches_started, season_name, current_matchday, matches_started_prev)
                sofascore_map[player_name.lower()] = {
                    "rating": row[1],
                    "url": row[2],
                    "starter_pct": starter_pct,
                }
    except Exception:
        pass
    
    return sofascore_map
