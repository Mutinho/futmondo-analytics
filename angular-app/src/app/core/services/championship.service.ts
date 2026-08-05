import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface Championship {
  championship_id: string;
  name: string;
  has_clauses: boolean;
  initial_budget: number;
  excluded_teams: string[];
}

interface ChampionshipsResponse {
  success: boolean;
  championships: Championship[];
}

@Injectable({ providedIn: 'root' })
export class ChampionshipService {
  private http = inject(HttpClient);

  championships = signal<Championship[]>([]);
  activeChampionship = signal<Championship | null>(null);

  // Computed helpers
  activeId = computed(() => this.activeChampionship()?.championship_id || '');
  hasClauses = computed(() => this.activeChampionship()?.has_clauses || false);

  async load() {
    const data = await firstValueFrom(this.http.get<ChampionshipsResponse>('/api/v1/championships'));
    this.championships.set(data.championships);
    // Por defecto seleccionar el primero
    if (data.championships.length && !this.activeChampionship()) {
      this.setActive(data.championships[0]);
    }
  }

  setActive(championship: Championship) {
    this.activeChampionship.set(championship);
  }
}
