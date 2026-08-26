import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

// === Response Interfaces ===

export interface TeamTrend {
  team_id: string;
  team_name: string;
  history: { matchday: number; points: number }[];
  total_points: number;
  position_delta: number;
  average_points: number;
  momentum: number;
}

export interface TrendsResponse {
  championship_id: string;
  latest_matchday: number;
  teams: TeamTrend[];
}

export interface ClassificationTeam {
  team_id: string;
  team_name: string;
  user_id: string;
  username: string;
  matches_count: number;
  total_points: number;
  average_points: number;
  max_points: number;
  min_points: number;
  volatility: number;
  trend: number;
  points_by_matchday: Record<string, number>;
  matchdays: number[];
  last_matchday: number;
  rank: number;
}

export interface CustomClassificationResponse {
  championship_id: string;
  latest_matchday: number;
  window: number;
  excluded_matchdays: number[];
  available_matchdays: number[];
  included_matchdays: number[];
  classification: ClassificationTeam[];
}

export interface HeatmapMatchday {
  matchday: number;
  scores: Record<string, number>;
}

export interface HeatmapResponse {
  championship_id: string;
  latest_matchday: number;
  matchdays: HeatmapMatchday[];
}

export interface ClassificationFullTeam {
  team_id: string;
  team_name: string;
  total_points: number;
  average_points: number;
  matches_count: number;
  max_points: number;
  min_points: number;
  trend: number;
  momentum: number;
  rank: number;
}

export interface ClassificationFullResponse {
  championship_id: string;
  latest_matchday: number;
  window: number | null;
  included_matchdays: number[];
  classification: ClassificationFullTeam[];
}

export interface PlayerForm {
  player_id: string;
  name: string;
  matches: number;
  average_points: number;
  trend: number;
  last_matchday: number;
  last_points: number;
}

export interface PlayerFormResponse {
  championship_id: string;
  window: number;
  players: PlayerForm[];
}

export interface PlayerValueTrend {
  player_id: string;
  name: string;
  current_value: number;
  previous_value: number;
  change: number;
  change_pct: number;
}

export interface PlayerValueTrendResponse {
  championship_id: string;
  window: number;
  players: PlayerValueTrend[];
}

export interface TeamConsistency {
  team_id: string;
  team_name: string;
  matches: number;
  average_points: number;
  consistency_index: number;
  volatility: number;
}

export interface UserConsistencyResponse {
  championship_id: string;
  window: number;
  teams: TeamConsistency[];
}

export interface TeamMarketActivity {
  team_id: string;
  team_name: string;
  transactions: number;
  spent: number;
  received: number;
  clauses_paid: number;
  clauses_received: number;
  clause_total_paid: number;
}

export interface UserMarketActivityResponse {
  championship_id: string;
  window_days: number;
  teams: TeamMarketActivity[];
}

export interface WatchlistPlayer {
  player_id: string;
  name: string;
  slug: string;
  position: string;
  position2: string;
  team: string;
  real_team_id: string;
  value: number;
  change: number;
  average: number;
  ratio: number;
  sofascore_rating: number | null;
  sofascore_url: string | null;
  starter_pct: number | null;
  is_favorite: boolean;
  streak: number;
  trend: number;
}

export interface WatchlistResponse {
  championship_id: string;
  total: number;
  players: WatchlistPlayer[];
}

export interface ClauseEdge {
  from_team_id: string;
  from_team_name: string;
  to_team_id: string;
  to_team_name: string;
  amount: number;
  count: number;
}

export interface ClauseNetworkResponse {
  championship_id: string;
  edges: ClauseEdge[];
}

export interface PlayerStreak {
  player_id: string;
  name: string;
  streak_length: number;
  streak_type: string;
  average_in_streak: number;
}

export interface StreaksResponse {
  championship_id: string;
  streaks: PlayerStreak[];
}

export interface ProjectionMatch {
  match_id: string;
  matchday: number;
  match_date: string;
  home: { team_id: string; team_name: string; difficulty: number };
  away: { team_id: string; team_name: string; difficulty: number };
}

export interface ProjectionsResponse {
  championship_id: string;
  target_matchday: number;
  window: number;
  matches: ProjectionMatch[];
}

// === Service ===

@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private http = inject(HttpClient);
  private base = '/api/v1/analytics';

  getTrends(window = 5): Promise<TrendsResponse> {
    return firstValueFrom(this.http.get<TrendsResponse>(`${this.base}/championship/trends`, { params: { window } }));
  }

  getCustomClassification(window = 5, excludeMatchdays?: number[]): Promise<CustomClassificationResponse> {
    let params = new HttpParams().set('window', window);
    if (excludeMatchdays?.length) {
      excludeMatchdays.forEach(m => params = params.append('exclude_matchday', m));
    }
    return firstValueFrom(this.http.get<CustomClassificationResponse>(`${this.base}/championship/custom-classification`, { params }));
  }

  getHeatmap(): Promise<HeatmapResponse> {
    return firstValueFrom(this.http.get<HeatmapResponse>(`${this.base}/championship/heatmap`));
  }

  getPlayerForm(window = 5): Promise<PlayerFormResponse> {
    return firstValueFrom(this.http.get<PlayerFormResponse>(`${this.base}/players/form`, { params: { window } }));
  }

  getPlayerValueTrend(window = 30): Promise<PlayerValueTrendResponse> {
    return firstValueFrom(this.http.get<PlayerValueTrendResponse>(`${this.base}/players/value-trend`, { params: { window } }));
  }

  getUserConsistency(window = 5): Promise<UserConsistencyResponse> {
    return firstValueFrom(this.http.get<UserConsistencyResponse>(`${this.base}/users/consistency`, { params: { window } }));
  }

  getUserMarketActivity(windowDays = 30): Promise<UserMarketActivityResponse> {
    return firstValueFrom(this.http.get<UserMarketActivityResponse>(`${this.base}/users/market-activity`, { params: { window_days: windowDays } }));
  }

  getWatchlist(championshipId?: string): Promise<WatchlistResponse> {
    const params: Record<string, string> = {};
    if (championshipId) params['championship_id'] = championshipId;
    return firstValueFrom(this.http.get<WatchlistResponse>(`${this.base}/market/watchlist`, { params }));
  }

  getClassificationFull(window?: number, championshipId?: string): Promise<ClassificationFullResponse> {
    const params: Record<string, string | number> = {};
    if (window) params['window'] = window;
    if (championshipId) params['championship_id'] = championshipId;
    return firstValueFrom(this.http.get<ClassificationFullResponse>(`${this.base}/championship/classification-full`, { params }));
  }

  getClauseNetwork(): Promise<ClauseNetworkResponse> {
    return firstValueFrom(this.http.get<ClauseNetworkResponse>(`${this.base}/clauses/network`));
  }

  getStreaks(minStreak = 3, threshold = 5): Promise<StreaksResponse> {
    return firstValueFrom(this.http.get<StreaksResponse>(`${this.base}/opportunities/streaks`, { params: { min_streak: minStreak, threshold } }));
  }

  getProjections(): Promise<ProjectionsResponse> {
    return firstValueFrom(this.http.get<ProjectionsResponse>(`${this.base}/projections/matchday`));
  }
}
