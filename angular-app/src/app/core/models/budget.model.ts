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
  prizes: number;
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

export interface SyncTriggerResponse {
  success: boolean;
  task_id: string;
  sync_type: string;
  championship_id: string;
  message: string;
}

export interface SyncTaskStepProgress {
  status: string;
  records_synced?: number;
  duration_seconds?: number;
  last_sync_id?: string;
  last_sync_matchday?: number;
}

export interface SyncTaskResponse {
  success: boolean;
  task_id: string;
  sync_type: string;
  championship_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  current_step: string | null;
  progress: Record<string, SyncTaskStepProgress>;
  result: Record<string, SyncTaskStepProgress> | null;
  error: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}
