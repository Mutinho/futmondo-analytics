#!/usr/bin/env python3
"""
Team Analyzer - Analyzes team financial status and rosters
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from app.services.data_manager import DataManager, UserProfitData
from app.services.futmondo_client import FutmondoClient
from app.core.config import CHAMPIONSHIP_ID, REQUEST_DELAY_SECONDS

logger = logging.getLogger(__name__)

@dataclass
class TeamData:
    """Team data structure"""
    id: str
    userid: str
    name: str
    teamname: str
    teamslug: str
    points: int
    team_value: int
    last_access: str
    is_admin: bool
    awards: Dict
    clauses: Dict
    initial_budget: int = 270000000  # 270M initial budget

@dataclass
class TeamFinancialStatus:
    """Team financial status analysis"""
    team_id: str
    team_name: str
    owner_name: str
    current_team_value: int
    initial_budget: int
    total_transaction_profit: float
    current_money: float
    total_invested: float
    profit_percentage: float
    transaction_count: int
    successful_trades: int
    failed_trades: int

class TeamAnalyzer:
    """Analyzes team financial status and rosters"""
    
    def __init__(self, data_manager: DataManager, client: FutmondoClient):
        self.data_manager = data_manager
        self.client = client
        self.initial_budget = 270000000  # 270M initial budget
    
    def get_championship_teams(self) -> Optional[List[TeamData]]:
        """Fetch all championship teams"""
        if not self.client.is_authenticated():
            logger.error("Not authenticated. Please login first.")
            return None
        
        logger.info("Fetching championship teams...")
        
        request_data = {
            "header": {
                "token": self.client.token,
                "userid": self.client.user_id
            },
            "query": {
                "championshipId": CHAMPIONSHIP_ID
            },
            "answer": {}
        }
        
        try:
            response = self.client.session.post(
                f"{self.client.base_url}/2/championship/teams",
                json=request_data
            )
            response.raise_for_status()
            
            data = response.json()
            teams_data = data.get("answer", {}).get("teams", [])
            
            teams = []
            for team_data in teams_data:
                team = TeamData(
                    id=team_data["id"],
                    userid=team_data["userid"],
                    name=team_data["name"],
                    teamname=team_data["teamname"],
                    teamslug=team_data["teamslug"],
                    points=team_data["points"],
                    team_value=team_data["teamValue"],
                    last_access=team_data.get("lastAccess", ""),
                    is_admin=team_data.get("isAdmin", False),
                    awards=team_data.get("awards", {}),
                    clauses=team_data.get("clauses", {})
                )
                teams.append(team)
            
            logger.info(f"Retrieved {len(teams)} teams")
            return teams
            
        except Exception as e:
            logger.error(f"Failed to fetch championship teams: {e}")
            return None
    
    def get_team_roster(self, team_id: str) -> Optional[List[Dict]]:
        """Get team roster using the client method"""
        if not self.client.is_authenticated():
            logger.error("Not authenticated. Please login first.")
            return None
        
        try:
            roster = self.client.get_userteam_roster(CHAMPIONSHIP_ID, team_id)
            if roster:
                logger.info(f"Retrieved roster for team {team_id}: {len(roster)} players")
            return roster
        except Exception as e:
            logger.error(f"Failed to fetch roster for team {team_id}: {e}")
            return None
    
    def calculate_team_financial_status(self, team: TeamData) -> Optional[TeamFinancialStatus]:
        """Calculate team's financial status based on actual transaction money flow"""
        # Get detailed user analysis to track actual money flow
        from analyzers import UserProfitAnalyzer
        user_profit_analyzer = UserProfitAnalyzer(self.data_manager)
        user_analysis = user_profit_analyzer.get_user_detailed_analysis(team.userid)
        
        if not user_analysis:
            # If no transaction data, assume no transactions
            return TeamFinancialStatus(
                team_id=team.id,
                team_name=team.teamname,
                owner_name=team.name,
                current_team_value=team.team_value,
                initial_budget=self.initial_budget,
                total_transaction_profit=0,
                current_money=self.initial_budget - team.team_value,
                total_invested=self.initial_budget,
                profit_percentage=0,
                transaction_count=0,
                successful_trades=0,
                failed_trades=0
            )
        
        # Calculate actual money flow from transactions
        total_spent = 0
        total_received = 0
        transaction_count = 0
        successful_trades = 0
        failed_trades = 0
        
        for player_name, player_data in user_analysis.get('player_analysis', {}).items():
            transactions = player_data.get('transactions', [])
            if len(transactions) >= 2:
                # Sort transactions by date
                transactions.sort(key=lambda x: x['date'])
                
                # Track money flow for this player
                for i in range(len(transactions)):
                    transaction = transactions[i]
                    price = transaction['price']
                    
                    if i == 0:
                        # First transaction is a purchase (money spent)
                        total_spent += price
                    else:
                        # Subsequent transactions are sales (money received)
                        total_received += price
                        
                        # Check if this was a profitable trade
                        prev_price = transactions[i-1]['price']
                        if price > prev_price:
                            successful_trades += 1
                        else:
                            failed_trades += 1
                
                transaction_count += len(transactions) - 1  # -1 because first is purchase, rest are sales
        
        # Calculate current money: Initial budget - total spent + total received - current team value
        # The current team value represents the cost of current players
        current_money = self.initial_budget - total_spent + total_received - team.team_value
        
        # Calculate total transaction profit (money received from sales - money spent on purchases)
        total_transaction_profit = total_received - total_spent
        
        # Calculate total invested (initial budget + net spending on players)
        total_invested = self.initial_budget + total_spent - total_received
        
        # Calculate profit percentage
        profit_percentage = (total_transaction_profit / self.initial_budget * 100) if self.initial_budget > 0 else 0
        
        return TeamFinancialStatus(
            team_id=team.id,
            team_name=team.teamname,
            owner_name=team.name,
            current_team_value=team.team_value,
            initial_budget=self.initial_budget,
            total_transaction_profit=total_transaction_profit,
            current_money=current_money,
            total_invested=total_invested,
            profit_percentage=profit_percentage,
            transaction_count=transaction_count,
            successful_trades=successful_trades,
            failed_trades=failed_trades
        )
    
    def get_detailed_money_flow(self, team: TeamData) -> Dict:
        """Get detailed money flow breakdown for a team"""
        from analyzers import UserProfitAnalyzer
        user_profit_analyzer = UserProfitAnalyzer(self.data_manager)
        user_analysis = user_profit_analyzer.get_user_detailed_analysis(team.name)
        
        if not user_analysis:
            return {
                "team_name": team.teamname,
                "owner_name": team.name,
                "initial_budget": self.initial_budget,
                "current_team_value": team.team_value,
                "total_spent": 0,
                "total_received": 0,
                "current_money": self.initial_budget - team.team_value,
                "transaction_breakdown": [],
                "summary": "No transactions found"
            }
        
        total_spent = 0
        total_received = 0
        transaction_breakdown = []
        
        for player_name, player_data in user_analysis.get('player_analysis', {}).items():
            transactions = player_data.get('transactions', [])
            if len(transactions) >= 2:
                # Sort transactions by date
                transactions.sort(key=lambda x: x['date'])
                
                player_breakdown = {
                    "player_name": player_name,
                    "transactions": [],
                    "total_spent": 0,
                    "total_received": 0,
                    "net_profit": 0
                }
                
                for i, transaction in enumerate(transactions):
                    price = transaction['price']
                    date = transaction['date']
                    is_current = transaction.get('is_current_owner', False)
                    
                    if i == 0:
                        # First transaction is a purchase
                        total_spent += price
                        player_breakdown["total_spent"] += price
                        player_breakdown["transactions"].append({
                            "type": "BUY",
                            "price": price,
                            "date": date,
                            "is_current": is_current
                        })
                    else:
                        # Subsequent transactions are sales
                        total_received += price
                        player_breakdown["total_received"] += price
                        player_breakdown["transactions"].append({
                            "type": "SELL",
                            "price": price,
                            "date": date,
                            "is_current": is_current
                        })
                
                player_breakdown["net_profit"] = player_breakdown["total_received"] - player_breakdown["total_spent"]
                transaction_breakdown.append(player_breakdown)
        
        current_money = self.initial_budget - total_spent + total_received - team.team_value
        
        return {
            "team_name": team.teamname,
            "owner_name": team.name,
            "initial_budget": self.initial_budget,
            "current_team_value": team.team_value,
            "total_spent": total_spent,
            "total_received": total_received,
            "current_money": current_money,
            "transaction_breakdown": transaction_breakdown,
            "summary": f"Spent: €{total_spent:,}, Received: €{total_received:,}, Current Money: €{current_money:,.0f}"
        }
    
    def analyze_all_teams_financial_status(self) -> List[TeamFinancialStatus]:
        """Analyze financial status for all teams"""
        logger.info("Starting team financial analysis...")
        
        # Get all teams
        teams = self.get_championship_teams()
        if not teams:
            logger.error("Failed to fetch teams")
            return []
        
        # Calculate financial status for each team
        financial_statuses = []
        for team in teams:
            status = self.calculate_team_financial_status(team)
            if status:
                financial_statuses.append(status)
        
        # Sort by current money (descending)
        financial_statuses.sort(key=lambda x: x.current_money, reverse=True)
        
        logger.info(f"Analyzed financial status for {len(financial_statuses)} teams")
        return financial_statuses
    
    def get_team_detailed_analysis(self, team_id: str) -> Optional[Dict]:
        """Get detailed analysis for a specific team"""
        # Get team data
        teams = self.get_championship_teams()
        team = None
        for t in teams:
            if t.id == team_id:
                team = t
                break
        
        if not team:
            logger.error(f"Team {team_id} not found")
            return None
        
        # Get financial status
        financial_status = self.calculate_team_financial_status(team)
        if not financial_status:
            return None
        
        # Get roster
        roster = self.get_team_roster(team_id)
        
        # Get user detailed analysis
        from analyzers import UserProfitAnalyzer
        user_profit_analyzer = UserProfitAnalyzer(self.data_manager)
        user_analysis = user_profit_analyzer.get_user_detailed_analysis(team.name)
        
        return {
            "team_info": {
                "id": team.id,
                "name": team.teamname,
                "owner": team.name,
                "points": team.points,
                "team_value": team.team_value,
                "last_access": team.last_access,
                "is_admin": team.is_admin,
                "awards": team.awards,
                "clauses": team.clauses
            },
            "financial_status": {
                "initial_budget": financial_status.initial_budget,
                "current_money": financial_status.current_money,
                "current_team_value": financial_status.current_team_value,
                "total_transaction_profit": financial_status.total_transaction_profit,
                "total_invested": financial_status.total_invested,
                "profit_percentage": financial_status.profit_percentage,
                "transaction_count": financial_status.transaction_count,
                "successful_trades": financial_status.successful_trades,
                "failed_trades": financial_status.failed_trades
            },
            "roster": roster,
            "user_analysis": user_analysis
        }
    
    def save_teams_data(self, teams: List[TeamData]):
        """Save teams data to database"""
        # This would require adding a teams table to the database
        # For now, we'll just log the data
        logger.info(f"Saving {len(teams)} teams data")
        
        # TODO: Implement teams table in database
        # For now, we can store this in a JSON file or extend the database schema
        pass
