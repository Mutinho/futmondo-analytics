"""My Roster endpoint — shows the current user's squad with stats."""

from fastapi import APIRouter, Query, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from app.core.config import CHAMPIONSHIP_ID
from app.api.v1.endpoints._helpers import get_user_futmondo_client
from app.services.db_connection import get_db

router = APIRouter()


class SellRequest(BaseModel):
    championship_id: str = CHAMPIONSHIP_ID
    player_ids: List[str]


@router.post("/sell")
async def sell_players(
    request: Request,
    body: SellRequest,
) -> Dict:
    """Put players on market at their current value, then hide them.
    
    For each player_id:
    1. Call /1/market/putonmarket with current market value as price
    2. Call /5/market/toggleplayer to hide from roster view
    """
    try:
        client = get_user_futmondo_client(request)
        championship_id = body.championship_id

        # Get user's team ID
        standings = client.get_matchday_standings(championship_id)
        if not standings:
            raise HTTPException(status_code=404, detail="No se pudo obtener el campeonato")

        teams_list = standings.get('teams', standings.get('ranking', []))
        user_team_id = None
        for team in teams_list:
            tid = team.get('teamid') or team.get('id')
            uid = team.get('userid') or team.get('user_id')
            if uid == client.user_id:
                user_team_id = tid
                break

        if not user_team_id:
            raise HTTPException(status_code=404, detail="No se encontró tu equipo en este campeonato")

        # Get roster to find current values
        roster = client.get_userteam_roster(championship_id, user_team_id)
        if not roster:
            raise HTTPException(status_code=404, detail="No se pudo obtener la plantilla")

        # Build player value map
        player_values = {}
        for p in roster:
            pid = p.get('id')
            if pid in body.player_ids:
                player_values[pid] = p.get('value', 0)

        results = []
        for player_id in body.player_ids:
            price = player_values.get(player_id)
            if price is None:
                results.append({"player_id": player_id, "success": False, "error": "Jugador no encontrado en plantilla"})
                continue

            # 1. Put on market
            put_data = {
                "header": {"token": client.token, "userid": client.user_id},
                "query": {
                    "championshipId": championship_id,
                    "userteamId": user_team_id,
                    "price": price,
                    "player_id": player_id,
                    "isClause": None,
                    "mode": None,
                    "toLoan": None,
                },
                "answer": {}
            }
            put_resp = client._make_request("/1/market/putonmarket", put_data)
            if not put_resp or put_resp.get("answer", {}).get("code") != "api.general.ok":
                error = put_resp.get("answer", {}).get("code", "Unknown error") if put_resp else "No response"
                results.append({"player_id": player_id, "success": False, "error": f"putonmarket: {error}"})
                continue

            # 2. Toggle (hide) player
            toggle_data = {
                "header": {"token": client.token, "userid": client.user_id},
                "query": {
                    "championshipId": championship_id,
                    "userteamId": user_team_id,
                    "player_id": player_id,
                },
                "answer": {}
            }
            toggle_resp = client._make_request("/5/market/toggleplayer", toggle_data)
            if not toggle_resp or toggle_resp.get("answer", {}).get("code") != "api.general.ok":
                # Put on market succeeded but toggle failed — still report partial success
                results.append({"player_id": player_id, "success": True, "warning": "En venta pero no se pudo ocultar"})
                continue

            results.append({"player_id": player_id, "success": True})

        success_count = sum(1 for r in results if r.get("success"))
        return {
            "success": True,
            "total": len(body.player_ids),
            "sold": success_count,
            "results": results,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/my")
async def get_my_roster(
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
) -> Dict:
    """Get the authenticated user's roster with Sofascore enrichment.
    
    Returns players sorted by position (GK → DEF → MID → FWD) with:
    - Futmondo data: value, points, averages, buyPrice, change
    - Sofascore data: rating (from cache)
    """
    try:
        client = get_user_futmondo_client(request)

        # Get user's team ID from standings
        standings = client.get_matchday_standings(championship_id)
        if not standings:
            raise HTTPException(status_code=404, detail="No se pudo obtener el campeonato")

        teams_list = standings.get('teams', standings.get('ranking', []))
        user_id_futmondo = client.user_id

        user_team_id = None
        for team in teams_list:
            tid = team.get('teamid') or team.get('id')
            uid = team.get('userid') or team.get('user_id')
            if uid == user_id_futmondo:
                user_team_id = tid
                break

        if not user_team_id:
            raise HTTPException(status_code=404, detail="No se encontró tu equipo en este campeonato")

        # Fetch roster from Futmondo API
        roster = client.get_userteam_roster(championship_id, user_team_id)
        if not roster:
            return {"success": True, "players": [], "summary": {}}

        # Enrich with Sofascore data from cache
        db = get_db()
        from app.api.v1.endpoints._sofascore_helpers import build_sofascore_map, lookup_sofascore
        sofascore_map = build_sofascore_map(db, championship_id)

        # Build response
        position_order = {'portero': 0, 'defensa': 1, 'centrocampista': 2, 'delantero': 3}
        players = []
        total_value = 0
        total_buy_price = 0

        for p in roster:
            value = p.get('value', 0)
            buy_price = p.get('buyPrice', 0)
            total_value += value
            total_buy_price += buy_price

            avg_data = p.get('average', {})
            average = avg_data.get('average', 0) if isinstance(avg_data, dict) else 0
            home_avg = avg_data.get('homeAverage', None) if isinstance(avg_data, dict) else None
            away_avg = avg_data.get('awayAverage', None) if isinstance(avg_data, dict) else None
            matches = avg_data.get('matches', 0) if isinstance(avg_data, dict) else 0

            # Clean up NaN strings
            if home_avg == "NaN" or home_avg is None:
                home_avg = None
            else:
                try:
                    home_avg = float(home_avg)
                except (ValueError, TypeError):
                    home_avg = None

            if away_avg == "NaN" or away_avg is None:
                away_avg = None
            else:
                try:
                    away_avg = float(away_avg)
                except (ValueError, TypeError):
                    away_avg = None

            if average == "NaN" or average is None:
                average = 0
            else:
                try:
                    average = float(average)
                except (ValueError, TypeError):
                    average = 0

            # Sofascore lookup
            player_name = p.get('name', '')
            player_team = p.get('team', '')
            sf = lookup_sofascore(sofascore_map, player_name, player_team)

            profit = value - buy_price

            players.append({
                "player_id": p.get('id'),
                "name": player_name,
                "slug": p.get('slug', ''),
                "position": p.get('role', ''),
                "position2": p.get('role2', ''),
                "team": p.get('team', ''),
                "team_logo": p.get('logo', ''),
                "value": value,
                "buy_price": buy_price,
                "profit": profit,
                "change": p.get('change', 0),
                "points": p.get('points', 0),
                "average": average,
                "home_average": home_avg,
                "away_average": away_avg,
                "matches": matches,
                "rating": p.get('rating', 0),
                "sofascore_rating": sf.get("rating"),
                "sofascore_url": sf.get("url"),
                "starter_pct": sf.get("starter_pct"),
                "status": p.get('status', ''),
                "position_order": position_order.get(p.get('role', '').lower(), 9),
            })

        # Sort: by position order, then by value descending
        players.sort(key=lambda x: (x['position_order'], -x['value']))

        # Summary stats
        summary = {
            "total_players": len(players),
            "total_value": total_value,
            "total_invested": total_buy_price,
            "total_profit": total_value - total_buy_price,
        }

        return {"success": True, "players": players, "summary": summary}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/on-sale")
async def get_players_on_sale(
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
) -> Dict:
    """Get players currently on sale by the user."""
    try:
        client = get_user_futmondo_client(request)

        # Get user's team ID
        standings = client.get_matchday_standings(championship_id)
        if not standings:
            raise HTTPException(status_code=404, detail="No se pudo obtener el campeonato")

        teams_list = standings.get('teams', standings.get('ranking', []))
        user_team_id = None
        for team in teams_list:
            tid = team.get('teamid') or team.get('id')
            uid = team.get('userid') or team.get('user_id')
            if uid == client.user_id:
                user_team_id = tid
                break

        if not user_team_id:
            raise HTTPException(status_code=404, detail="No se encontró tu equipo en este campeonato")

        # Call myplayers endpoint
        request_data = {
            "header": {"token": client.token, "userid": client.user_id},
            "query": {
                "championshipId": championship_id,
                "userteamId": user_team_id,
                "type": "market",
            },
            "answer": {}
        }
        resp = client._make_request("/1/market/myplayers", request_data)
        if not resp:
            return {"success": True, "players": []}

        answer = resp.get("answer", [])
        if not isinstance(answer, list):
            return {"success": True, "players": []}

        players = []
        for p in answer:
            players.append({
                "player_id": p.get("id"),
                "name": p.get("name", ""),
                "slug": p.get("slug", ""),
                "position": p.get("role", ""),
                "position2": p.get("role2", ""),
                "team": p.get("team", ""),
                "team_logo": p.get("logo", ""),
                "value": p.get("value", 0),
                "price": p.get("price", 0),
                "buy_price": p.get("buyPrice", 0),
                "change": p.get("change", 0),
                "points": p.get("points", 0),
                "expiration_date": p.get("expirationDate"),
                "bids": len(p.get("bids", [])),
                "hidden": p.get("hidden", False),
            })

        return {"success": True, "players": players}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class CancelSaleRequest(BaseModel):
    championship_id: str = CHAMPIONSHIP_ID
    player_id: str


@router.post("/cancel-sale")
async def cancel_sale(
    request: Request,
    body: CancelSaleRequest,
) -> Dict:
    """Cancel a player sale (remove from market).
    
    Calls /1/market/removefrommarket to cancel the sale.
    """
    try:
        client = get_user_futmondo_client(request)

        # Get user's team ID
        standings = client.get_matchday_standings(body.championship_id)
        if not standings:
            raise HTTPException(status_code=404, detail="No se pudo obtener el campeonato")

        teams_list = standings.get('teams', standings.get('ranking', []))
        user_team_id = None
        for team in teams_list:
            tid = team.get('teamid') or team.get('id')
            uid = team.get('userid') or team.get('user_id')
            if uid == client.user_id:
                user_team_id = tid
                break

        if not user_team_id:
            raise HTTPException(status_code=404, detail="No se encontró tu equipo en este campeonato")

        # Remove from market
        remove_data = {
            "header": {"token": client.token, "userid": client.user_id},
            "query": {
                "championshipId": body.championship_id,
                "userteamId": user_team_id,
                "player_id": body.player_id,
            },
            "answer": {}
        }
        resp = client._make_request("/1/market/cancelsell", remove_data)
        if not resp or resp.get("answer", {}).get("code") != "api.general.ok":
            error = resp.get("answer", {}).get("code", "Unknown") if resp else "No response"
            raise HTTPException(status_code=400, detail=f"No se pudo cancelar la venta: {error}")

        return {"success": True, "player_id": body.player_id}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
