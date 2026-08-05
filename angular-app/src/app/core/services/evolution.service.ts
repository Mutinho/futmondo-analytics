import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { EvolutionResponse } from '../models/evolution.model';

@Injectable({ providedIn: 'root' })
export class EvolutionService {
  private http = inject(HttpClient);

  getEvolution(): Promise<EvolutionResponse> {
    return firstValueFrom(this.http.get<EvolutionResponse>('/api/v1/matchdays/evolution'));
  }
}
