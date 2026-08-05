export interface TeamBudget {
  team_id: string;
  team_name: string;
  balance: number;
  initial_budget: number;
  total_spent: number;
  total_income: number;
  purchases_count: number;
  sales_count: number;
  team_value: number;
  performance: number;
  max_bid: number;
}

export interface BalancesResponse {
  success: boolean;
  championship_id: string;
  initial_budget: number;
  teams: TeamBudget[];
}

export interface Transaction {
  player_id: string;
  player_name: string;
  price: number;
  date: string;
  from?: string;  // Para compras: de dónde viene
  to?: string;    // Para ventas: a dónde va
}

export interface TeamDetailResponse {
  success: boolean;
  team_id: string;
  team_name: string;
  balance: number;
  initial_budget: number;
  total_spent: number;
  total_income: number;
  purchases: Transaction[];
  sales: Transaction[];
}

export interface SyncResponse {
  success: boolean;
  championship_id: string;
  sync_type: string;
  results: {
    transactions: {
      status: string;
      records_synced: number;
      last_sync_id: string;
      duration_seconds: number;
    };
  };
}
