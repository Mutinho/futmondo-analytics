"""Sofascore detail endpoint — todas las stats cacheadas de un jugador."""

from typing import Dict
from fastapi import APIRouter, Query, HTTPException
from app.core.config import CHAMPIONSHIP_ID
from app.services.db_connection import get_db

router = APIRouter()


@router.get("/player/{player_name}")
async def get_sofascore_player_detail(
    player_name: str,
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
) -> Dict:
    """Devuelve todas las estadísticas cacheadas de Sofascore para un jugador."""
    db = get_db()

    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        sql = """
            SELECT player_name, sofascore_id, sofascore_name,
                   team, rating, goals, assists, appearances, minutes_played,
                   yellow_cards, red_cards, tournament, season,
                   successful_dribbles, accurate_passes_pct,
                   shots_on_target, tackles, interceptions, clean_sheets, saves,
                   synced_at, matches_started
            FROM sofascore_cache
            WHERE player_name = ?
        """
        sql = db.adapt_params(sql)
        cursor.execute(sql, (player_name,))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"No se encontraron stats de Sofascore para '{player_name}'")

    appearances = row[7] or 0
    matches_started = row[21] or 0
    starter_pct = round((matches_started / 38) * 100) if matches_started else None

    return {
        "success": True,
        "player": {
            "player_name": row[0],
            "sofascore_id": row[1],
            "sofascore_name": row[2],
            "team": row[3],
            "rating": row[4],
            "goals": row[5],
            "assists": row[6],
            "appearances": appearances,
            "matches_started": matches_started,
            "starter_pct": starter_pct,
            "minutes_played": row[8],
            "yellow_cards": row[9],
            "red_cards": row[10],
            "tournament": row[11],
            "season": row[12],
            "successful_dribbles": row[13],
            "accurate_passes_pct": row[14],
            "shots_on_target": row[15],
            "tackles": row[16],
            "interceptions": row[17],
            "clean_sheets": row[18],
            "saves": row[19],
            "synced_at": row[20],
        },
    }
