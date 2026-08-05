import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private http = inject(HttpClient);
  private base = '/api/v1/analytics';

  getTrends(window = 5): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/championship/trends`, { params: { window } }));
  }

  getCustomClassification(window = 5, excludeMatchdays?: number[]): Promise<any> {
    let params = new HttpParams().set('window', window);
    if (excludeMatchdays?.length) {
      excludeMatchdays.forEach(m => params = params.append('exclude_matchday', m));
    }
    return firstValueFrom(this.http.get(`${this.base}/championship/custom-classification`, { params }));
  }

  getHeatmap(): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/championship/heatmap`));
  }

  getPlayerForm(window = 5): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/players/form`, { params: { window } }));
  }

  getPlayerValueTrend(window = 30): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/players/value-trend`, { params: { window } }));
  }

  getUserConsistency(window = 5): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/users/consistency`, { params: { window } }));
  }

  getUserMarketActivity(windowDays = 30): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/users/market-activity`, { params: { window_days: windowDays } }));
  }

  getWatchlist(limit = 20): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/market/watchlist`, { params: { limit } }));
  }

  getClauseNetwork(): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/clauses/network`));
  }

  getStreaks(minStreak = 3, threshold = 5): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/opportunities/streaks`, { params: { min_streak: minStreak, threshold } }));
  }

  getProjections(): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/projections/matchday`));
  }
}
