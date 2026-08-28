"""Market endpoint — jugadores del computer en mercado hoy + puja sugerida."""

import logging
from typing import Dict, List
from fastapi import APIRouter, Query, HTTPException, Request
from app.core.config import CHAMPIONSHIP_ID
from app.services.db_connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


from app.api.v1.endpoints._helpers import clean_float as _clean_avg


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
    """Calcula puja sugerida basándose en el % real de sobrepago histórico.
    
    Usa transacciones enriquecidas (con market_value_at_purchase) para calcular
    cuánto se sobrepuja de media respecto al valor de mercado del jugador.
    Fallback: si no hay datos enriquecidos, usa el método anterior (precio pagado en rango similar).
    """
    margin = 0.25  # ±25%
    min_value = int(player_value * (1 - margin))
    max_value = int(player_value * (1 + margin))
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # Método principal: usar transacciones con market_value_at_purchase para calcular % sobrepago real
        sql_enriched = """
            SELECT t.price, t.market_value_at_purchase
            FROM transactions t
            WHERE t.championship_id = ?
            AND t.seller_team_id = 'market_team'
            AND t.market_value_at_purchase IS NOT NULL
            AND t.market_value_at_purchase > 0
            AND t.market_value_at_purchase BETWEEN ? AND ?
            ORDER BY t.transaction_date DESC
            LIMIT 50
        """
        sql_enriched = db.adapt_params(sql_enriched)
        cursor.execute(sql_enriched, (championship_id, min_value, max_value))
        enriched_rows = cursor.fetchall()
        
        if enriched_rows and len(enriched_rows) >= 3:
            # Calculate real overpay % from enriched data
            overpay_ratios = []
            for price_paid, market_val in enriched_rows:
                if market_val > 0:
                    ratio = price_paid / market_val
                    overpay_ratios.append(ratio)
            
            if overpay_ratios:
                avg_ratio = sum(overpay_ratios) / len(overpay_ratios)
                suggested = int(player_value * avg_ratio)
                overpay_pct = (avg_ratio - 1) * 100
                confidence = "high" if len(overpay_ratios) >= 10 else "medium"
                
                return {
                    "suggested_bid": suggested,
                    "confidence": confidence,
                    "based_on": len(overpay_ratios),
                    "overpay_pct": round(max(overpay_pct, 0), 1),
                }
        
        # Fallback: buscar por precio pagado en rango similar (método anterior)
        sql_fallback = """
            SELECT t.price
            FROM transactions t
            WHERE t.championship_id = ?
            AND t.seller_team_id = 'market_team'
            AND t.price BETWEEN ? AND ?
            AND t.price > 0
            ORDER BY t.transaction_date DESC
            LIMIT 50
        """
        sql_fallback = db.adapt_params(sql_fallback)
        cursor.execute(sql_fallback, (championship_id, min_value, max_value))
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
    overpay_pct = ((suggested - player_value) / player_value) * 100 if player_value > 0 else 0
    
    confidence = "medium" if len(prices) >= 3 else "low"
    
    return {
        "suggested_bid": suggested,
        "confidence": confidence,
        "based_on": len(prices),
        "overpay_pct": round(max(overpay_pct, 0), 1),
    }


