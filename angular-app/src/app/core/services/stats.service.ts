import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { UserStatsResponse, PlayerFinancesResponse, ClausulableResponse } from '../models/stats.model';

@Injectable({ providedIn: 'root' })
export class StatsService {
  private http = inject(HttpClient);

  getUserStats(): Promise<UserStatsResponse> {
    return firstValueFrom(this.http.get<UserStatsResponse>('/api/v1/user-stats/'));
  }

  getPlayerFinances(): Promise<PlayerFinancesResponse> {
    return firstValueFrom(this.http.get<PlayerFinancesResponse>('/api/v1/player-finances/'));
  }

  getClausulablePlayers(): Promise<ClausulableResponse> {
    return firstValueFrom(this.http.get<ClausulableResponse>('/api/v1/clausulable-players/'));
  }
}
