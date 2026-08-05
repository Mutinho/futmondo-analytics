import { Component, inject, signal } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { ChampionshipService } from '../../core/services/championship.service';
import { DecimalPipe } from '@angular/common';

interface SofascoreStats {
  player_name: string;
  rating: number | null;
  goals: number | null;
  assists: number | null;
  appearances: number | null;
  minutes_played: number | null;
  yellow_cards: number | null;
  red_cards: number | null;
  tournament: string | null;
  season: string | null;
  position: string | null;
  nationality: string | null;
  age: number | null;
  successful_dribbles: number | null;
  accurate_passes_pct: number | null;
  shots_on_target: number | null;
  tackles: number | null;
  interceptions: number | null;
  clean_sheets: number | null;
  saves: number | null;
  synced_at: string | null;
}

@Component({
  selector: 'app-sofascore-detail-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule, MatProgressSpinnerModule, MatIconModule, MatCardModule, DecimalPipe],
  template: `
    <h2 mat-dialog-title>⚽ {{ data.player_name }}</h2>
    <mat-dialog-content>
      @if (loading()) {
        <div class="loading">
          <mat-spinner diameter="36" />
          <span>Cargando stats de Sofascore...</span>
        </div>
      } @else if (error()) {
        <div class="error-msg">
          <mat-icon>error</mat-icon>
          <span>{{ error() }}</span>
        </div>
      } @else if (stats()) {
        <!-- Rating grande -->
        <div class="rating-hero">
          <div class="rating-circle" [class]="getRatingClass(stats()!.rating)">
            {{ stats()!.rating ? (stats()!.rating! | number:'1.1-1') : '-' }}
          </div>
          <div class="rating-meta">
            @if (stats()!.position) { <span class="meta-item">📋 {{ stats()!.position }}</span> }
            @if (stats()!.nationality) { <span class="meta-item">🌍 {{ stats()!.nationality }}</span> }
            @if (stats()!.age) { <span class="meta-item">🎂 {{ stats()!.age }} años</span> }
            @if (stats()!.tournament) { <span class="meta-item">🏆 {{ stats()!.tournament }}</span> }
            @if (stats()!.season) { <span class="meta-item">📅 {{ stats()!.season }}</span> }
          </div>
        </div>

        <!-- Stats grid -->
        <div class="stats-grid">
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-value">{{ stats()!.appearances ?? '-' }}</div>
              <div class="stat-label">Partidos</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-value">{{ stats()!.minutes_played ?? '-' }}</div>
              <div class="stat-label">Minutos</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card goals">
            <mat-card-content>
              <div class="stat-value">{{ stats()!.goals ?? '-' }}</div>
              <div class="stat-label">Goles</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card assists">
            <mat-card-content>
              <div class="stat-value">{{ stats()!.assists ?? '-' }}</div>
              <div class="stat-label">Asistencias</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-value yellow">{{ stats()!.yellow_cards ?? '-' }}</div>
              <div class="stat-label">Amarillas</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-value red">{{ stats()!.red_cards ?? '-' }}</div>
              <div class="stat-label">Rojas</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-value">{{ stats()!.accurate_passes_pct != null ? (stats()!.accurate_passes_pct! | number:'1.0-1') + '%' : '-' }}</div>
              <div class="stat-label">Pases precisos</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-value">{{ stats()!.successful_dribbles ?? '-' }}</div>
              <div class="stat-label">Regates</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-value">{{ stats()!.shots_on_target ?? '-' }}</div>
              <div class="stat-label">Tiros a puerta</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-value">{{ stats()!.tackles ?? '-' }}</div>
              <div class="stat-label">Tackles</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="stat-card">
            <mat-card-content>
              <div class="stat-value">{{ stats()!.interceptions ?? '-' }}</div>
              <div class="stat-label">Intercepciones</div>
            </mat-card-content>
          </mat-card>
          @if (stats()!.clean_sheets != null) {
            <mat-card class="stat-card">
              <mat-card-content>
                <div class="stat-value">{{ stats()!.clean_sheets }}</div>
                <div class="stat-label">Porterías a cero</div>
              </mat-card-content>
            </mat-card>
          }
          @if (stats()!.saves != null) {
            <mat-card class="stat-card">
              <mat-card-content>
                <div class="stat-value">{{ stats()!.saves }}</div>
                <div class="stat-label">Paradas</div>
              </mat-card-content>
            </mat-card>
          }
        </div>

        @if (stats()!.synced_at) {
          <p class="synced-at">Última actualización: {{ stats()!.synced_at }}</p>
        }
      }
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cerrar</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .loading { display: flex; align-items: center; gap: 16px; padding: 24px 0; }
    .error-msg { display: flex; align-items: center; gap: 8px; color: var(--mat-sys-error); padding: 16px 0; }
    .rating-hero { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
    .rating-circle {
      width: 72px; height: 72px; border-radius: 50%; display: flex;
      align-items: center; justify-content: center; font-size: 1.6em;
      font-weight: 800; color: #fff; flex-shrink: 0;
    }
    .rating-circle.rating-green { background: #16a34a; }
    .rating-circle.rating-yellow { background: #ca8a04; }
    .rating-circle.rating-red { background: #dc2626; }
    .rating-circle.rating-none { background: #6b7280; }
    .rating-meta { display: flex; flex-direction: column; gap: 4px; }
    .meta-item { font-size: 0.9em; color: var(--mat-sys-on-surface-variant); }
    .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .stat-card { text-align: center; }
    .stat-value { font-size: 1.4em; font-weight: 700; }
    .stat-value.yellow { color: #ca8a04; }
    .stat-value.red { color: #dc2626; }
    .stat-label { font-size: 0.75em; color: var(--mat-sys-on-surface-variant); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }
    .stat-card.goals .stat-value { color: #16a34a; }
    .stat-card.assists .stat-value { color: #2563eb; }
    .synced-at { font-size: 0.75em; color: var(--mat-sys-on-surface-variant); margin-top: 16px; text-align: right; }
    mat-dialog-content { min-width: 400px; max-width: 550px; }
  `]
})
export class SofascoreDetailDialogComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);
  data = inject<{ player_name: string }>(MAT_DIALOG_DATA);

  loading = signal(true);
  error = signal('');
  stats = signal<SofascoreStats | null>(null);

  constructor() {
    this.loadStats();
  }

  async loadStats() {
    try {
      let params = new HttpParams();
      const champId = this.championshipService.activeId();
      if (champId) params = params.set('championship_id', champId);

      const data = await firstValueFrom(
        this.http.get<SofascoreStats>(`/api/v1/sofascore/player/${encodeURIComponent(this.data.player_name)}`, { params })
      );
      this.stats.set(data);
    } catch (err: any) {
      if (err.status === 404) {
        this.error.set('No se encontraron datos de Sofascore para este jugador.');
      } else {
        this.error.set(err.message || 'Error cargando stats');
      }
    } finally {
      this.loading.set(false);
    }
  }

  getRatingClass(rating: number | null | undefined): string {
    if (rating == null) return 'rating-none';
    if (rating >= 7) return 'rating-green';
    if (rating >= 6) return 'rating-yellow';
    return 'rating-red';
  }
}
