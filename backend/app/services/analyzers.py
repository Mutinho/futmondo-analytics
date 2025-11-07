#!/usr/bin/env python3
"""
Analyzers - Business logic for analyzing player transactions and user profits
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from app.services.data_manager import PlayerData, TransactionData, UserProfitData, DataManager
from app.core.config import MIN_TRANSACTIONS_FOR_ANALYSIS

logger = logging.getLogger(__name__)

@dataclass
class PlayerTransactionAnalysis:
    """Player transaction analysis result"""
    player_id: str
    player_name: str
    role: str
    team: str
    current_value: int
    current_points: int
    profit_analysis: Dict
    average_performance: Optional[Dict] = None

class TransactionAnalyzer:
    """Analyzes player transactions for profit opportunities"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def analyze_player_transactions(self, player: PlayerData, transactions: List[TransactionData]) -> Optional[PlayerTransactionAnalysis]:
        """Analyze a single player's transaction history for profit opportunities"""
        if len(transactions) < MIN_TRANSACTIONS_FOR_ANALYSIS:
            return None
        
        # Calculate profits between consecutive trades
        profits = []
        for i in range(1, len(transactions)):
            prev_trade = transactions[i-1]
            curr_trade = transactions[i]
            
            # Previous trade: someone bought the player
            # Current trade: someone else bought the player (previous owner sold)
            buy_price = prev_trade.price
            sell_price = curr_trade.price
            profit = sell_price - buy_price
            profit_percentage = (profit / buy_price * 100) if buy_price > 0 else 0
            
            # Get usernames from user IDs
            buyer_user = self.data_manager.get_user_by_id(prev_trade.buyer_user_id)
            seller_user = self.data_manager.get_user_by_id(curr_trade.seller_user_id)
            
            profits.append({
                "buyer": buyer_user.username if buyer_user else prev_trade.buyer_user_id,
                "seller": seller_user.username if seller_user else curr_trade.seller_user_id,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "profit": profit,
                "profit_percentage": profit_percentage,
                "transaction_date": curr_trade.date
            })
        
        if not profits:
            return None
        
        # Find best profit opportunity
        max_profit = max(profits, key=lambda x: x["profit"])
        avg_profit = sum(p["profit"] for p in profits) / len(profits)
        
        profit_analysis = {
            "max_profit": max_profit["profit"],
            "max_profit_percentage": max_profit["profit_percentage"],
            "avg_profit": avg_profit,
            "total_transactions": len(transactions),
            "all_profits": profits,
            "best_transaction": max_profit
        }
        
        return PlayerTransactionAnalysis(
            player_id=player.id,
            player_name=player.name,
            role=player.role,
            team=player.team,
            current_value=player.current_value,
            current_points=player.current_points,
            profit_analysis=profit_analysis,
            average_performance=player.average_performance
        )
    
    def analyze_all_players(self) -> List[PlayerTransactionAnalysis]:
        """Analyze all players with transaction data"""
        logger.info("Starting player transaction analysis...")
        
        players = self.data_manager.get_players()
        traded_players = [p for p in players if p.userteam_id is not None]
        
        logger.info(f"Analyzing {len(traded_players)} traded players...")
        
        analyses = []
        for i, player in enumerate(traded_players):
            if i % 50 == 0:
                logger.info(f"Processing player {i+1}/{len(traded_players)}")
            
            transactions = self.data_manager.get_player_transactions(player.id)
            if transactions:
                analysis = self.analyze_player_transactions(player, transactions)
                if analysis:
                    analyses.append(analysis)
        
        # Sort by profit potential
        analyses.sort(key=lambda x: x.profit_analysis.get("max_profit", 0), reverse=True)
        
        logger.info(f"Found {len(analyses)} players with profitable transaction data")
        return analyses

