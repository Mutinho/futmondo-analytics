"""Market endpoint — jugadores del computer en mercado hoy + puja sugerida."""

from typing import Dict, List
from fastapi import APIRouter, Query, Depends, HTTPException
from app.core.config import CHAMPIONSHIP_ID
from app.services.futmondo_service import FutmondoService
from app.services.db_connection import DBConnection

router = APIRouter()


def _get_championship_config_for_market(db, cursor, championship_id: str) -> dict:
    """Lee la config del campeonato."""
    import json as _json
    sql = "SELECT initial_budget FROM championships_config WHERE championship_id = ?"
    sql = db.adapt_params(sql)
    cursor.execute(sql, (championship_id,))
    row = cursor.fetchone()
    return {"initial_budget": row[0] if row else 200000000}


def _get_user_team_id(client, championship_id: str) -> str:
    """Obtiene el team_id del usuario autenticado en el campeonato."""
    standings = client.get_matchday_standings(championship_id)
    if not standings or standings.get('error'):
        return ""
    teams = standings.get('teams', standings.get('ranking', []))
    for t in teams:
        if t.get('userid') == client.user_id:
            return t.get('teamid') or t.get('id', '')
    # Fallback: usar el primer equipo
    return teams[0].get('teamid') or teams[0].get('id', '') if teams else ""


def _calculate_suggested_bid(player_value: int, championship_id: str, db) -> Dict:
    """Calcula puja sugerida basándose en cuánto se ha sobrepujado históricamente.
    
    Busca compras al mercado (seller = market_team) de jugadores con valor similar (±25%)
    y calcula el % medio de sobrepuja respecto al valor del jugador.
    Ejemplo: si jugadores de ~20M se han comprado de media por 22M → sobrepuja media = 10%
    → para un jugador de 20M sugiere 22M.
    """
    margin = 0.25  # ±25%
    min_value = int(player_value * (1 - margin))
    max_value = int(player_value * (1 + margin))
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # Buscar transacciones del mercado con precio pagado en rango similar al valor del jugador
        # Esto nos da "cuánto se pagó por jugadores de este rango de precio"
        sql = """
            SELECT t.price
            FROM transactions t
            WHERE t.championship_id = ?
            AND t.seller_team_id = 'market_team'
            AND t.price BETWEEN ? AND ?
            AND t.price > 0
            ORDER BY t.transaction_date DESC
            LIMIT 50
        """
        sql = db.adapt_params(sql)
        cursor.execute(sql, (championship_id, min_value, max_value))
        prices = [row[0] for row in cursor.fetchall()]
    
    if not prices:
        # Sin historial, sugiere el valor del jugador (puja mínima)
        return {
            "suggested_bid": player_value,
            "confidence": "low",
            "based_on": 0,
            "overpay_pct": 0,
        }
    
    # Media de lo pagado en transacciones similares
    avg_price = sum(prices) / len(prices)
    suggested = int(avg_price)
    # % que supone la puja sugerida respecto al valor del jugador
    overpay_pct = ((suggested - player_value) / player_value) * 100 if player_value > 0 else 0
    
    confidence = "high" if len(prices) >= 10 else "medium" if len(prices) >= 3 else "low"
    
    return {
        "suggested_bid": suggested,
        "confidence": confidence,
        "based_on": len(prices),
        "overpay_pct": round(max(overpay_pct, 0), 1),
    }


