import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { UserStatsResponse, PlayerFinancesResponse, ClausulableResponse } from '../models/stats.model';

@Injectable({ providedIn: 'root' })
export class StatsService {
  private http = inject(HttpClient);

  // Cache for user stats
  private userStatsCache = signal<UserStatsResponse | null>(null);
  private userStatsCacheKey = '';
  private userStatsCacheExpiry = 0;

  // Cache for player finances
  private financesCache = signal<PlayerFinancesResponse | null>(null);
  private financesCacheKey = '';
  private financesCacheExpiry = 0;

  // Cache for clausulable players
  private clausulableCache = signal<ClausulableResponse | null>(null);
  private clausulableCacheKey = '';
  private clausulableCacheExpiry = 0;

  async getUserStats(championshipId?: string): Promise<UserStatsResponse> {
    const key = championshipId || 'default';
    if (this.userStatsCacheKey === key && this.userStatsCache() && Date.now() < this.userStatsCacheExpiry) {
      return this.userStatsCache()!;
    }
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    const res = await firstValueFrom(this.http.get<UserStatsResponse>('/api/v1/user-stats/', { params }));
    this.userStatsCache.set(res);
    this.userStatsCacheKey = key;
    this.userStatsCacheExpiry = Date.now() + 5 * 60_000;
    return res;
  }

  async getPlayerFinances(championshipId?: string): Promise<PlayerFinancesResponse> {
    const key = championshipId || 'default';
    if (this.financesCacheKey === key && this.financesCache() && Date.now() < this.financesCacheExpiry) {
      return this.financesCache()!;
    }
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    const res = await firstValueFrom(this.http.get<PlayerFinancesResponse>('/api/v1/player-finances/', { params }));
    this.financesCache.set(res);
    this.financesCacheKey = key;
    this.financesCacheExpiry = Date.now() + 5 * 60_000;
    return res;
  }

  async getClausulablePlayers(championshipId?: string): Promise<ClausulableResponse> {
    const key = championshipId || 'default';
    if (this.clausulableCacheKey === key && this.clausulableCache() && Date.now() < this.clausulableCacheExpiry) {
      return this.clausulableCache()!;
    }
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    const res = await firstValueFrom(this.http.get<ClausulableResponse>('/api/v1/clausulable-players/', { params }));
    this.clausulableCache.set(res);
    this.clausulableCacheKey = key;
    this.clausulableCacheExpiry = Date.now() + 5 * 60_000;
    return res;
  }
}