class UserProfitAnalyzer:
    """Analyzes user profits from all transactions"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def analyze_user_profits(self) -> List[UserProfitData]:
        """Analyze profits for all users based on their transaction history"""
        logger.info("Starting user profit analysis...")
        
        # Get all transactions grouped by user
        user_transactions = self._get_user_transactions()
        
        user_profits = []
        for username, transactions in user_transactions.items():
            profit_data = self._calculate_user_profit(username, transactions)
            if profit_data:
                user_profits.append(profit_data)
        
        # Sort by total profit
        user_profits.sort(key=lambda x: x.total_profit, reverse=True)
        
        logger.info(f"Analyzed profits for {len(user_profits)} users")
        return user_profits
    
    def _get_user_transactions(self) -> Dict[str, List[Dict]]:
        """Get all transactions grouped by user_id (both buy and sell)"""
        conn = self.data_manager.db_path
        import sqlite3
        
        conn_db = sqlite3.connect(conn)
        cursor = conn_db.cursor()
        
        # Get all transactions where user is either buyer or seller
        cursor.execute('''
            SELECT t.seller_user_id, t.buyer_user_id, t.price, t.date, t.transaction_type,
                   p.name as player_name, p.role, p.team, p.current_value, t.player_id,
                   su.username as seller_username, bu.username as buyer_username
            FROM transactions t
            JOIN players p ON t.player_id = p.id
            JOIN users su ON t.seller_user_id = su.id
            JOIN users bu ON t.buyer_user_id = bu.id
            ORDER BY t.date
        ''')
        
        rows = cursor.fetchall()
        conn_db.close()
        
        user_transactions = {}
        
        # Process all transactions
        for row in rows:
            seller_user_id = row[0]
            buyer_user_id = row[1]
            price = row[2]
            date = row[3]
            transaction_type = row[4]
            player_name = row[5]
            role = row[6]
            team = row[7]
            current_value = row[8]
            player_id = row[9]
            seller_username = row[10]
            buyer_username = row[11]
            
            # Add transaction for seller (if not Market)
            if seller_username != "Market":
                if seller_user_id not in user_transactions:
                    user_transactions[seller_user_id] = []
                
                user_transactions[seller_user_id].append({
                    "price": price,
                    "date": date,
                    "transaction_type": transaction_type,
                    "player_name": player_name,
                    "role": role,
                    "team": team,
                    "current_value": current_value,
                    "player_id": player_id,
                    "is_buy": False,
                    "counterparty": buyer_username
                })
            
            # Add transaction for buyer
            if buyer_user_id not in user_transactions:
                user_transactions[buyer_user_id] = []
            
            user_transactions[buyer_user_id].append({
                "price": price,
                "date": date,
                "transaction_type": transaction_type,
                "player_name": player_name,
                "role": role,
                "team": team,
                "current_value": current_value,
                "player_id": player_id,
                "is_buy": True,
                "counterparty": seller_username
            })
        
        # Sort all transactions by date for each user
        for user_id in user_transactions:
            user_transactions[user_id].sort(key=lambda x: x["date"])
        
        return user_transactions
    
    def _calculate_user_profit(self, user_id: str, transactions: List[Dict]) -> Optional[UserProfitData]:
        """Calculate profit data for a specific user"""
        if len(transactions) < 1:
            return None
        
        # Group transactions by player to calculate individual profits
        player_transactions = {}
        for transaction in transactions:
            player_id = transaction["player_id"]
            if player_id not in player_transactions:
                player_transactions[player_id] = {
                    "player_name": transaction["player_name"],
                    "role": transaction["role"],
                    "team": transaction["team"],
                    "current_value": transaction["current_value"],
                    "buys": [],
                    "sells": []
                }
            
            if transaction["is_buy"]:
                player_transactions[player_id]["buys"].append(transaction)
            else:
                player_transactions[player_id]["sells"].append(transaction)
        
        total_profit = 0
        total_transactions = 0
        successful_trades = 0
        failed_trades = 0
        profits = []
        
        for player_id, player_data in player_transactions.items():
            buys = sorted(player_data["buys"], key=lambda x: x["date"])
            sells = sorted(player_data["sells"], key=lambda x: x["date"])
            
            # Calculate profit for each buy-sell pair
            for buy_tx in buys:
                # Find the corresponding sell transaction (if any)
                for sell_tx in sells:
                    if sell_tx["date"] > buy_tx["date"]:  # Sell happened after buy
                        profit = sell_tx["price"] - buy_tx["price"]
                        total_profit += profit
                        total_transactions += 1
                        profits.append(profit)
                        
                        if profit > 0:
                            successful_trades += 1
                        else:
                            failed_trades += 1
                        break  # Only count the first sell after each buy
        
        if total_transactions == 0:
            return None
        
        best_profit = max(profits) if profits else 0
        worst_loss = min(profits) if profits else 0
        avg_profit_per_trade = total_profit / total_transactions
        
        # Calculate profit percentage (total profit / total investment)
        total_investment = sum(tx["price"] for tx in transactions if tx["is_buy"])
        profit_percentage = (total_profit / total_investment * 100) if total_investment > 0 else 0
        
        # Get username from data manager
        user_data = self.data_manager.get_user_by_id(user_id)
        username = user_data.username if user_data else user_id
        
        return UserProfitData(
            user_id=user_id,
            username=username,
            team_id=user_data.team_id if user_data else "",
            team_name=user_data.team_name if user_data else "",
            total_profit=total_profit,
            total_transactions=total_transactions,
            successful_trades=successful_trades,
            failed_trades=failed_trades,
            best_profit=best_profit,
            worst_loss=worst_loss,
            avg_profit_per_trade=avg_profit_per_trade,
            profit_percentage=profit_percentage
        )
    
    def get_user_detailed_analysis(self, user_id: str) -> Dict:
        """Get detailed analysis for a specific user"""
        # Get user by ID first
        user_data = self.data_manager.get_user_by_id(user_id)
        if not user_data:
            return {"error": f"User with ID {user_id} not found"}
        
        username = user_data.username
        
        conn = self.data_manager.db_path
        import sqlite3
        
        conn_db = sqlite3.connect(conn)
        cursor = conn_db.cursor()
        
        # Get all transactions where user is either buyer or seller
        cursor.execute('''
            SELECT t.seller_user_id, t.buyer_user_id, t.price, t.date, t.transaction_type, t.player_id,
                   p.name as player_name, p.role, p.team, p.current_value,
                   su.username as seller_username, bu.username as buyer_username
            FROM transactions t
            JOIN players p ON t.player_id = p.id
            JOIN users su ON t.seller_user_id = su.id
            JOIN users bu ON t.buyer_user_id = bu.id
            WHERE t.seller_user_id = ? OR t.buyer_user_id = ?
            ORDER BY t.date
        ''', (user_id, user_id))
        
        rows = cursor.fetchall()
        conn_db.close()
        
        transactions = []
        
        # Process all transactions
        for row in rows:
            seller_user_id = row[0]
            buyer_user_id = row[1]
            price = row[2]
            date = row[3]
            transaction_type = row[4]
            player_id = row[5]
            player_name = row[6]
            role = row[7]
            team = row[8]
            current_value = row[9]
            seller_username = row[10]
            buyer_username = row[11]
            
            # Add transaction for seller (if user is seller and not Market)
            if seller_user_id == user_id and seller_username != "Market":
                transactions.append({
                    "price": price,
                    "date": date,
                    "transaction_type": transaction_type,
                    "player_id": player_id,
                    "player_name": player_name,
                    "role": role,
                    "team": team,
                    "current_value": current_value,
                    "is_buy": False,
                    "counterparty": buyer_username
                })
            
            # Add transaction for buyer (if user is buyer)
            if buyer_user_id == user_id:
                transactions.append({
                    "price": price,
                    "date": date,
                    "transaction_type": transaction_type,
                    "player_id": player_id,
                    "player_name": player_name,
                    "role": role,
                    "team": team,
                    "current_value": current_value,
                    "is_buy": True,
                    "counterparty": seller_username
                })
        
        # Sort all transactions by date
        transactions.sort(key=lambda x: x["date"])
        
        # Group by player and calculate individual profits
        player_analysis = {}
        for transaction in transactions:
            player_id = transaction["player_id"]
            if player_id not in player_analysis:
                player_analysis[player_id] = {
                    "player_name": transaction["player_name"],
                    "role": transaction["role"],
                    "team": transaction["team"],
                    "current_value": transaction["current_value"],
                    "transactions": [],
                    "buys": [],
                    "sells": [],
                    "total_invested": 0,
                    "total_received": 0
                }
            
            player_analysis[player_id]["transactions"].append(transaction)
            
            if transaction["is_buy"]:
                player_analysis[player_id]["buys"].append(transaction)
                player_analysis[player_id]["total_invested"] += transaction["price"]
            else:
                player_analysis[player_id]["sells"].append(transaction)
                player_analysis[player_id]["total_received"] += transaction["price"]
        
        # Calculate profits for each player
        for player_id, data in player_analysis.items():
            buys = sorted(data["buys"], key=lambda x: x["date"])
            sells = sorted(data["sells"], key=lambda x: x["date"])
            
            total_profit = 0
            trade_count = 0
            
            # Calculate profit for each buy-sell pair
            for buy_tx in buys:
                for sell_tx in sells:
                    if sell_tx["date"] > buy_tx["date"]:  # Sell happened after buy
                        profit = sell_tx["price"] - buy_tx["price"]
                        total_profit += profit
                        trade_count += 1
                        break  # Only count the first sell after each buy
            
            data["profit"] = total_profit
            data["profit_percentage"] = (total_profit / data["total_invested"] * 100) if data["total_invested"] > 0 else 0
            data["trade_count"] = trade_count
        
        return {
            "username": username,
            "total_transactions": len(transactions),
            "player_analysis": player_analysis
        }
