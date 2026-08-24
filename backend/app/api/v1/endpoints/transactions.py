"""Transactions history endpoint — all championship transactions with filters."""

from fastapi import APIRouter, Query, Request, HTTPException
from typing import Dict, Optional
from app.core.config import CHAMPIONSHIP_ID
from app.api.v1.endpoints._helpers import get_user_futmondo_client
from app.services.db_connection import get_db

router = APIRouter()


@router.get("/history")
async def get_transactions_history(
    request: Request,
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
    team_id: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
) -> Dict:
    """Get all transactions for a championship, grouped by date.
    
    Filters:
        team_id: filter by buyer or seller team
        date_from: ISO date string (YYYY-MM-DD)
        date_to: ISO date string (YYYY-MM-DD)
    
    Returns transactions split into purchases and sales per date.
    """
    try:
        db = get_db()
        
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # Build query with filters
            conditions = ["t.championship_id = ?"]
            params = [championship_id]
            
            if team_id:
                conditions.append("(t.buyer_team_id = ? OR t.seller_team_id = ?)")
                params.extend([team_id, team_id])
            
            if date_from:
                conditions.append("t.transaction_date >= ?")
                params.append(date_from)
            
            if date_to:
                conditions.append("t.transaction_date <= ?")
                params.append(date_to + "T23:59:59")
            
            where_clause = " AND ".join(conditions)
            
            sql = f"""
                SELECT 
                    t.transaction_id, t.player_id, t.buyer_team_id, t.seller_team_id,
                    t.price, t.transaction_date, t.market_value_at_purchase, t.matchday,
                    p.name as player_name, p.role as player_role, p.role2 as player_role2, p.slug as player_slug,
                    p.real_team_id, p.real_team_name,
                    buyer.team_name as buyer_name,
                    seller.team_name as seller_name,
                    t.bids_json
                FROM transactions t
                LEFT JOIN players p ON t.player_id = p.player_id
                LEFT JOIN teams buyer ON t.buyer_team_id = buyer.team_id
                LEFT JOIN teams seller ON t.seller_team_id = seller.team_id
                WHERE {where_clause}
                ORDER BY t.transaction_date DESC
            """
            sql = db.adapt_params(sql)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            
            # Get all teams for the filter dropdown
            sql_teams = """
                SELECT DISTINCT team_id, team_name FROM teams 
                WHERE team_id IN (
                    SELECT DISTINCT buyer_team_id FROM transactions WHERE championship_id = ? AND buyer_team_id != 'market_team'
                    UNION
                    SELECT DISTINCT seller_team_id FROM transactions WHERE championship_id = ? AND seller_team_id != 'market_team'
                )
                ORDER BY team_name
            """
            sql_teams = db.adapt_params(sql_teams)
            cursor.execute(sql_teams, (championship_id, championship_id))
            teams = [{"team_id": r[0], "team_name": r[1]} for r in cursor.fetchall()]
        
        # Enrich with Sofascore
        from app.api.v1.endpoints._sofascore_helpers import build_sofascore_map, lookup_sofascore
        sofascore_map = build_sofascore_map(db, championship_id)
        
        # LaLiga team map for resolving team names from IDs
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
        
        # Pre-fetch original buy prices for calculating sale profits
        buy_prices = {}  # (player_id, buyer_team_id) -> price
        try:
            with db.get_connection() as conn:
                cursor = db.get_cursor(conn)
                sql_buys = """
                    SELECT player_id, buyer_team_id, price 
                    FROM transactions 
                    WHERE championship_id = ? AND buyer_team_id != 'market_team'
                """
                sql_buys = db.adapt_params(sql_buys)
                cursor.execute(sql_buys, (championship_id,))
                for row in cursor.fetchall():
                    buy_prices[(row[0], row[1])] = row[2]
        except Exception:
            pass
        
        # Build response grouped by date
        from collections import defaultdict
        date_groups = defaultdict(lambda: {"purchases": [], "sales": []})
        
        for row in rows:
            txn_id, player_id, buyer_id, seller_id, price, txn_date, market_val, matchday, \
                player_name, player_role, player_role2, player_slug, real_team_id, real_team_name, \
                buyer_name, seller_name, bids_json = row
            
            # Format date as YYYY-MM-DD
            if txn_date:
                if hasattr(txn_date, 'strftime'):
                    date_key = txn_date.strftime('%Y-%m-%d')
                else:
                    date_key = str(txn_date)[:10]
            else:
                date_key = "Sin fecha"
            
            sf = lookup_sofascore(sofascore_map, player_name or '', resolved_team_name)
            
            # Resolve real team name/logo from ID
            team_info = LALIGA_TEAMS.get(real_team_id or '', {})
            resolved_team_name = real_team_name or team_info.get("name", "")
            resolved_team_logo = team_info.get("logo", "")
            
            overpay_pct = None
            if market_val and market_val > 0 and price:
                overpay_pct = round(((price - market_val) / market_val) * 100, 1)
            
            # Parse bids
            import json as _json
            bids = []
            if bids_json:
                try:
                    bids = _json.loads(bids_json)
                except Exception:
                    pass
            
            txn_data = {
                "transaction_id": txn_id,
                "player_id": player_id,
                "player_name": player_name or "?",
                "player_slug": player_slug or "",
                "player_role": player_role or "",
                "player_role2": player_role2 or "",
                "real_team_name": resolved_team_name,
                "real_team_logo": resolved_team_logo,
                "price": price,
                "market_value": market_val,
                "overpay_pct": overpay_pct,
                "sofascore_rating": sf.get("rating"),
                "sofascore_url": sf.get("url"),
                "starter_pct": sf.get("starter_pct"),
                "bids": bids,
            }
            
            # Categorize: purchase (someone bought) or sale (someone sold to market)
            if buyer_id and buyer_id != 'market_team':
                date_groups[date_key]["purchases"].append({
                    **txn_data,
                    "team_id": buyer_id,
                    "team_name": buyer_name or buyer_id,
                    "seller_name": seller_name if seller_id != 'market_team' else "Mercado",
                })
            
            if seller_id and seller_id != 'market_team':
                # Calculate profit: what they sold for vs what they originally paid
                original_buy_price = buy_prices.get((player_id, seller_id))
                sale_profit = (price - original_buy_price) if original_buy_price and price else None
                # Also calculate vs market value
                sale_vs_market = None
                if market_val and market_val > 0 and price:
                    sale_vs_market = round(((price - market_val) / market_val) * 100, 1)
                
                date_groups[date_key]["sales"].append({
                    **txn_data,
                    "team_id": seller_id,
                    "team_name": seller_name or seller_id,
                    "buyer_name": buyer_name if buyer_id != 'market_team' else "Mercado",
                    "original_buy_price": original_buy_price,
                    "sale_profit": sale_profit,
                    "sale_vs_market_pct": sale_vs_market,
                })
        
        # Convert to sorted list
        grouped = []
        for date_key in sorted(date_groups.keys(), reverse=True):
            grouped.append({
                "date": date_key,
                "purchases": date_groups[date_key]["purchases"],
                "sales": date_groups[date_key]["sales"],
            })
        
        return {
            "success": True,
            "championship_id": championship_id,
            "total_transactions": len(rows),
            "groups": grouped,
            "teams": teams,
        }
    
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
