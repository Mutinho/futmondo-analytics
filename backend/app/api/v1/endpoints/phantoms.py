"""Phantom players detection — finds players without registered purchase."""

import json
from typing import Dict, List
from fastapi import APIRouter, Query, Depends, HTTPException
from app.core.config import CHAMPIONSHIP_ID
from app.services.futmondo_service import FutmondoService
from app.services.futmondo_client import FutmondoClient
from app.services.db_connection import get_db

router = APIRouter()


def ensure_authenticated(service: FutmondoService) -> FutmondoService:
    if not service.client or not service.client.is_authenticated():
        service.login()
    return service


@router.post("/check-phantoms")
async def check_phantoms(
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: FutmondoService = Depends(FutmondoService),
) -> Dict:
    """Detecta jugadores fantasma (en plantilla o vendidos sin compra registrada).
    
    Returns:
        - roster_phantoms: jugadores en plantilla actual sin compra
        - sold_phantoms: jugadores vendidos por un equipo sin compra previa
    """
    try:
        service = ensure_authenticated(service)
        client = service.client
        
        # Obtener config del campeonato para excluded_teams
        db = get_db()
        excluded_teams = set()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "SELECT excluded_teams FROM championships_config WHERE championship_id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (championship_id,))
            row = cursor.fetchone()
            if row and row[0]:
                excluded_teams = set(json.loads(row[0]))
        
        # Obtener equipos
        standings = client.get_matchday_standings(championship_id)
        if not standings or standings.get('error'):
            return {"success": True, "roster_phantoms": [], "sold_phantoms": []}
        
        teams = standings.get('teams', standings.get('ranking', []))
        
        roster_phantoms: List[Dict] = []
        sold_phantoms: List[Dict] = []
        
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # === CASO 1: Jugadores en roster sin compra registrada ===
            for team in teams:
                team_id = team.get('teamid') or team.get('id')
                team_name = team.get('teamname') or team.get('name')
                
                if team_id in excluded_teams:
                    continue
                
                roster = client.get_userteam_roster(championship_id, team_id)
                if not roster:
                    continue
                
                # IDs comprados por este equipo
                sql = "SELECT DISTINCT player_id FROM transactions WHERE buyer_team_id = ? AND championship_id = ?"
                sql = db.adapt_params(sql)
                cursor.execute(sql, (team_id, championship_id))
                bought_ids = {row[0] for row in cursor.fetchall()}
                
                for p in roster:
                    pid = p.get('id')
                    if pid and pid not in bought_ids:
                        roster_phantoms.append({
                            "team_id": team_id,
                            "team_name": team_name,
                            "player_id": pid,
                            "player_name": p.get('name', '?'),
                            "value": p.get('value', 0),
                            "type": "roster",
                        })
            
            # === CASO 2: Jugadores vendidos sin compra previa ===
            excluded_str = ",".join(["?" for _ in excluded_teams]) if excluded_teams else "'__none__'"
            params = [championship_id, 'market_team'] + list(excluded_teams)
            
            sql = f"""
                SELECT 
                    t_sell.seller_team_id,
                    tm.team_name,
                    t_sell.player_id,
                    p.name,
                    t_sell.price,
                    t_sell.transaction_date
                FROM transactions t_sell
                LEFT JOIN players p ON t_sell.player_id = p.player_id
                LEFT JOIN teams tm ON t_sell.seller_team_id = tm.team_id
                WHERE t_sell.championship_id = ?
                AND t_sell.seller_team_id != ?
                AND t_sell.seller_team_id NOT IN ({excluded_str})
                AND NOT EXISTS (
                    SELECT 1 FROM transactions t_buy 
                    WHERE t_buy.player_id = t_sell.player_id 
                    AND t_buy.buyer_team_id = t_sell.seller_team_id
                    AND t_buy.championship_id = ?
                )
                ORDER BY tm.team_name
            """
            params.append(championship_id)
            sql = db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            
            for row in cursor.fetchall():
                sold_phantoms.append({
                    "team_id": row[0],
                    "team_name": row[1] or row[0],
                    "player_id": row[2],
                    "player_name": row[3] or '?',
                    "sell_price": row[4],
                    "sell_date": str(row[5])[:10] if row[5] else None,
                    "type": "sold",
                })
        
        return {
            "success": True,
            "championship_id": championship_id,
            "roster_phantoms": roster_phantoms,
            "sold_phantoms": sold_phantoms,
            "total_phantoms": len(roster_phantoms) + len(sold_phantoms),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
