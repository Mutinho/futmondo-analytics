import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class RosterService {
  private http = inject(HttpClient);
  private baseUrl = '/api/v1/roster';

  getMyRoster(championshipId: string): Promise<any> {
    const params = new HttpParams().set('championship_id', championshipId);
    return firstValueFrom(this.http.get(`${this.baseUrl}/my`, { params }));
  }

  getOnSale(championshipId: string): Promise<any> {
    const params = new HttpParams().set('championship_id', championshipId);
    return firstValueFrom(this.http.get(`${this.baseUrl}/on-sale`, { params }));
  }

  sell(championshipId: string, playerIds: string[]): Promise<any> {
    return firstValueFrom(this.http.post(`${this.baseUrl}/sell`, {
      championship_id: championshipId,
      player_ids: playerIds,
    }));
  }

  cancelSale(championshipId: string, playerId: string): Promise<any> {
    return firstValueFrom(this.http.post(`${this.baseUrl}/cancel-sale`, {
      championship_id: championshipId,
      player_id: playerId,
    }));
  }
}