@router.post("/bid")
async def place_bid(
    request: Request,
    championship_id: str = Query(...),
    player_id: str = Query(...),
    player_slug: str = Query(...),
    price: int = Query(...),
    is_clause: bool = Query(default=False),
) -> Dict:
    """Realiza una puja por un jugador en el mercado de Futmondo."""
    try:
        from app.api.v1.endpoints._helpers import get_user_futmondo_client
        client = get_user_futmondo_client(request)

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
    request: Request,
    championship_id: str = Query(...),
    bid_id: str = Query(...),
) -> Dict:
    """Cancela una puja activa en el mercado de Futmondo."""
    try:
        from app.api.v1.endpoints._helpers import get_user_futmondo_client
        client = get_user_futmondo_client(request)

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
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
) -> Dict:
    """Devuelve los jugadores del computer disponibles hoy en el mercado con puja sugerida.
    
    Reads from market_today table (cached). Falls back to live API if no data today.
    """
    try:
        from app.api.v1.endpoints._helpers import get_user_futmondo_client, get_championship_config
        from app.api.v1.endpoints._sofascore_helpers import calculate_starter_pct, get_current_matchday
        from datetime import date
        import json as json_mod

        db = get_db()
        today = date.today().isoformat()
        client = get_user_futmondo_client(request)

        # Get user's team_id from DB (not API)
        user = getattr(request.state, "user", None)
        user_id = user.get("user_id", "") if user else ""
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            cursor.execute(db.adapt_params(
                "SELECT futmondo_team_id FROM user_championships WHERE user_id = ? AND championship_id = ?"
            ), (user_id, championship_id))
            row = cursor.fetchone()
            user_team_id = row[0] if row else ""

        if not user_team_id:
            # Fallback to API only if not in DB
            user_team_id = _get_user_team_id(client, championship_id)

        # Try reading from DB cache first
        all_players = []
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            try:
                cursor.execute(db.adapt_params(
                    "SELECT raw_json FROM market_today WHERE championship_id = ? AND market_date = ?"
                ), (championship_id, today))
                rows = cursor.fetchall()
                if rows:
                    all_players = [json_mod.loads(r[0]) for r in rows if r[0]]
            except Exception:
                pass  # Table might not exist or have the column

        # Fallback: fetch from API if no cached data
        if not all_players:
            if not user_team_id:
                return {"success": True, "players": [], "message": "No se pudo determinar el equipo"}

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

            if isinstance(answer, list):
                all_players = answer
            elif isinstance(answer, dict):
                all_players = answer.get('players', answer.get('market', []))
            else:
                all_players = []

            # Save to DB for next time
            if all_players:
                try:
                    from app.services.assistant_service import get_assistant_service
                    get_assistant_service()._save_market_to_db(championship_id, all_players)
                except Exception as e:
                    logger.debug(f"Failed to save market_today cache: {e}")

        # Filter computer players only
        computer_players = [p for p in all_players if p.get('computer') is True]

        # Calcular puja sugerida para cada jugador (batch: una sola query para todos)
        # Load ALL market transactions at once instead of 24 individual queries
        all_market_txns = []
        with db.get_connection() as conn_bids:
            cursor_bids = db.get_cursor(conn_bids)
            cursor_bids.execute(db.adapt_params("""
                SELECT price, market_value_at_purchase
                FROM transactions
                WHERE championship_id = ? AND seller_team_id = 'market_team'
                AND market_value_at_purchase IS NOT NULL AND market_value_at_purchase > 0
                ORDER BY transaction_date DESC
                LIMIT 200
            """), (championship_id,))
            all_market_txns = cursor_bids.fetchall()

        def _calc_bid_batch(player_value):
            """Calculate suggested bid using pre-loaded transactions."""
            margin = 0.25
            min_val = int(player_value * (1 - margin))
            max_val = int(player_value * (1 + margin))
            
            enriched = [(p, mv) for p, mv in all_market_txns if min_val <= mv <= max_val]
            
            if len(enriched) >= 3:
                ratios = [p / mv for p, mv in enriched if mv > 0]
                if ratios:
                    avg_ratio = sum(ratios) / len(ratios)
                    return {
                        "suggested_bid": int(player_value * avg_ratio),
                        "confidence": "high" if len(ratios) >= 10 else "medium",
                        "based_on": len(ratios),
                        "overpay_pct": round(max((avg_ratio - 1) * 100, 0), 1),
                    }
            
            # Fallback: simple 5%
            return {
                "suggested_bid": player_value,
                "confidence": "low",
                "based_on": 0,
                "overpay_pct": 0,
            }

        players_with_bid = []
        for p in computer_players:
            player_value = p.get('value', 0)
            market_price = p.get('price', player_value)
            bid_info = _calc_bid_batch(player_value)

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
                "team_logo": p.get('logo', ''),
                "position": p.get('role', ''),
                "position2": p.get('role2', ''),
                "value": player_value,
                "market_price": market_price,
                "change": p.get('change', 0),
                "current_bid": p.get('bid', {}).get('price', 0) if isinstance(p.get('bid'), dict) else 0,
                "current_bid_id": p.get('bid', {}).get('id', '') if isinstance(p.get('bid'), dict) else '',
                "average": p.get('average', {}).get('average', 0) if isinstance(p.get('average'), dict) else 0,
                "points": p.get('points', 0),
                "home_average": _clean_avg(p.get('average', {}).get('homeAverage') if isinstance(p.get('average'), dict) else None),
                "away_average": _clean_avg(p.get('average', {}).get('awayAverage') if isinstance(p.get('average'), dict) else None),
                "matches": p.get('average', {}).get('matches', 0) if isinstance(p.get('average'), dict) else 0,
                "photo": p.get('photo', ''),
                "expiration": p.get('expirationDate', ''),
                "suggested_bid": suggested,
                "bid_confidence": bid_info["confidence"],
                "bid_based_on": bid_info["based_on"],
                "overpay_pct": overpay_pct,
            })

        # Enriquecer con ratings de Sofascore
        current_matchday = get_current_matchday(db, championship_id)

        # Get user's favorites
        favorite_player_ids = set()
        try:
            with db.get_connection() as conn_fav:
                cursor_fav = db.get_cursor(conn_fav)
                sql_fav = db.adapt_params("SELECT player_id FROM player_favorites WHERE championship_id = ? AND user_id = ?")
                cursor_fav.execute(sql_fav, (championship_id, client.user_id))
                favorite_player_ids = {row[0] for row in cursor_fav.fetchall()}
        except Exception as e:
            logger.debug(f"Failed to fetch user favorites: {e}")

        with db.get_connection() as conn_sf:
            cursor_sf = db.get_cursor(conn_sf)
            cursor_sf.execute("SELECT player_name, sofascore_id, rating, goals, assists, appearances, sofascore_url, matches_started, season, matches_started_prev FROM sofascore_cache")
            sf_rows = cursor_sf.fetchall()

        sf_map = {}
        for row in sf_rows:
            matches_started = row[7] or 0
            season_name = row[8] or ""
            matches_started_prev = row[9] or 0
            starter_pct = calculate_starter_pct(matches_started, season_name, current_matchday, matches_started_prev)
            sf_map[row[0]] = {
                "sofascore_id": row[1],
                "sofascore_rating": row[2],
                "sofascore_goals": row[3],
                "sofascore_assists": row[4],
                "sofascore_appearances": row[5],
                "sofascore_url": row[6] or None,
                "starter_pct": starter_pct,
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
                player["sofascore_url"] = None
            player["is_favorite"] = player["player_id"] in favorite_player_ids

        # Sort by value desc
        players_with_bid.sort(key=lambda x: x['value'], reverse=True)

        # Active bids total (from all players, not just computer)
        active_bids_total = 0
        for p in all_players:
            bid = p.get('bid')
            if isinstance(bid, dict) and bid.get('price'):
                active_bids_total += bid['price']

        # User balance and team value (from DB, not API)
        user_team_value = 0
        with db.get_connection() as conn2:
            cursor2 = db.get_cursor(conn2)

            # Team value from latest standings
            cursor2.execute(db.adapt_params(
                "SELECT team_value FROM team_standings WHERE championship_id = ? AND team_id = ? ORDER BY matchday DESC LIMIT 1"
            ), (championship_id, user_team_id))
            tv_row = cursor2.fetchone()
            if tv_row and tv_row[0]:
                user_team_value = int(tv_row[0])
            else:
                # Fallback: sum player values
                cursor2.execute(db.adapt_params(
                    "SELECT COALESCE(SUM(p.value), 0) FROM player_championship_stats pcs JOIN players p ON pcs.player_id = p.player_id WHERE pcs.championship_id = ? AND pcs.owner_team_id = ?"
                ), (championship_id, user_team_id))
                user_team_value = int(cursor2.fetchone()[0] or 0)

            config = get_championship_config(championship_id, request)
            initial_budget = config["initial_budget"]

            sql_spent = db.adapt_params("SELECT COALESCE(SUM(price), 0) FROM transactions WHERE championship_id = ? AND buyer_team_id = ?")
            cursor2.execute(sql_spent, (championship_id, user_team_id))
            user_spent = int(cursor2.fetchone()[0] or 0)

            sql_income = db.adapt_params("SELECT COALESCE(SUM(price), 0) FROM transactions WHERE championship_id = ? AND seller_team_id = ?")
            cursor2.execute(sql_income, (championship_id, user_team_id))
            user_income = int(cursor2.fetchone()[0] or 0)

            # Prizes (same as budget page)
            sql_prizes = db.adapt_params("SELECT COALESCE(SUM(ranking_prize + mvp_prize + COALESCE(points_prize, 0) + COALESCE(dream_team_prize, 0)), 0) FROM team_prizes WHERE championship_id = ? AND team_id = ?")
            cursor2.execute(sql_prizes, (championship_id, user_team_id))
            user_prizes = int(cursor2.fetchone()[0] or 0)

        user_balance = initial_budget - user_spent + user_income + user_prizes
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
