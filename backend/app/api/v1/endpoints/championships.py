"""Championships config endpoint — lista campeonatos configurados."""

import json
from fastapi import APIRouter, HTTPException
from app.services.db_connection import DBConnection

router = APIRouter()


@router.get("/championships")
async def get_championships():
    """Devuelve la lista de campeonatos configurados con su metadata."""
    try:
        db = DBConnection()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute("SELECT championship_id, name, has_clauses, initial_budget, excluded_teams FROM championships_config")
            rows = cursor.fetchall()

            championships = []
            for row in rows:
                championships.append({
                    "championship_id": row[0],
                    "name": row[1],
                    "has_clauses": bool(row[2]),
                    "initial_budget": row[3],
                    "excluded_teams": json.loads(row[4]) if row[4] else [],
                })

            return {"success": True, "championships": championships}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
