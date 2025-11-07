#!/usr/bin/env python3
"""
Script para exportar todas las transacciones de un usuario específico a CSV
"""
import sys
import os
import csv
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.futmondo_client import FutmondoClient
from app.core.config import FUTMONDO_EMAIL, FUTMONDO_PASSWORD, CHAMPIONSHIP_ID

def export_user_transactions(user_identifier: str, output_file: str = None):
    """Export all transactions for a specific user to CSV
    
    Args:
        user_identifier: Can be user_id, team_id, or username/team_name
    """
    
    from app.services.data_manager_v2 import DataManagerV2
    
    dm = DataManagerV2()
    
    # Try to find user by name first
    user_info = dm.get_user_id_by_name(user_identifier)
    if user_info:
        user_id = user_info.get("user_id")
        team_id = user_info.get("team_id")
        print(f"✅ Usuario encontrado: {user_identifier}")
        print(f"   - user_id: {user_id}")
        print(f"   - team_id: {team_id}")
        # Use team_id if available, otherwise user_id
        actual_user_id = team_id if team_id else user_id
    else:
        # Assume it's already a user_id or team_id
        actual_user_id = user_identifier
        print(f"⚠️  No se encontró usuario por nombre, usando como ID: {user_identifier}")
    
    if output_file is None:
        # Create filename from identifier
        safe_name = user_identifier.replace("/", "_").replace(" ", "_")
        output_file = f"transactions_{safe_name}.csv"
    
    print("=" * 80)
    print(f"Exportando transacciones del usuario: {user_identifier} (ID: {actual_user_id})")
    print("=" * 80)
    
    # Initialize client
    client = FutmondoClient(FUTMONDO_EMAIL, FUTMONDO_PASSWORD)
    
    # Login
    print("\n1. Autenticando...")
    if not client.login():
        print("❌ Error: No se pudo autenticar")
        return
    print("✅ Autenticación exitosa")
    
    # Fetch all transactions from pressroom with pagination
    print("\n2. Obteniendo todas las transacciones del pressroom...")
    all_transactions = []
    seen_transaction_ids = set()  # Track IDs to avoid duplicates
    from_id = ""  # Start with empty string for first page
    page_count = 0
    
    while True:
        try:
            page_count += 1
            print(f"   Obteniendo página {page_count}...", end=" ")
            
            # For first page, use empty string, for subsequent pages use the last _id
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
            print(f"✅ {len(new_transactions)} transacciones nuevas (total: {len(all_transactions)})")
            
            # If no new transactions, we've reached the end
            if len(new_transactions) == 0:
                print("   No hay más transacciones nuevas")
                break
            
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
    
    print(f"\n✅ Total transacciones obtenidas: {len(all_transactions)}")
    print(f"✅ Páginas procesadas: {page_count}")
    
    # Filter transactions for the specific user
    print(f"\n3. Filtrando transacciones del usuario {actual_user_id}...")
    user_transactions = []
    
    # Also get user_id if we have team_id (for matching)
    matching_ids = {actual_user_id}
    matching_names = {user_identifier}  # Also match by name
    if user_info and team_id and user_id:
        matching_ids.add(user_id)
        matching_ids.add(team_id)
    
    for transaction in all_transactions:
        buyer_info = transaction.get("_buyer")
        seller_info = transaction.get("_seller")
        
        buyer_id = buyer_info.get("_id") if buyer_info else None
        seller_id = seller_info.get("_id") if seller_info else None
        buyer_name = buyer_info.get("name", "") if buyer_info else ""
        seller_name = seller_info.get("name", "") if seller_info else ""
        
        # Check if user is buyer or seller (match by ID or name)
        buyer_match = buyer_id in matching_ids or buyer_name in matching_names
        seller_match = seller_id in matching_ids or seller_name in matching_names
        
        if buyer_match or seller_match:
            user_transactions.append(transaction)
    
    print(f"✅ Encontradas {len(user_transactions)} transacciones del usuario")
    
    # Sort by date (most recent first)
    user_transactions.sort(key=lambda x: x.get("created", ""), reverse=True)
    
    # Write to CSV
    print(f"\n4. Escribiendo CSV: {output_file}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'transaction_id',
            'date',
            'type',  # 'buy' or 'sell'
            'player_id',
            'player_name',
            'player_team',
            'other_user_id',
            'other_user_name',
            'price',
            'is_market'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for transaction in user_transactions:
            transaction_id = transaction.get("_id", "")
            created = transaction.get("created", "")
            
            player_info = transaction.get("_player", {})
            player_id = player_info.get("_id", "")
            player_name = player_info.get("name", "")
            
            player_team_info = transaction.get("_playerTeam", {})
            player_team = player_team_info.get("name", "")
            
            buyer_info = transaction.get("_buyer")
            seller_info = transaction.get("_seller")
            price = transaction.get("price", 0)
            
            buyer_id = buyer_info.get("_id") if buyer_info else None
            seller_id = seller_info.get("_id") if seller_info else None
            
            # Determine transaction type (check against all matching IDs or names)
            buyer_match = buyer_id in matching_ids or buyer_name in matching_names
            seller_match = seller_id in matching_ids or seller_name in matching_names
            
            if buyer_match:
                transaction_type = "buy"
                other_user_id = seller_id if seller_id else "Market"
                other_user_name = seller_info.get("name", "Market") if seller_info else "Market"
                is_market = seller_id is None
            elif seller_match:
                transaction_type = "sell"
                other_user_id = buyer_id if buyer_id else "Market"
                other_user_name = buyer_info.get("name", "Market") if buyer_info else "Market"
                is_market = buyer_id is None
            else:
                continue  # Should not happen, but just in case
            
            writer.writerow({
                'transaction_id': transaction_id,
                'date': created,
                'type': transaction_type,
                'player_id': player_id,
                'player_name': player_name,
                'player_team': player_team,
                'other_user_id': other_user_id,
                'other_user_name': other_user_name,
                'price': price,
                'is_market': 'Yes' if is_market else 'No'
            })
    
    print(f"✅ CSV creado: {output_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    
    buys = [t for t in user_transactions if (t.get("_buyer", {}).get("_id") in matching_ids or t.get("_buyer", {}).get("name", "") in matching_names)]
    sells = [t for t in user_transactions if (t.get("_seller", {}).get("_id") in matching_ids or t.get("_seller", {}).get("name", "") in matching_names)]
    
    total_spent = sum(t.get("price", 0) for t in buys)
    total_received = sum(t.get("price", 0) for t in sells)
    profit = total_received - total_spent
    
    print(f"Total transacciones: {len(user_transactions)}")
    print(f"  - Compras: {len(buys)}")
    print(f"  - Ventas: {len(sells)}")
    print(f"\nTotal gastado: {total_spent:,} €")
    print(f"Total recibido: {total_received:,} €")
    print(f"Ganancia/Pérdida: {profit:,} €")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Default: Fabinho
    user_identifier = "Fabinho"
    
    if len(sys.argv) > 1:
        user_identifier = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = None  # Will be generated from identifier
    
    export_user_transactions(user_identifier, output_file)

