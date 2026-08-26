import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { PageHeaderComponent } from '../../shared/components/page-header.component';

interface ChampionshipConfig {
  championship_id: string;
  name: string;
  initial_budget: number;
  has_clauses: boolean;
  excluded_teams: string[];
  money_per_point: number;
  money_per_ranking: number;
  dream_team_bonus: number;
  mvp_bonus: number;
  ranking_mode: string;
  users_to_rank: number;
  _excluded_str?: string;
}

@Component({
  selector: 'app-championships-config',
  standalone: true,
  imports: [
    FormsModule, MatCardModule, MatFormFieldModule, MatInputModule,
    MatButtonModule, MatIconModule, MatSlideToggleModule,
    MatProgressSpinnerModule, MatSnackBarModule, MoneyPipe, PageHeaderComponent
  ],
  templateUrl: './championships-config.component.html',
  styleUrl: './championships-config.component.scss'
})
export class ChampionshipsConfigComponent {
  private http = inject(HttpClient);
  private snackBar = inject(MatSnackBar);

  loading = signal(true);
  saving = signal(false);
  championships = signal<ChampionshipConfig[]>([]);

  constructor() {
    this.loadChampionships();
  }

  async loadChampionships() {
    this.loading.set(true);
    try {
      const data = await firstValueFrom(
        this.http.get<{ success: boolean; championships: ChampionshipConfig[] }>('/api/v1/user/championships')
      );
      const champs = (data.championships || []).map(c => ({
        ...c,
        _excluded_str: (c.excluded_teams || []).join(', '),
      }));
      this.championships.set(champs);
    } catch {
      this.snackBar.open('Error cargando campeonatos', 'OK', { duration: 4000 });
    } finally {
      this.loading.set(false);
    }
  }

  async saveChampionship(champ: ChampionshipConfig) {
    this.saving.set(true);
    try {
      const excluded = (champ._excluded_str || '')
        .split(',').map(s => s.trim()).filter(s => s.length > 0);

      await firstValueFrom(
        this.http.post('/api/v1/user/championships', {
          championship_id: champ.championship_id,
          name: champ.name,
          initial_budget: champ.initial_budget,
          has_clauses: champ.has_clauses,
          excluded_teams: excluded,
          money_per_point: champ.money_per_point,
          money_per_ranking: champ.money_per_ranking,
          dream_team_bonus: champ.dream_team_bonus,
          mvp_bonus: champ.mvp_bonus,
          ranking_mode: champ.ranking_mode,
          users_to_rank: champ.users_to_rank,
        })
      );
      this.snackBar.open(`✅ "${champ.name}" guardado`, 'OK', { duration: 3000 });
    } catch {
      this.snackBar.open('Error al guardar', 'OK', { duration: 4000 });
    } finally {
      this.saving.set(false);
    }
  }

  async resyncChampionship(champ: ChampionshipConfig) {
    this.saving.set(true);
    try {
      const data = await firstValueFrom(
        this.http.post<{ success: boolean; configuration: any }>(`/api/v1/user/championships/${champ.championship_id}/resync`, {})
      );
      if (data.configuration) {
        champ.initial_budget = data.configuration.initial_budget;
        champ.has_clauses = data.configuration.has_clauses;
        champ.money_per_point = data.configuration.money_per_point;
        champ.money_per_ranking = data.configuration.money_per_ranking;
        champ.dream_team_bonus = data.configuration.dream_team_bonus;
        champ.mvp_bonus = data.configuration.mvp_bonus;
        champ.ranking_mode = data.configuration.ranking_mode;
        champ.users_to_rank = data.configuration.users_to_rank;
      }
      this.snackBar.open(`🔄 "${champ.name}" resincronizado desde Futmondo`, 'OK', { duration: 3000 });
    } catch {
      this.snackBar.open('Error al resincronizar', 'OK', { duration: 4000 });
    } finally {
      this.saving.set(false);
    }
  }

  async deleteChampionship(champ: ChampionshipConfig) {
    if (!confirm(`¿Eliminar "${champ.name}"?`)) return;

    this.saving.set(true);
    try {
      await firstValueFrom(
        this.http.delete(`/api/v1/user/championships/${champ.championship_id}`)
      );
      this.championships.update(list => list.filter(c => c.championship_id !== champ.championship_id));
      this.snackBar.open(`"${champ.name}" eliminado`, 'OK', { duration: 3000 });
    } catch {
      this.snackBar.open('Error al eliminar', 'OK', { duration: 4000 });
    } finally {
      this.saving.set(false);
    }
  }
}
