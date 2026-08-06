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

const STORAGE_KEY = 'futmondo_active_championship';

@Injectable({ providedIn: 'root' })
export class ChampionshipService {
  private http = inject(HttpClient);
  private loading = false;

  championships = signal<Championship[]>([]);
  activeChampionship = signal<Championship | null>(null);

  // Se inicializa directo de localStorage — disponible inmediatamente sin esperar HTTP
  activeId = signal<string>(localStorage.getItem(STORAGE_KEY) || '');

  hasClauses = computed(() => this.activeChampionship()?.has_clauses || false);

  async load() {
    if (this.loading) return;
    this.loading = true;

    try {
      const data = await firstValueFrom(this.http.get<ChampionshipsResponse>('/api/v1/user/championships'));
      this.championships.set(data.championships);
    } catch {
      try {
        const data = await firstValueFrom(this.http.get<ChampionshipsResponse>('/api/v1/championships'));
        this.championships.set(data.championships);
      } catch {
        this.championships.set([]);
        this.loading = false;
        return;
      }
    }

    // Recuperar selección de localStorage
    const saved = this.activeId()
      ? this.championships().find(c => c.championship_id === this.activeId())
      : null;

    if (saved) {
      this.activeChampionship.set(saved);
    } else if (this.championships().length) {
      this.setActive(this.championships()[0]);
    }

    this.loading = false;
  }

  setActive(championship: Championship) {
    this.activeChampionship.set(championship);
    this.activeId.set(championship.championship_id);
    localStorage.setItem(STORAGE_KEY, championship.championship_id);
  }
}
