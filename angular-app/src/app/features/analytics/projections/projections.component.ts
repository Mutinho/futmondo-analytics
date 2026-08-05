import { InfoCardComponent } from '../../../shared/components/info-card.component';
import { Component, inject, signal } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { DatePipe } from '@angular/common';
import { AnalyticsService } from '../../../core/services/analytics.service';

@Component({
  selector: 'app-analytics-projections',
  standalone: true,
  imports: [MatProgressSpinnerModule, MatCardModule, DatePipe, InfoCardComponent],
  template: `
    <h3>🎯 Proyecciones de la Próxima Jornada</h3>
    <app-info-card>Dificultad estimada de cada partido de la próxima jornada combinando las cuotas de apuestas y la forma de los equipos.</app-info-card>
    @if (loading()) {
      <div class="loading"><mat-spinner diameter="32" /> Calculando proyecciones...</div>
    } @else if (!matches().length) {
      <div class="empty">🎯 No hay proyecciones disponibles todavía.</div>
    } @else {
      <div class="matches-grid">
        @for (match of matches(); track match) {
          <mat-card class="match-card">
            <mat-card-header>
              <mat-card-title>{{ match.home?.team_name || 'Local' }} vs {{ match.away?.team_name || 'Visitante' }}</mat-card-title>
              <mat-card-subtitle>{{ match.match_date | date:'medium' }}</mat-card-subtitle>
            </mat-card-header>
            <mat-card-content>
              <div class="difficulty-row">
                <span>Local: <strong [class]="getDiffClass(match.home?.difficulty)">{{ getDiffLabel(match.home?.difficulty) }}</strong></span>
                <span>Visitante: <strong [class]="getDiffClass(match.away?.difficulty)">{{ getDiffLabel(match.away?.difficulty) }}</strong></span>
              </div>
            </mat-card-content>
          </mat-card>
        }
      </div>
    }
  `,
  styles: [`
    .loading { display: flex; align-items: center; gap: 12px; padding: 32px; color: var(--mat-sys-on-surface-variant); }
    .empty { text-align: center; padding: 48px; color: var(--mat-sys-on-surface-variant); }
    .matches-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
    .match-card { margin-bottom: 0; }
    .difficulty-row { display: flex; justify-content: space-between; padding-top: 8px; }
    .easy { color: #16a34a; }
    .hard { color: #dc2626; }
    .neutral { color: #d97706; }
    .section-desc { color: #666666; font-size: 13px; margin: -4px 0 20px; }
  `]
})
export class ProjectionsComponent {
  private svc = inject(AnalyticsService);
  loading = signal(true);
  matches = signal<any[]>([]);

  constructor() { this.load(); }

  async load() {
    try { const d = await this.svc.getProjections(); this.matches.set(d?.matches || []); }
    catch {}
    finally { this.loading.set(false); }
  }

  getDiffClass(value: number | null): string {
    if (value == null) return 'neutral';
    if (value <= -0.1) return 'easy';
    if (value >= 0.1) return 'hard';
    return 'neutral';
  }

  getDiffLabel(value: number | null): string {
    if (value == null) return 'Sin datos';
    if (value <= -0.1) return 'Favorable';
    if (value >= 0.1) return 'Complicado';
    return 'Neutral';
  }
}
