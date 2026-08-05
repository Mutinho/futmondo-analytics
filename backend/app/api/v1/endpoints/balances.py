"""Balances endpoint - Muestra saldo actual de cada equipo y sus altas/bajas."""

from fastapi import APIRouter, Query, HTTPException
from app.core.config import CHAMPIONSHIP_ID
from app.services.db_connection import DBConnection

router = APIRouter()

INITIAL_BUDGET = 200_000_000  # Default fallback


def _get_championship_config(db, cursor, championship_id: str) -> dict:
    """Lee la config del campeonato de la DB."""
    sql = "SELECT initial_budget, excluded_teams FROM championships_config WHERE championship_id = ?"
    sql = db.adapt_params(sql)
    cursor.execute(sql, (championship_id,))
    row = cursor.fetchone()
    if row:
        import json
        return {
            "initial_budget": row[0],
            "excluded_teams": set(json.loads(row[1])) if row[1] else set(),
        }
    return {"initial_budget": INITIAL_BUDGET, "excluded_teams": set()}


@router.get("/balances")
async def get_balances(
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
):
    """Calcula el saldo actual de cada equipo (200M - compras + ventas).
    
    Devuelve por cada equipo:
    - balance: saldo actual
    - total_spent: total gastado en compras
    - total_income: total ingresado por ventas
    - purchases_count: número de compras
    - sales_count: número de ventas
    - team_value: valor actual de la plantilla
    - performance: rendimiento (teamValue + balance - initial_budget). Positivo = buenos fichajes.
    """
    try:
        db = DBConnection()
        
        # Obtener teamValue de la API de Futmondo (live)
        from app.services.futmondo_service import FutmondoService
        service = FutmondoService()
        if not service.client or not service.client.is_authenticated():
            service.login()
        
        team_values = {}
        standings = service.client.get_matchday_standings(championship_id)
        if standings:
            teams_list = standings.get('teams', standings.get('ranking', []))
            for t in teams_list:
                tid = t.get('teamid') or t.get('id')
                if tid:
                    team_values[tid] = t.get('teamValue', 0)
        
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # Leer config del campeonato
            config = _get_championship_config(db, cursor, championship_id)
            initial_budget = config["initial_budget"]
            excluded_teams = config["excluded_teams"]
            sql_purchases = """
                SELECT buyer_team_id as team_id, SUM(price) as total_spent, COUNT(*) as count
                FROM transactions
                WHERE championship_id = ? AND buyer_team_id != 'market_team'
                GROUP BY buyer_team_id
            """
            sql_purchases = db.adapt_params(sql_purchases)
            cursor.execute(sql_purchases, (championship_id,))
            purchases = {row[0]: {"total_spent": row[1], "count": row[2]} for row in cursor.fetchall()}
            
            # Ventas por equipo (cuando el equipo es seller y NO es market)
            sql_sales = """
                SELECT seller_team_id as team_id, SUM(price) as total_income, COUNT(*) as count
                FROM transactions
                WHERE championship_id = ? AND seller_team_id != 'market_team'
                GROUP BY seller_team_id
            """
            sql_sales = db.adapt_params(sql_sales)
            cursor.execute(sql_sales, (championship_id,))
            sales = {row[0]: {"total_income": row[1], "count": row[2]} for row in cursor.fetchall()}
            
            # Obtener nombres de equipos
            all_team_ids = set(list(purchases.keys()) + list(sales.keys()))
            teams_info = {}
            if all_team_ids:
                placeholders = ",".join(["?" for _ in all_team_ids])
                sql_teams = f"SELECT team_id, team_name FROM teams WHERE team_id IN ({placeholders})"
                sql_teams = db.adapt_params(sql_teams)
                cursor.execute(sql_teams, tuple(all_team_ids))
                teams_info = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Construir resultado
            result = []
            for team_id in all_team_ids:
                if team_id in excluded_teams:
                    continue
                    
                spent = purchases.get(team_id, {}).get("total_spent", 0)
                income = sales.get(team_id, {}).get("total_income", 0)
                balance = initial_budget - spent + income
                team_value = team_values.get(team_id, 0)
                # Rendimiento: valor de equipo - gasto neto (gastado - ingresado)
                # Si positivo = la plantilla vale más de lo que has gastado neto = buenos fichajes
                # Si negativo = has gastado más de lo que vale tu plantilla = sobrepujar
                net_spent = spent - income
                performance = team_value - net_spent
                
                result.append({
                    "team_id": team_id,
                    "team_name": teams_info.get(team_id, team_id),
                    "balance": balance,
                    "initial_budget": initial_budget,
                    "total_spent": spent,
                    "total_income": income,
                    "purchases_count": purchases.get(team_id, {}).get("count", 0),
                    "sales_count": sales.get(team_id, {}).get("count", 0),
                    "team_value": team_value,
                    "performance": performance,
                })
            
            # Ordenar por saldo descendente
            result.sort(key=lambda x: x["balance"], reverse=True)
            
            return {
                "success": True,
                "championship_id": championship_id,
                "initial_budget": initial_budget,
                "teams": result,
            }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/balances/{team_id}")
