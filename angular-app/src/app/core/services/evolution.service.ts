import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { EvolutionResponse } from '../models/evolution.model';

@Injectable({ providedIn: 'root' })
export class EvolutionService {
  private http = inject(HttpClient);

  private cache = signal<EvolutionResponse | null>(null);
  private cacheKey = '';
  private cacheExpiry = 0;

  async getEvolution(championshipId?: string): Promise<EvolutionResponse> {
    const key = championshipId || 'default';
    if (this.cacheKey === key && this.cache() && Date.now() < this.cacheExpiry) {
      return this.cache()!;
    }
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    const res = await firstValueFrom(this.http.get<EvolutionResponse>('/api/v1/matchdays/evolution', { params }));
    this.cache.set(res);
    this.cacheKey = key;
    this.cacheExpiry = Date.now() + 5 * 60_000; // 5 min TTL
    return res;
  }
}