@router.post("/bid")
async def place_bid(
    championship_id: str = Query(...),
    player_id: str = Query(...),
    player_slug: str = Query(...),
    price: int = Query(...),
    is_clause: bool = Query(default=False),
    service: FutmondoService = Depends(FutmondoService),
) -> Dict:
    """Realiza una puja por un jugador en el mercado de Futmondo."""
    try:
        if not service.client or not service.client.is_authenticated():
            service.login()
        client = service.client

        user_team_id = _get_user_team_id(client, championship_id)
        if not user_team_id:
            raise HTTPException(status_code=400, detail="No se pudo determinar tu equipo")

        bid_data = {
            "header": {
                "token": client.token,
                "userid": client.user_id,
            },
            "query": {
                "championshipId": championship_id,
                "userteamId": user_team_id,
                "player_slug": player_slug,
                "player_id": player_id,
                "price": price,
                "isClause": is_clause,
            },
            "answer": {}
        }

        resp = client.session.post(f"{client.base_url}/1/market/bid", json=bid_data, timeout=15)
        result = resp.json()
        answer = result.get("answer", {})

        if answer.get("code") == "api.general.ok":
            return {
                "success": True,
                "message": f"Puja de {price:,}€ realizada correctamente",
                "player_id": player_id,
                "price": price,
            }
        else:
            return {
                "success": False,
                "message": answer.get("code", "Error desconocido"),
                "detail": answer,
            }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/cancelbid")
async def cancel_bid(
    championship_id: str = Query(...),
    bid_id: str = Query(...),
    service: FutmondoService = Depends(FutmondoService),
) -> Dict:
    """Cancela una puja activa en el mercado de Futmondo."""
    try:
        if not service.client or not service.client.is_authenticated():
            service.login()
        client = service.client

        user_team_id = _get_user_team_id(client, championship_id)
        if not user_team_id:
            raise HTTPException(status_code=400, detail="No se pudo determinar tu equipo")

        cancel_data = {
            "header": {
                "token": client.token,
                "userid": client.user_id,
            },
            "query": {
                "championshipId": championship_id,
                "userteamId": user_team_id,
                "bid": bid_id,
            },
            "answer": {}
        }

        resp = client.session.post(f"{client.base_url}/1/market/cancelbid", json=cancel_data, timeout=15)
        result = resp.json()
        answer = result.get("answer", {})

        if answer.get("code") == "api.general.ok":
            return {"success": True, "message": "Puja cancelada correctamente"}
        else:
            return {"success": False, "message": answer.get("code", "Error desconocido")}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/today")
