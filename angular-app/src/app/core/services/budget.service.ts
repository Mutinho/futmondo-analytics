import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { BalancesResponse, TeamDetailResponse, SyncResponse } from '../models/budget.model';

@Injectable({ providedIn: 'root' })
export class BudgetService {
  private http = inject(HttpClient);
  private baseUrl = '/api/v1/analytics';

  getBalances(championshipId?: string): Promise<BalancesResponse> {
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    return firstValueFrom(this.http.get<BalancesResponse>(`${this.baseUrl}/balances`, { params }));
  }

  getTeamDetail(teamId: string, championshipId?: string): Promise<TeamDetailResponse> {
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    return firstValueFrom(this.http.get<TeamDetailResponse>(`${this.baseUrl}/balances/${teamId}`, { params }));
  }

  syncTransactions(championshipId?: string): Promise<SyncResponse> {
    let params = new HttpParams();
    params = params.set('sync_type', 'all');
    if (championshipId) params = params.set('championship_id', championshipId);
    return firstValueFrom(this.http.post<SyncResponse>('/api/v1/sync/trigger', {}, { params }));
  }
}
