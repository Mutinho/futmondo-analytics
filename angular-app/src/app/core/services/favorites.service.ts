import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class FavoritesService {
  private http = inject(HttpClient);
  private baseUrl = '/api/v1/favorites';

  getMyFavorites(championshipId: string): Promise<any> {
    const params = new HttpParams().set('championship_id', championshipId);
    return firstValueFrom(this.http.get(`${this.baseUrl}/my`, { params }));
  }

  unfollow(championshipId: string, playerId: string): Promise<any> {
    const params = new HttpParams()
      .set('championship_id', championshipId)
      .set('player_id', playerId);
    return firstValueFrom(this.http.post(`${this.baseUrl}/unfollow`, {}, { params }));
  }
}
