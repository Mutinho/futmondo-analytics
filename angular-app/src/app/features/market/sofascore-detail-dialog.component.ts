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
  matches_started: number | null;
  starter_pct: number | null;
  minutes_played: number | null;
  yellow_cards: number | null;
  red_cards: number | null;
  tournament: string | null;
  season: string | null;
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
  templateUrl: './sofascore-detail-dialog.component.html',
  styleUrl: './sofascore-detail-dialog.component.scss'
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

      const response = await firstValueFrom(
        this.http.get<{ success: boolean; player: SofascoreStats }>(`/api/v1/sofascore/player/${encodeURIComponent(this.data.player_name)}`, { params })
      );
      if (response.player) {
        this.stats.set(response.player);
      } else {
        this.error.set('No se encontraron datos.');
      }
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

  getStarterClass(pct: number | null | undefined): string {
    if (pct == null) return '';
    if (pct >= 80) return 'starter-80';
    if (pct >= 60) return 'starter-60';
    if (pct >= 40) return 'starter-40';
    if (pct >= 20) return 'starter-20';
    return 'starter-0';
  }
}
