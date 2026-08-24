import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { EvolutionResponse } from '../models/evolution.model';

@Injectable({ providedIn: 'root' })
export class EvolutionService {
  private http = inject(HttpClient);

  getEvolution(championshipId?: string): Promise<EvolutionResponse> {
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    return firstValueFrom(this.http.get<EvolutionResponse>('/api/v1/matchdays/evolution', { params }));
  }
}