async def get_market_today(
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    service: FutmondoService = Depends(FutmondoService),
) -> Dict:
    """Devuelve los jugadores del computer disponibles hoy en el mercado con puja sugerida."""
    try:
        # Autenticar
        if not service.client or not service.client.is_authenticated():
            service.login()
        client = service.client
        
        # Obtener team_id del usuario para el request
        user_team_id = _get_user_team_id(client, championship_id)
        if not user_team_id:
            return {"success": True, "players": [], "message": "No se pudo determinar el equipo"}
        
        # Obtener jugadores en mercado
        data = {
            'header': {'token': client.token, 'userid': client.user_id},
            'query': {'championshipId': championship_id, 'userteamId': user_team_id},
            'answer': {}
        }
        resp = client.session.post(f'{client.base_url}/1/market/players', json=data, timeout=15)
        if resp.status_code != 200:
            return {"success": False, "players": [], "error": "API error"}
        
        result = resp.json()
        answer = result.get('answer', {})
        
        if isinstance(answer, dict) and answer.get('error'):
            return {"success": False, "players": [], "error": answer.get('code', 'Unknown')}
        
        # Extraer lista de jugadores
        if isinstance(answer, list):
            all_players = answer
        elif isinstance(answer, dict):
            all_players = answer.get('players', answer.get('market', []))
        else:
            all_players = []
        
        # Filtrar solo jugadores del computer
        computer_players = [p for p in all_players if p.get('computer') is True]
        
        # Calcular puja sugerida para cada jugador
        db = DBConnection()
        players_with_bid = []
        for p in computer_players:
            player_value = p.get('value', 0)
            market_price = p.get('price', player_value)
            bid_info = _calculate_suggested_bid(player_value, championship_id, db)
            
            # La puja nunca puede ser inferior al precio de mercado
            # Si la sugerencia basada en historial es menor, añadir un 5% sobre mercado como seguridad
            if bid_info["suggested_bid"] <= market_price:
                suggested = int(market_price * 1.05)
                overpay_pct = 5.0
            else:
                suggested = bid_info["suggested_bid"]
                overpay_pct = bid_info["overpay_pct"]
            
            players_with_bid.append({
                "player_id": p.get('id', ''),
                "slug": p.get('slug', ''),
                "name": p.get('name', ''),
                "team": p.get('team', ''),
                "position": p.get('role', ''),
                "position2": p.get('role2', ''),
                "value": player_value,
                "market_price": market_price,
                "change": p.get('change', 0),
                "current_bid": p.get('bid', {}).get('price', 0) if isinstance(p.get('bid'), dict) else 0,
                "current_bid_id": p.get('bid', {}).get('id', '') if isinstance(p.get('bid'), dict) else '',
                "average": p.get('average', {}).get('average', 0) if isinstance(p.get('average'), dict) else 0,
                "photo": p.get('photo', ''),
                "expiration": p.get('expirationDate', ''),
                "suggested_bid": suggested,
                "bid_confidence": bid_info["confidence"],
                "bid_based_on": bid_info["based_on"],
                "overpay_pct": overpay_pct,
            })
        
        # Enriquecer con ratings de Sofascore desde caché
        with db.get_connection() as conn_sf:
            cursor_sf = db.get_cursor(conn_sf)
            sql_sf = """
                SELECT player_name, sofascore_id, rating, goals, assists, appearances
                FROM sofascore_cache
                WHERE championship_id = ?
            """
            sql_sf = db.adapt_params(sql_sf)
            cursor_sf.execute(sql_sf, (championship_id,))
            sf_rows = cursor_sf.fetchall()

        sf_map = {}
        for row in sf_rows:
            sf_map[row[0]] = {
                "sofascore_id": row[1],
                "sofascore_rating": row[2],
                "sofascore_goals": row[3],
                "sofascore_assists": row[4],
                "sofascore_appearances": row[5],
            }

        for player in players_with_bid:
            sf_data = sf_map.get(player["name"])
            if sf_data:
                player.update(sf_data)
            else:
                player["sofascore_id"] = None
                player["sofascore_rating"] = None
                player["sofascore_goals"] = None
                player["sofascore_assists"] = None
                player["sofascore_appearances"] = None

        # Ordenar por valor descendente
        players_with_bid.sort(key=lambda x: x['value'], reverse=True)
        
        # Calcular pujas activas del usuario (todas las pujas, no solo computer)
        active_bids_total = 0
        for p in all_players:
            bid = p.get('bid')
            if isinstance(bid, dict) and bid.get('price'):
                active_bids_total += bid['price']
        
        # Obtener saldo y valor de equipo del usuario para calcular puja máxima
        standings = client.get_matchday_standings(championship_id)
        user_team_value = 0
        if standings and not standings.get('error'):
            for t in standings.get('teams', []):
                if t.get('userid') == client.user_id:
                    user_team_value = t.get('teamValue', 0)
                    break
        
        # Calcular saldo del usuario
        with db.get_connection() as conn2:
            cursor2 = db.get_cursor(conn2)
            config = _get_championship_config_for_market(db, cursor2, championship_id)
            initial_budget = config["initial_budget"]
            
            sql_spent = "SELECT COALESCE(SUM(price), 0) FROM transactions WHERE championship_id = ? AND buyer_team_id = ?"
            sql_spent = db.adapt_params(sql_spent)
            cursor2.execute(sql_spent, (championship_id, user_team_id))
            user_spent = cursor2.fetchone()[0]
            
            sql_income = "SELECT COALESCE(SUM(price), 0) FROM transactions WHERE championship_id = ? AND seller_team_id = ?"
            sql_income = db.adapt_params(sql_income)
            cursor2.execute(sql_income, (championship_id, user_team_id))
            user_income = cursor2.fetchone()[0]
        
        user_balance = initial_budget - user_spent + user_income
        user_max_bid = user_balance + int(user_team_value * 0.5)
        
        return {
            "success": True,
            "championship_id": championship_id,
            "total_in_market": len(all_players),
            "computer_players": len(players_with_bid),
            "players": players_with_bid,
            "user_info": {
                "balance": user_balance,
                "team_value": user_team_value,
                "max_bid": user_max_bid,
                "active_bids_total": active_bids_total,
                "available_for_bids": user_max_bid - active_bids_total,
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
