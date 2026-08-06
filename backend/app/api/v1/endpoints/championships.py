"""Championships endpoint — legacy, redirects to user championships."""

import json
from fastapi import APIRouter, HTTPException, Request
from app.services.db_connection import get_db

router = APIRouter()


@router.get("/championships")
async def get_championships(request: Request):
    """Devuelve la lista de campeonatos del usuario autenticado."""
    try:
        user = getattr(request.state, "user", None)
        if not user:
            return {"success": True, "championships": []}
        
        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "SELECT championship_id, name, has_clauses, initial_budget, excluded_teams FROM user_championships WHERE user_id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (user["user_id"],))
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
