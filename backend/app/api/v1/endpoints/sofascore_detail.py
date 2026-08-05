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
            SELECT player_name, championship_id, sofascore_id, sofascore_name,
                   team, rating, goals, assists, appearances, minutes_played,
                   yellow_cards, red_cards, tournament, season, position,
                   nationality, age, successful_dribbles, accurate_passes_pct,
                   shots_on_target, tackles, interceptions, clean_sheets, saves,
                   synced_at
            FROM sofascore_cache
            WHERE player_name = ? AND championship_id = ?
        """
        sql = db.adapt_params(sql)
        cursor.execute(sql, (player_name, championship_id))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"No se encontraron stats de Sofascore para '{player_name}'")

    return {
        "success": True,
        "player": {
            "player_name": row[0],
            "championship_id": row[1],
            "sofascore_id": row[2],
            "sofascore_name": row[3],
            "team": row[4],
            "rating": row[5],
            "goals": row[6],
            "assists": row[7],
            "appearances": row[8],
            "minutes_played": row[9],
            "yellow_cards": row[10],
            "red_cards": row[11],
            "tournament": row[12],
            "season": row[13],
            "position": row[14],
            "nationality": row[15],
            "age": row[16],
            "successful_dribbles": row[17],
            "accurate_passes_pct": row[18],
            "shots_on_target": row[19],
            "tackles": row[20],
            "interceptions": row[21],
            "clean_sheets": row[22],
            "saves": row[23],
            "synced_at": row[24],
        },
    }
