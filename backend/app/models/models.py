#!/usr/bin/env python3
"""
Pydantic models for FastAPI
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# Base response models
class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None

# Authentication models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user_id: Optional[str] = None
    message: str

# Player models
class PlayerData(BaseModel):
    id: str
    name: str
    role: str
    team: str
    current_value: int
    current_points: int
    userteam_id: Optional[str] = None
    userteam_name: Optional[str] = None
    average_performance: Optional[Dict] = None

class PlayerTransactionAnalysis(BaseModel):
    player_id: str
    player_name: str
    role: str
    team: str
    current_value: int
    current_points: int
    profit_analysis: Dict
    average_performance: Optional[Dict] = None

# User models
class UserProfitData(BaseModel):
    user_id: str
    username: str
    team_id: str
    team_name: str
    total_profit: float
    total_transactions: int
    successful_trades: int
    failed_trades: int
    best_profit: float
    worst_loss: float
    avg_profit_per_trade: float
    profit_percentage: float

class UserDetailAnalysis(BaseModel):
    username: str
    total_transactions: int
    player_analysis: Dict

# Team models
class TeamData(BaseModel):
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

class TeamFinancialStatus(BaseModel):
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

class TeamMoneyFlow(BaseModel):
    team_name: str
    owner_name: str
    initial_budget: int
    current_team_value: int
    total_spent: int
    total_received: int
    current_money: float
    transaction_breakdown: List[Dict]
    summary: str

class TeamDetailAnalysis(BaseModel):
    team_info: Dict
    financial_status: Dict
    roster: Optional[List[Dict]] = None
    user_analysis: Optional[Dict] = None

# Database stats model
class DatabaseStats(BaseModel):
    total_players: int
    total_transactions: int
    users_analyzed: int
    cache_status: Dict

# Request models
class UpdateDataRequest(BaseModel):
    force_refresh: bool = False

class AnalysisRequest(BaseModel):
    max_players: Optional[int] = None
    force_refresh: bool = False

class TeamAnalysisRequest(BaseModel):
    team_id: str

class UserAnalysisRequest(BaseModel):
    username: str

# Response models for endpoints
class PlayersResponse(BaseResponse):
    data: List[PlayerTransactionAnalysis]

class UsersResponse(BaseResponse):
    data: List[UserProfitData]

class TeamsResponse(BaseResponse):
    data: List[TeamFinancialStatus]

class TeamDetailResponse(BaseResponse):
    data: TeamDetailAnalysis

class TeamMoneyFlowResponse(BaseResponse):
    data: TeamMoneyFlow

class UserDetailResponse(BaseResponse):
    data: UserDetailAnalysis

class DatabaseStatsResponse(BaseResponse):
    data: DatabaseStats

class FullAnalysisResponse(BaseResponse):
    data: Dict[str, Any]
