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
    MatProgressSpinnerModule, MatSnackBarModule, MoneyPipe
  ],
  template: `
    <div class="settings-container">
      <h2>Configuración de Campeonatos</h2>
      <p class="description">Configuración de tus campeonatos. Puedes resincronizar los valores desde Futmondo o editarlos manualmente.</p>

      @if (loading()) {
        <div class="loading">
          <mat-spinner diameter="36" />
          <span>Cargando campeonatos...</span>
        </div>
      } @else if (championships().length === 0) {
        <div class="empty">
          <mat-icon>sports_soccer</mat-icon>
          <p>No hay campeonatos configurados. Se detectarán automáticamente al iniciar sesión.</p>
        </div>
      } @else {
        <div class="championships-list">
          @for (champ of championships(); track champ.championship_id) {
            <mat-card class="champ-card">
              <mat-card-header>
                <mat-card-title>{{ champ.name }}</mat-card-title>
                <mat-card-subtitle>{{ champ.championship_id }}</mat-card-subtitle>
              </mat-card-header>
              <mat-card-content>
                <!-- Row 1: Budget + Clauses (read-only from API) -->
                <div class="config-row">
                  <mat-form-field appearance="outline" class="field-md">
                    <mat-label>Presupuesto inicial</mat-label>
                    <input matInput type="number" [(ngModel)]="champ.initial_budget" [disabled]="true" />
                  </mat-form-field>
                  <mat-slide-toggle [(ngModel)]="champ.has_clauses" [disabled]="true">
                    Cláusulas
                  </mat-slide-toggle>
                </div>

                <!-- Row 2: Money config (read-only from API) -->
                <div class="config-row">
                  <mat-form-field appearance="outline" class="field-sm">
                    <mat-label>€ / punto</mat-label>
                    <input matInput type="number" [(ngModel)]="champ.money_per_point" [disabled]="true" />
                  </mat-form-field>
                  <mat-form-field appearance="outline" class="field-sm">
                    <mat-label>€ / clasificación</mat-label>
                    <input matInput type="number" [(ngModel)]="champ.money_per_ranking" [disabled]="true" />
                  </mat-form-field>
                  <mat-form-field appearance="outline" class="field-sm">
                    <mat-label>€ dream team</mat-label>
                    <input matInput type="number" [(ngModel)]="champ.dream_team_bonus" [disabled]="true" />
                  </mat-form-field>
                  <mat-form-field appearance="outline" class="field-sm">
                    <mat-label>€ MVP</mat-label>
                    <input matInput type="number" [(ngModel)]="champ.mvp_bonus" [disabled]="true" />
                  </mat-form-field>
                </div>

                <!-- Row 3: Ranking config (read-only from API) -->
                <div class="config-row">
                  <mat-form-field appearance="outline" class="field-sm">
                    <mat-label>Modo ranking</mat-label>
                    <input matInput [value]="champ.ranking_mode === 'flop' ? 'Últimos' : 'Primeros'" [disabled]="true" />
                  </mat-form-field>
                  <mat-form-field appearance="outline" class="field-sm">
                    <mat-label>Usuarios a rankear</mat-label>
                    <input matInput [value]="champ.users_to_rank === -1 ? 'Todos' : champ.users_to_rank" [disabled]="true" />
                  </mat-form-field>
                </div>

                <!-- Row 4: Excluded teams (editable) -->
                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Equipos excluidos (IDs separados por coma)</mat-label>
                  <input matInput [(ngModel)]="champ._excluded_str" [disabled]="saving()" placeholder="team_id_1, team_id_2" />
                  <mat-icon matPrefix>block</mat-icon>
                </mat-form-field>
              </mat-card-content>
              <mat-card-actions align="end">
                <button mat-button color="warn" (click)="deleteChampionship(champ)" [disabled]="saving()">
                  <mat-icon>delete</mat-icon> Eliminar
                </button>
                <button mat-button (click)="resyncChampionship(champ)" [disabled]="saving()">
                  <mat-icon>cloud_sync</mat-icon> Resincronizar
                </button>
                <button mat-flat-button color="primary" (click)="saveChampionship(champ)" [disabled]="saving()">
                  <mat-icon>save</mat-icon> Guardar exclusiones
                </button>
              </mat-card-actions>
            </mat-card>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .settings-container { padding: 24px; max-width: 800px; }
    .description { color: var(--mat-sys-on-surface-variant); font-size: 0.9em; margin-bottom: 24px; }
    .loading { display: flex; align-items: center; gap: 16px; padding: 40px; color: var(--mat-sys-on-surface-variant); }
    .empty { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); }
    .empty mat-icon { font-size: 48px; width: 48px; height: 48px; margin-bottom: 16px; }
    .championships-list { display: flex; flex-direction: column; gap: 16px; }
    .champ-card { border-radius: 12px; }
    .config-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-top: 12px; }
    .field-md { width: 200px; }
    .field-sm { width: 150px; }
    .full-width { width: 100%; margin-top: 8px; }
  `]
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
