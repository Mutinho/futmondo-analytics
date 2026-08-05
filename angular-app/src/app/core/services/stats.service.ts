import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { UserStatsResponse, PlayerFinancesResponse, ClausulableResponse } from '../models/stats.model';

@Injectable({ providedIn: 'root' })
export class StatsService {
  private http = inject(HttpClient);

  getUserStats(championshipId?: string): Promise<UserStatsResponse> {
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    return firstValueFrom(this.http.get<UserStatsResponse>('/api/v1/user-stats/', { params }));
  }

  getPlayerFinances(championshipId?: string): Promise<PlayerFinancesResponse> {
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    return firstValueFrom(this.http.get<PlayerFinancesResponse>('/api/v1/player-finances/', { params }));
  }

  getClausulablePlayers(championshipId?: string): Promise<ClausulableResponse> {
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    return firstValueFrom(this.http.get<ClausulableResponse>('/api/v1/clausulable-players/', { params }));
  }
}
