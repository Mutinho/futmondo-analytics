export interface UserStats {
  team_id: string;
  user_id: string;
  team_name: string;
  username: string;
  unique_players_count: number;
  clauses_paid: number;
  clauses_received: number;
  total_clauses_paid: number;
  total_clauses_received: number;
  transaction_count: number;
  total_spent: number;
  total_received: number;
  transaction_profit: number;
  ideal_team_count: number;
  mvp_count: number;
  total_punishments: number;
  total_bonuses: number;
  net_adjustment: number;
  punishment_count: number;
  bonus_count: number;
}

export interface UserStatsResponse {
  success: boolean;
  championship_id: string;
  total_users: number;
  users: UserStats[];
}

export interface PlayerFinance {
  team_name: string;
  username: string;
  points: number;
  money_per_point: number;
  transaction_profit: number;
  dream_team_count: number;
  mvp_count: number;
  total: number;
}

export interface PlayerFinancesResponse {
  success: boolean;
  championship_id: string;
  total_users: number;
  users: PlayerFinance[];
}

export interface ClausulablePlayer {
  player_id: string;
  player_name: string;
  team: string;
  position: string;
  current_value: number;
  clause_price: number;
  average_points: number;
  score: number;
}

export interface ClausulableResponse {
  success: boolean;
  message?: string;
  players: ClausulablePlayer[];
}