async def get_team_transactions(
    team_id: str,
    championship_id: str = Query(default=CHAMPIONSHIP_ID),
):
    """Detalle de altas (compras) y bajas (ventas) de un equipo específico."""
    try:
        db = DBConnection()
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # Nombre del equipo
            sql_name = "SELECT team_name FROM teams WHERE team_id = ?"
            sql_name = db.adapt_params(sql_name)
            cursor.execute(sql_name, (team_id,))
            row = cursor.fetchone()
            team_name = row[0] if row else team_id
            
            # Altas (compras): el equipo es buyer
            sql_purchases = """
                SELECT t.player_id, p.name as player_name, t.price, t.transaction_date,
                       ts.team_name as seller_name
                FROM transactions t
                LEFT JOIN players p ON t.player_id = p.player_id
                LEFT JOIN teams ts ON t.seller_team_id = ts.team_id
                WHERE t.championship_id = ? AND t.buyer_team_id = ?
                ORDER BY t.transaction_date DESC
            """
            sql_purchases = db.adapt_params(sql_purchases)
            cursor.execute(sql_purchases, (championship_id, team_id))
            purchases = []
            for row in cursor.fetchall():
                purchases.append({
                    "player_id": row[0],
                    "player_name": row[1] or "Desconocido",
                    "price": row[2],
                    "date": row[3],
                    "from": row[4] or "Mercado",
                })
            
            # Bajas (ventas): el equipo es seller
            sql_sales = """
                SELECT t.player_id, p.name as player_name, t.price, t.transaction_date,
                       tb.team_name as buyer_name
                FROM transactions t
                LEFT JOIN players p ON t.player_id = p.player_id
                LEFT JOIN teams tb ON t.buyer_team_id = tb.team_id
                WHERE t.championship_id = ? AND t.seller_team_id = ?
                ORDER BY t.transaction_date DESC
            """
            sql_sales = db.adapt_params(sql_sales)
            cursor.execute(sql_sales, (championship_id, team_id))
            sales = []
            for row in cursor.fetchall():
                sales.append({
                    "player_id": row[0],
                    "player_name": row[1] or "Desconocido",
                    "price": row[2],
                    "date": row[3],
                    "to": row[4] or "Mercado",
                })
            
            total_spent = sum(p["price"] for p in purchases)
            total_income = sum(s["price"] for s in sales)
            
            config = _get_championship_config(db, cursor, championship_id)
            initial_budget = config["initial_budget"]
            balance = initial_budget - total_spent + total_income
            
            return {
                "success": True,
                "team_id": team_id,
                "team_name": team_name,
                "balance": balance,
                "initial_budget": initial_budget,
                "total_spent": total_spent,
                "total_income": total_income,
                "purchases": purchases,
                "sales": sales,
            }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
