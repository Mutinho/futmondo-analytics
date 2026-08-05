import { InfoCardComponent } from '../../../shared/components/info-card.component';
import { Component, inject, signal } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { DecimalPipe } from '@angular/common';
import { AnalyticsService } from '../../../core/services/analytics.service';

@Component({
  selector: 'app-analytics-opportunities',
  standalone: true,
  imports: [MatProgressSpinnerModule, MatTableModule, DecimalPipe, InfoCardComponent],
  template: `
    <h3>⚡ Rachas Activas</h3>
    <app-info-card>Jugadores que llevan varias jornadas consecutivas por encima de un umbral de puntos. Indica jugadores en racha que podrían ser interesantes para fichar.</app-info-card>
    @if (loading()) {
      <div class="loading"><mat-spinner diameter="32" /> Cargando...</div>
    } @else if (!streaks().length) {
      <div class="empty">⚡ No hay rachas activas detectadas.</div>
    } @else {
      <div class="table-container">
        <table mat-table [dataSource]="streaks()">
          <ng-container matColumnDef="name"><th mat-header-cell *matHeaderCellDef>Jugador</th><td mat-cell *matCellDef="let s"><strong>{{ s.name }}</strong></td></ng-container>
          <ng-container matColumnDef="team"><th mat-header-cell *matHeaderCellDef>Equipo</th><td mat-cell *matCellDef="let s">{{ s.team }}</td></ng-container>
          <ng-container matColumnDef="streak"><th mat-header-cell *matHeaderCellDef>Racha</th><td mat-cell *matCellDef="let s" class="streak">🔥 {{ s.streak }} jornadas</td></ng-container>
          <ng-container matColumnDef="average"><th mat-header-cell *matHeaderCellDef>Media en racha</th><td mat-cell *matCellDef="let s">{{ s.average | number:'1.1-1' }}</td></ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
    }
  `,
  styles: [`.loading { display: flex; align-items: center; gap: 12px; padding: 32px; color: var(--mat-sys-on-surface-variant); } .empty { text-align: center; padding: 48px; color: var(--mat-sys-on-surface-variant); } .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); } table { width: 100%; } .streak { color: #FF9800; font-weight: 700; } .section-desc { color: #666666; font-size: 13px; margin: -4px 0 20px; }`]
})
export class OpportunitiesComponent {
  private svc = inject(AnalyticsService);
  loading = signal(true);
  streaks = signal<any[]>([]);
  columns = ['name', 'team', 'streak', 'average'];
  constructor() { this.load(); }
  async load() {
    try { const d = await this.svc.getStreaks(); this.streaks.set(d?.streaks || d?.players || []); }
    catch {}
    finally { this.loading.set(false); }
  }
}
