"""Favorites endpoint — shows user's favorited free-agent players with stats."""

from fastapi import APIRouter, Query, Request, HTTPException
from typing import Dict
from app.core.config import CHAMPIONSHIP_ID
from app.api.v1.endpoints._helpers import get_user_futmondo_client
from app.services.db_connection import get_db

router = APIRouter()


@router.get("/my")
async def get_my_favorites(
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
) -> Dict:
    """Get the user's favorited players (free agents only) with Sofascore enrichment.
    
    Returns players from the player_favorites table, enriched with current
    value/stats from the championship players data and Sofascore cache.
    """
    try:
        client = get_user_futmondo_client(request)
        user_id = client.user_id
        
        db = get_db()
        
        # Get favorite player IDs from DB
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "SELECT player_id FROM player_favorites WHERE championship_id = ? AND user_id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (championship_id, user_id))
            fav_ids = {row[0] for row in cursor.fetchall()}
        
        if not fav_ids:
            return {"success": True, "players": [], "total": 0}
        
        # Get current player data from Futmondo API
        players_data = client.get_championship_players(championship_id)
        if not players_data or not players_data.get("players"):
            return {"success": True, "players": [], "total": 0}
        
        all_players = players_data["players"]
        
        # Filter: only favorites that are free agents (no userteamId)
        fav_players = [p for p in all_players if p.get("id") in fav_ids and not p.get("userteamId")]
        
        # Build team_map: teamId → {name, logo} from DB (players table) + user roster + static fallback
        # Static LaLiga team map as final fallback
        LALIGA_TEAMS = {
            "504e581e4d8bec9a670000c6": {"name": "Real Madrid", "logo": "real-madrid.png"},
            "504e581e4d8bec9a670000c7": {"name": "Barcelona", "logo": "barcelona.png"},
            "504e581e4d8bec9a670000c8": {"name": "Atlético de Madrid", "logo": "atletico-de-madrid.png"},
            "504e581e4d8bec9a670000c9": {"name": "Athletic de Bilbao", "logo": "athletic-de-bilbao.png"},
            "504e581e4d8bec9a670000ca": {"name": "Rayo Vallecano", "logo": "rayo-vallecano.png"},
            "504e581e4d8bec9a670000cb": {"name": "Valencia", "logo": "valencia.png"},
            "504e581e4d8bec9a670000cc": {"name": "Betis", "logo": "betis.png"},
            "504e581e4d8bec9a670000cd": {"name": "Getafe", "logo": "getafe.png"},
            "504e581e4d8bec9a670000ce": {"name": "Real Sociedad", "logo": "real-sociedad.png"},
            "504e581e4d8bec9a670000cf": {"name": "Levante", "logo": "levante.png"},
            "504e581e4d8bec9a670000d0": {"name": "Espanyol", "logo": "espanyol.png"},
            "504e581e4d8bec9a670000d1": {"name": "Osasuna", "logo": "osasuna.png"},
            "504e581e4d8bec9a670000d5": {"name": "Sevilla", "logo": "sevilla.png"},
            "504e581e4d8bec9a670000d6": {"name": "Málaga", "logo": "malaga.png"},
            "504e581e4d8bec9a670000d8": {"name": "Deportivo de la Coruña", "logo": "deportivo-de-la-coruna.png"},
            "504e581e4d8bec9a670000d9": {"name": "Celta de Vigo", "logo": "celta-de-vigo.png"},
            "51b889b1e401a15f2c0000f0": {"name": "Elche", "logo": "elche.png"},
            "51b890f5b986415a2c000012": {"name": "Villarreal", "logo": "villarreal.png"},
            "52038563b8d07d930b00008a": {"name": "Alavés", "logo": "deportivo-alaves.png"},
            "520e4ee4a776cc826b00004b": {"name": "Racing", "logo": "racing-santander.png"},
        }
        team_map = dict(LALIGA_TEAMS)
        
        # Complement with user's roster (more accurate, has all teams the user has players from)
        try:
            standings = client.get_matchday_standings(championship_id)
            if standings:
                teams_list = standings.get('teams', standings.get('ranking', []))
                user_team_id = None
                for t in teams_list:
                    if t.get('userid') == user_id:
                        user_team_id = t.get('teamid') or t.get('id')
                        break
                if user_team_id:
                    roster = client.get_userteam_roster(championship_id, user_team_id)
                    if roster:
                        for rp in roster:
                            tid = rp.get('teamId')
                            if tid and rp.get('team'):
                                team_map[tid] = {"name": rp["team"], "logo": rp.get("logo", "")}
        except Exception:
            pass
        
        # Enrich with Sofascore data from cache
        from app.api.v1.endpoints._sofascore_helpers import build_sofascore_map
        sofascore_map = build_sofascore_map(db, championship_id)
        
        # Build response
        position_order = {'portero': 0, 'defensa': 1, 'centrocampista': 2, 'delantero': 3}
        players = []
        
        for p in fav_players:
            player_name = p.get('name', '')
            sf = sofascore_map.get(player_name.lower(), {})
            
            avg_data = p.get('average', {})
            average = avg_data.get('average', 0) if isinstance(avg_data, dict) else 0
            home_avg = avg_data.get('homeAverage', None) if isinstance(avg_data, dict) else None
            away_avg = avg_data.get('awayAverage', None) if isinstance(avg_data, dict) else None
            matches = avg_data.get('matches', 0) if isinstance(avg_data, dict) else 0
            
            # Clean NaN
            if average == "NaN" or average is None:
                average = 0
            else:
                try:
                    average = float(average)
                except (ValueError, TypeError):
                    average = 0
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
            
            team_name = p.get('team') or ''
            team_logo = p.get('logo') or ''
            if not team_name:
                tid = p.get('teamId', '')
                if tid in team_map:
                    team_info = team_map[tid]
                    team_name = team_info.get('name', '')
                    team_logo = team_info.get('logo', '')
            
            players.append({
                "player_id": p.get('id'),
                "name": player_name,
                "slug": p.get('slug', ''),
                "position": p.get('role', ''),
                "position2": p.get('role2', ''),
                "team": team_name,
                "team_logo": team_logo,
                "value": p.get('value', 0),
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
        
        # Sort by position, then value descending
        players.sort(key=lambda x: (x['position_order'], -x['value']))
        
        return {"success": True, "players": players, "total": len(players)}
    
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))



@router.post("/unfollow")
async def unfollow_player(
    request: Request,
    championship_id: str = Query(...),
    player_id: str = Query(...),
) -> Dict:
    """Unmark a player as favorite in Futmondo and remove from local DB."""
    try:
        client = get_user_futmondo_client(request)
        
        # Call Futmondo API to unmark favorite
        request_data = {
            "header": {"token": client.token, "userid": client.user_id},
            "query": {"championshipId": championship_id, "playerId": player_id},
            "answer": {}
        }
        resp = client.session.post(
            f"{client.base_url}/5/championship/unmarkfavorite",
            json=request_data, timeout=15
        )
        
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Error al quitar favorito en Futmondo")
        
        result = resp.json()
        if result.get("answer", {}).get("code") != "api.general.ok":
            raise HTTPException(status_code=400, detail="Futmondo no pudo quitar el favorito")
        
        # Remove from local DB
        db = get_db()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            sql = "DELETE FROM player_favorites WHERE championship_id = ? AND user_id = ? AND player_id = ?"
            sql = db.adapt_params(sql)
            cursor.execute(sql, (championship_id, client.user_id, player_id))
        
        return {"success": True, "message": "Favorito eliminado"}
    
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
