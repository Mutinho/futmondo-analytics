#!/usr/bin/env python3
"""
Script para obtener y validar datos de finanzas de usuarios
Obtiene dream teams, MVPs y rosters de usuarios para cada round
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.futmondo_client import FutmondoClient
from app.services.data_manager_v2 import DataManagerV2
from app.core.config import FUTMONDO_EMAIL, FUTMONDO_PASSWORD, CHAMPIONSHIP_ID, LEAGUE_ID
import time
import json

# Constants
POINTS_TO_EUROS = 40000  # 40,000 euros por punto
IDEAL_TEAM_BONUS = 300000  # 300,000 euros por jugador en dream team
MVP_BONUS = 800000  # 500,000 euros por tener al MVP
INITIAL_BUDGET = 270000000  # 270 millones de presupuesto inicial


def main():
    """Main function to fetch and validate user finances data"""
    print("=" * 80)
    print("Script de Obtención de Datos de Finanzas de Usuarios")
    print("=" * 80)
    
    # Initialize client
    client = FutmondoClient(FUTMONDO_EMAIL, FUTMONDO_PASSWORD)
    
    # Login
    print("\n1. Autenticando...")
    if not client.login():
        print("❌ Error: No se pudo autenticar")
        return
    print("✅ Autenticación exitosa")
    
    # Get league list
    print("\n2. Obteniendo lista de ligas y rounds...")
    leagues = client.get_league_list()
    if not leagues:
        print("❌ Error: No se pudo obtener la lista de ligas")
        return
    
    print(f"✅ Se obtuvieron {len(leagues)} ligas")
    
    # Debug: Show available leagues
    print("\n   Ligas disponibles:")
    for idx, league in enumerate(leagues[:5], 1):  # Show first 5
        league_id = league.get("_id") or league.get("id") or league.get("championshipId")
        league_name = league.get("name", "Unknown")
        print(f"   {idx}. ID: {league_id}, Nombre: {league_name}")
        if idx == 1 and len(leagues) > 1:
            print(f"      (mostrando 5 de {len(leagues)} ligas)")
    
    # Find target championship - try multiple possible field names
    target_league = None
    for league in leagues:
        # Try different possible field names for the ID
        league_id = (
            league.get("_id") or 
            league.get("id") or 
            league.get("championshipId") or
            league.get("championship_id")
        )
        if league_id == LEAGUE_ID:
            target_league = league
            break
    
    if not target_league:
        print(f"\n❌ Error: No se encontró el campeonato {CHAMPIONSHIP_ID}")
        print(f"   Buscando en todas las ligas...")
        # Try to find by partial match or show all IDs
        all_ids = []
        for league in leagues:
            league_id = (
                league.get("_id") or 
                league.get("id") or 
                league.get("championshipId") or
                league.get("championship_id")
            )
            if league_id:
                all_ids.append(f"  - {league_id} ({league.get('name', 'Unknown')})")
        
        if all_ids:
            print(f"   IDs encontrados en las ligas:")
            for id_info in all_ids[:10]:  # Show first 10
                print(id_info)
        return
    
    print(f"✅ Campeonato encontrado: {target_league.get('name', 'Unknown')}")
    
    # Get closed rounds
    rounds = target_league.get("rounds", [])
    closed_rounds = [r for r in rounds if r.get("status") == "closed"]
    print(f"✅ Encontrados {len(closed_rounds)} rounds cerrados")
    
    # Get all teams
    print("\n3. Obteniendo todos los equipos del campeonato...")
    standings = client.get_matchday_standings(CHAMPIONSHIP_ID)
    if not standings:
        print("❌ Error: No se pudieron obtener los standings")
        return
    
    teams = standings.get("teams", [])
    print(f"✅ Encontrados {len(teams)} equipos")
    
    # Get user data from database
    print("\n4. Obteniendo datos de usuarios desde la base de datos...")
    dm = DataManagerV2()
    
    # Get all users with points
    users_data = dm.get_all_users_with_points(CHAMPIONSHIP_ID)
    print(f"✅ Encontrados {len(users_data)} usuarios en la base de datos")
    
    # If no users in database, get them from API and save
    if len(users_data) == 0:
        print("\n⚠️  No hay usuarios en la base de datos. Obteniendo desde la API...")
        
        # Get standings from API
        standings = client.get_matchday_standings(CHAMPIONSHIP_ID)
        if standings and standings.get("teams"):
            api_teams = standings.get("teams", [])
            print(f"   ✅ Encontrados {len(api_teams)} equipos en la API")
            
            # Save teams and standings to database
            saved_count = 0
            for team in api_teams:
                team_id = team.get("id", team.get("teamid", ""))
                team_name = team.get("name", team.get("teamname", "Unknown"))
                points = team.get("points", 0)
                position = team.get("position", 0)
                team_value = team.get("value", 0)
                
                if team_id:
                    try:
                        # Save team
                        dm.save_team(team_id, team_name, user_id=team_id)
                        
                        # Save current standing (using matchday 1 as placeholder, will be updated later)
                        current_matchday = 1  # Default
                        dm.save_team_standing(
                            CHAMPIONSHIP_ID, team_id, current_matchday,
                            position, points, points_this_matchday=0,
                            team_value=team_value
                        )
                        saved_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Error guardando equipo {team_name}: {e}")
            
            print(f"   ✅ Guardados {saved_count} equipos en la base de datos")
            
            # Re-fetch users from database
            users_data = dm.get_all_users_with_points(CHAMPIONSHIP_ID)
            print(f"   ✅ Usuarios en BD después de guardar: {len(users_data)}")
    
    # Get user transactions
    user_transactions = dm.get_user_transactions(CHAMPIONSHIP_ID)
    print(f"✅ Encontradas transacciones para {len(user_transactions)} usuarios")
    
    # If no transactions, fetch them from API using pressroom
    if len(user_transactions) == 0:
        print("\n⚠️  No hay transacciones en la base de datos. Obteniendo desde la API (pressroom)...")
        print("   Esto puede tardar varios minutos...")
        
        # Fetch all transactions from pressroom with pagination
        all_transactions = []
        seen_transaction_ids = set()  # Track IDs to avoid duplicates
        from_id = ""  # Empty string for first page
        page_count = 0
        
        while True:
            try:
                page_count += 1
                print(f"   Obteniendo página {page_count}...", end=" ")
                
                pressroom_data = client.get_pressroom_news(CHAMPIONSHIP_ID, from_id=from_id)
                
                if not pressroom_data or "news" not in pressroom_data:
                    print("No hay más transacciones")
                    break
                
                transactions = pressroom_data.get("news", [])
                if not transactions:
                    print("No hay más transacciones")
                    break
                
                # Filter out duplicates based on transaction _id
                new_transactions = []
                duplicates_count = 0
                for transaction in transactions:
                    transaction_id = transaction.get("_id")
                    if transaction_id and transaction_id not in seen_transaction_ids:
                        seen_transaction_ids.add(transaction_id)
                        new_transactions.append(transaction)
                    elif transaction_id:
                        duplicates_count += 1
                
                if duplicates_count > 0:
                    print(f"⚠️  {duplicates_count} duplicados ignorados, ", end="")
                
                all_transactions.extend(new_transactions)
                print(f"✅ {len(new_transactions)} transacciones nuevas")
                
                # If no new transactions, we've reached the end
                if len(new_transactions) == 0:
                    print("   No hay más transacciones nuevas")
                    break
                
                # Save this batch (only new transactions)
                dm.save_pressroom_transactions(CHAMPIONSHIP_ID, new_transactions)
                
                # Get last transaction ID for pagination
                last_transaction = transactions[-1]
                from_id = last_transaction.get("_id")
                
                # Small delay to avoid rate limiting
                time.sleep(0.3)
                
                # Limit to prevent infinite loops (safety)
                if page_count >= 1000:
                    print("   ⚠️  Límite de páginas alcanzado (1000)")
                    break
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        print(f"\n   ✅ Total transacciones obtenidas: {len(all_transactions)}")
        print(f"   ✅ Páginas procesadas: {page_count}")
        
        # Re-fetch transactions from database
        user_transactions = dm.get_user_transactions(CHAMPIONSHIP_ID)
        print(f"   ✅ Transacciones en BD después de obtener: {len(user_transactions)} usuarios")
    
    # Get punishments and bonuses
    print("\n5.5. Obteniendo castigos y bonos...")
    user_punishments_bonuses = dm.get_user_punishments_bonuses(CHAMPIONSHIP_ID)
    print(f"✅ Encontrados castigos/bonos para {len(user_punishments_bonuses)} usuarios")
    
    # If no punishments/bonuses, fetch them from API
    if len(user_punishments_bonuses) == 0:
        print("\n⚠️  No hay castigos/bonos en la base de datos. Obteniendo desde la API (locker news)...")
        print("   Esto puede tardar varios minutos...")
        
        # Fetch all locker news with pagination
        from_id = ""  # Empty string for first page
        page_count = 0
        total_news = 0
        
        while True:
            try:
                page_count += 1
                print(f"   Obteniendo página {page_count}...", end=" ")
                
                locker_news_data = client.get_locker_news(CHAMPIONSHIP_ID, from_id=from_id)
                
                if not locker_news_data:
                    print("No hay más noticias")
                    break
                
                # The response might have 'news' or 'data' array
                news_items = locker_news_data.get("news", locker_news_data.get("data", []))
                if not news_items:
                    print("No hay más noticias")
                    break
                
                # Filter only punish and bonus items and remove duplicates
                seen_news_ids = set()
                punish_bonus_items = []
                for item in news_items:
                    if item.get("styp") in ["punish", "bonus"]:
                        news_id = item.get("_id")
                        if news_id and news_id not in seen_news_ids:
                            seen_news_ids.add(news_id)
                            punish_bonus_items.append(item)
                
                total_news += len(punish_bonus_items)
                
                print(f"✅ {len(news_items)} noticias ({len(punish_bonus_items)} castigos/bonos)")
                
                # Save this batch
                if punish_bonus_items:
                    dm.save_punishments_bonuses(CHAMPIONSHIP_ID, punish_bonus_items)
                
                # Get last news ID for pagination
                last_news = news_items[-1]
                from_id = last_news.get("_id")
                
                # Small delay to avoid rate limiting
                time.sleep(0.3)
                
                # Limit to prevent infinite loops (safety)
                if page_count >= 1000:
                    print("   ⚠️  Límite de páginas alcanzado (1000)")
                    break
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        print(f"\n   ✅ Total castigos/bonos obtenidos: {total_news}")
        print(f"   ✅ Páginas procesadas: {page_count}")
        
        # Re-fetch punishments/bonuses from database
        user_punishments_bonuses = dm.get_user_punishments_bonuses(CHAMPIONSHIP_ID)
        print(f"   ✅ Castigos/bonos en BD después de obtener: {len(user_punishments_bonuses)} usuarios")
    
    # Create a mapping of userteam_id to user data
    users_by_team_id = {}
    for user in users_data:
        userteam_id = user.get("team_id")
        if userteam_id:
            users_by_team_id[userteam_id] = user
    
    # Statistics
    stats = {
        "total_rounds": len(closed_rounds),
        "total_teams": len(teams),
        "dream_teams_fetched": 0,
        "rosters_fetched": 0,
        "dream_team_players": set(),
        "mvp_players": set(),
        "user_bonuses": {}  # userteam_id -> {ideal_team_count: int, mvp_count: int}
    }
    
    # Process each closed round
    print("\n5. Procesando rounds cerrados...")
    for idx, round_data in enumerate(closed_rounds, 1):
        round_id = round_data.get("_id")
        print(f"\n   Round {idx}/{len(closed_rounds)}: {round_id}")
        
        # Get dream team for this round
        print(f"   - Obteniendo dream team...")
        dream_team_data = client.get_dream_team(CHAMPIONSHIP_ID, round_id=round_id)
        time.sleep(0.1)  # Small delay to avoid rate limiting
        
        if not dream_team_data:
            print(f"   ⚠️  No se pudo obtener dream team para round {round_id}")
            continue
        
        stats["dream_teams_fetched"] += 1
        
        # Extract dream team players and MVP
        dream_team_players = set()
        players = dream_team_data.get("players", [])
        for player in players:
            player_id = player.get("id")
            if player_id:
                dream_team_players.add(player_id)
                stats["dream_team_players"].add(player_id)
        
        mvp_id = dream_team_data.get("mvp")
        if mvp_id:
            stats["mvp_players"].add(mvp_id)
        
        print(f"   ✅ Dream team: {len(dream_team_players)} jugadores, MVP: {mvp_id if mvp_id else 'N/A'}")
        
        # Get roster for each team
        print(f"   - Obteniendo rosters de {len(teams)} equipos...")
        for team_idx, team in enumerate(teams, 1):
            userteam_id = team.get("id", team.get("teamid", ""))
            if not userteam_id:
                continue
            
            # Initialize user bonuses if not exists
            if userteam_id not in stats["user_bonuses"]:
                stats["user_bonuses"][userteam_id] = {
                    "ideal_team_count": 0,
                    "mvp_count": 0,
                    "team_name": team.get("name", "Unknown")
                }
            
            # Get roster for this round
            roster_data = client.get_user_roundlineup(CHAMPIONSHIP_ID, round_id, userteam_id)
            time.sleep(0.1)  # Small delay
            
            if not roster_data:
                if team_idx <= 3:  # Only log first few failures
                    print(f"     ⚠️  No se pudo obtener roster para equipo {userteam_id}")
                continue
            
            stats["rosters_fetched"] += 1
            
            # Get players from roster
            roster_players = roster_data.get("players", [])
            roster_player_ids = {p.get("id") for p in roster_players if p.get("id")}
            
            # Check for dream team players
            dream_team_matches = roster_player_ids & dream_team_players
            if dream_team_matches:
                stats["user_bonuses"][userteam_id]["ideal_team_count"] += len(dream_team_matches)
                if team_idx <= 3:  # Log first few
                    print(f"     ✅ {team.get('name', 'Unknown')}: {len(dream_team_matches)} jugadores en dream team")
            
            # Check for MVP
            if mvp_id and mvp_id in roster_player_ids:
                stats["user_bonuses"][userteam_id]["mvp_count"] += 1
                if team_idx <= 3:  # Log first few
                    print(f"     🏆 {team.get('name', 'Unknown')}: Tiene al MVP!")
        
        print(f"   ✅ Procesado round {idx}/{len(closed_rounds)}")
    
    # Calculate complete finances for each user
    print("\n6. Calculando finanzas completas de usuarios...")
    
    user_finances = []
    
    for user in users_data:
        userteam_id = user.get("team_id")
        team_name = user.get("team_name", "Unknown")
        username = user.get("username", team_name)
        user_id = user.get("user_id")
        total_points = user.get("total_points", 0)
        
        # Calculate money from points
        points_money = total_points * POINTS_TO_EUROS
        
        # Get transaction data for this user
        user_transaction_data = user_transactions.get(userteam_id, user_transactions.get(user_id, {}))
        transaction_profit = user_transaction_data.get("transaction_profit", 0)
        total_spent = user_transaction_data.get("total_spent", 0)
        total_received = user_transaction_data.get("total_received", 0)
        transaction_count = user_transaction_data.get("transaction_count", 0)
        
        # Debug: Log suspicious transactions
        if transaction_profit < -50000000:  # Very negative (suspicious)
            print(f"   ⚠️  TRANSACCIÓN SOSPECHOSA: {team_name}")
            print(f"      - Gastado: {total_spent:,} €")
            print(f"      - Recibido: {total_received:,} €")
            print(f"      - Ganancia: {transaction_profit:,} €")
            print(f"      - Número transacciones: {transaction_count}")
        
        # Debug: Log users with 0 transactions but should have some
        if transaction_count == 0 and total_points > 400:  # High points but no transactions
            print(f"   ⚠️  SIN TRANSACCIONES: {team_name} (puntos: {total_points})")
        
        # Get bonuses for this user
        bonus_data = stats["user_bonuses"].get(userteam_id, stats["user_bonuses"].get(user_id, {
            "ideal_team_count": 0,
            "mvp_count": 0
        }))
        
        ideal_team_count = bonus_data.get("ideal_team_count", 0)
        mvp_count = bonus_data.get("mvp_count", 0)
        
        # Calculate bonuses (300,000 per dream team player, 800,000 per MVP)
        ideal_team_bonus = ideal_team_count * IDEAL_TEAM_BONUS
        mvp_bonus = mvp_count * MVP_BONUS
        total_bonus = ideal_team_bonus + mvp_bonus
        
        # Get punishments/bonuses for this user
        adjustment_data = user_punishments_bonuses.get(userteam_id, user_punishments_bonuses.get(user_id, {
            "total_punishments": 0,
            "total_bonuses": 0,
            "net_adjustment": 0,
            "punishment_count": 0,
            "bonus_count": 0
        }))
        
        net_adjustment = adjustment_data.get("net_adjustment", 0)
        
        # Total money = initial budget + points money + transaction profit + bonuses - punishments + bonuses
        total_money = INITIAL_BUDGET + points_money + transaction_profit + total_bonus + net_adjustment
        
        user_finances.append({
            "userteam_id": userteam_id,
            "user_id": user_id,
            "team_name": team_name,
            "username": username,
            "total_points": total_points,
            "initial_budget": INITIAL_BUDGET,
            "points_money": points_money,
            "transaction_profit": transaction_profit,
            "total_spent": total_spent,
            "total_received": total_received,
            "ideal_team_count": ideal_team_count,
            "mvp_count": mvp_count,
            "ideal_team_bonus": ideal_team_bonus,
            "mvp_bonus": mvp_bonus,
            "total_bonus": total_bonus,
            "total_punishments": adjustment_data.get("total_punishments", 0),
            "total_bonuses": adjustment_data.get("total_bonuses", 0),
            "net_adjustment": net_adjustment,
            "punishment_count": adjustment_data.get("punishment_count", 0),
            "bonus_count": adjustment_data.get("bonus_count", 0),
            "total_money": total_money,
            "transaction_count": transaction_count
        })
    
    # Sort by total money (descending)
    user_finances.sort(key=lambda x: x["total_money"], reverse=True)
    
    # Print summary
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Rounds procesados: {stats['dream_teams_fetched']}/{stats['total_rounds']}")
    print(f"Dream teams obtenidos: {stats['dream_teams_fetched']}")
    print(f"Rosters obtenidos: {stats['rosters_fetched']}")
    print(f"Jugadores únicos en dream teams: {len(stats['dream_team_players'])}")
    print(f"MVPs únicos: {len(stats['mvp_players'])}")
    print(f"Usuarios con bonos: {len(stats['user_bonuses'])}")
    print(f"Usuarios con finanzas calculadas: {len(user_finances)}")
    
    # Show detailed transaction analysis
    print("\n" + "-" * 80)
    print("ANÁLISIS DE TRANSACCIONES")
    print("-" * 80)
    users_with_transactions = [u for u in user_finances if u['transaction_count'] > 0]
    users_without_transactions = [u for u in user_finances if u['transaction_count'] == 0]
    print(f"Usuarios con transacciones: {len(users_with_transactions)}")
    print(f"Usuarios sin transacciones: {len(users_without_transactions)}")
    
    if users_with_transactions:
        print(f"\nTransacciones totales: {sum(u['transaction_count'] for u in users_with_transactions)}")
        print(f"Gasto total: {sum(u['total_spent'] for u in users_with_transactions):,} €")
        print(f"Ingreso total: {sum(u['total_received'] for u in users_with_transactions):,} €")
        print(f"Ganancia total: {sum(u['transaction_profit'] for u in users_with_transactions):,} €")
    
    # Show users with suspicious transactions
    suspicious = [u for u in user_finances if u['transaction_profit'] < -30000000]
    if suspicious:
        print(f"\n⚠️  Usuarios con transacciones sospechosas (ganancia < -30M): {len(suspicious)}")
        for user in suspicious[:5]:
            print(f"   - {user['team_name']}: {user['transaction_profit']:,} € "
                  f"(gastado: {user['total_spent']:,} €, recibido: {user['total_received']:,} €, "
                  f"transacciones: {user['transaction_count']})")
    
    # Show top users by total money
    print("\n" + "-" * 100)
    print("TOP 15 USUARIOS POR DINERO TOTAL")
    print("-" * 100)
    print(f"{'Pos':<5} {'Equipo':<30} {'Puntos':<8} {'Dinero Pts':<18} {'Transac':<18} {'Bonos':<18} {'TOTAL':<20}")
    print("-" * 100)
    
    for idx, user in enumerate(user_finances[:15], 1):
        team_name = user['team_name'][:28] if len(user['team_name']) > 28 else user['team_name']
        transac_str = f"{user['transaction_profit']:,}" if user['transaction_profit'] != 0 else "0"
        print(f"{idx:<5} {team_name:<30} "
              f"{user['total_points']:<8} "
              f"{user['points_money']:>15,} € "
              f"{transac_str:>15} "
              f"{user['total_bonus']:>15,} € "
              f"{user['total_money']:>18,} €")
    
    # Show top users by bonuses
    print("\n" + "-" * 80)
    print("TOP 10 USUARIOS POR BONOS")
    print("-" * 80)
    
    user_bonus_list = []
    for user in user_finances:
        if user['total_bonus'] > 0:
            user_bonus_list.append({
                "userteam_id": user["userteam_id"],
                "team_name": user["team_name"],
                "ideal_team_count": user["ideal_team_count"],
                "mvp_count": user["mvp_count"],
                "ideal_team_bonus": user["ideal_team_bonus"],
                "mvp_bonus": user["mvp_bonus"],
                "total_bonus": user["total_bonus"]
            })
    
    user_bonus_list.sort(key=lambda x: x["total_bonus"], reverse=True)
    
    for idx, user in enumerate(user_bonus_list[:10], 1):
        print(f"{idx:2d}. {user['team_name']:30s} | "
              f"Dream Team: {user['ideal_team_count']:2d} ({user['ideal_team_bonus']:,} €) | "
              f"MVP: {user['mvp_count']:2d} ({user['mvp_bonus']:,} €) | "
              f"Total: {user['total_bonus']:,} €")
    
    # Debug: Show transaction details for specific users
    print("\n" + "-" * 80)
    print("DEBUG: DETALLES DE TRANSACCIONES POR USUARIO")
    print("-" * 80)
    
    # Show first 5 users with transactions
    debug_users = [u for u in user_finances if u['transaction_count'] > 0][:5]
    for user in debug_users:
        print(f"\n{user['team_name']}:")
        print(f"  - userteam_id: {user['userteam_id']}")
        print(f"  - user_id: {user['user_id']}")
        print(f"  - Transacciones: {user['transaction_count']}")
        print(f"  - Gastado: {user['total_spent']:,} €")
        print(f"  - Recibido: {user['total_received']:,} €")
        print(f"  - Ganancia: {user['transaction_profit']:,} €")
        
        # Try to get raw transaction data from database
        try:
            with dm.db.get_connection() as conn:
                cursor = dm.db.get_cursor(conn)
                # Get transactions for this user
                sql = '''
                    SELECT buyer_user_id, seller_user_id, price, transaction_date
                    FROM transactions
                    WHERE buyer_user_id = ? OR seller_user_id = ?
                    ORDER BY transaction_date
                    LIMIT 5
                '''
                sql = dm.db.adapt_params(sql)
                cursor.execute(sql, (user['userteam_id'], user['userteam_id']))
                raw_transactions = cursor.fetchall()
                
                if raw_transactions:
                    print(f"  - Primeras 5 transacciones en BD:")
                    for txn in raw_transactions:
                        print(f"    Comprador: {txn[0]}, Vendedor: {txn[1]}, Precio: {txn[2]:,} €")
                else:
                    # Try by username
                    sql = '''
                        SELECT buyer_user_id, seller_user_id, price, transaction_date
                        FROM transactions t
                        JOIN users u ON (t.buyer_user_id = u.user_id OR t.seller_user_id = u.user_id)
                        WHERE u.username = ?
                        ORDER BY transaction_date
                        LIMIT 5
                    '''
                    sql = dm.db.adapt_params(sql)
                    cursor.execute(sql, (user['team_name'],))
                    raw_transactions = cursor.fetchall()
                    if raw_transactions:
                        print(f"  - Transacciones encontradas por username:")
                        for txn in raw_transactions:
                            print(f"    Comprador: {txn[0]}, Vendedor: {txn[1]}, Precio: {txn[2]:,} €")
        except Exception as e:
            print(f"  - Error obteniendo detalles: {e}")
    
    # Save results to JSON
    output_file = backend_dir / "scripts" / "user_finances_data.json"
    output_data = {
        "championship_id": CHAMPIONSHIP_ID,
        "constants": {
            "points_to_euros": POINTS_TO_EUROS,
            "ideal_team_bonus": IDEAL_TEAM_BONUS,
            "mvp_bonus": MVP_BONUS
        },
        "stats": {
            "total_rounds": stats["total_rounds"],
            "dream_teams_fetched": stats["dream_teams_fetched"],
            "rosters_fetched": stats["rosters_fetched"],
            "unique_dream_team_players": len(stats["dream_team_players"]),
            "unique_mvps": len(stats["mvp_players"]),
            "users_with_bonuses": len(stats["user_bonuses"]),
            "total_users": len(user_finances),
            "users_with_transactions": len(users_with_transactions),
            "users_without_transactions": len(users_without_transactions)
        },
        "user_finances": user_finances
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Datos guardados en: {output_file}")
    print(f"   Total usuarios: {len(user_finances)}")
    print(f"   Dinero total acumulado: {sum(u['total_money'] for u in user_finances):,} €")
    print("\n" + "=" * 80)
    print("Script completado exitosamente")
    print("=" * 80)


if __name__ == "__main__":
    main()

