import { Component, inject, signal } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { AnalyticsService } from '../../../core/services/analytics.service';

@Component({
  selector: 'app-analytics-overview',
  standalone: true,
  imports: [MatProgressSpinnerModule, MatTableModule],
  template: `
    @if (loading()) {
      <div class="loading"><mat-spinner diameter="32" /> Cargando visión general...</div>
    } @else if (!hasData()) {
      <div class="empty">🌐 No hay datos de jornadas disponibles para mostrar tendencias.</div>
    } @else {
      <h3>📊 Tendencias (últimas 5 jornadas)</h3>
      <div class="table-container">
        <table mat-table [dataSource]="trends()">
          <ng-container matColumnDef="team_name">
            <th mat-header-cell *matHeaderCellDef>Equipo</th>
            <td mat-cell *matCellDef="let t">{{ t.team_name }}</td>
          </ng-container>
          <ng-container matColumnDef="points">
            <th mat-header-cell *matHeaderCellDef>Puntos</th>
            <td mat-cell *matCellDef="let t">{{ t.points }}</td>
          </ng-container>
          <ng-container matColumnDef="position">
            <th mat-header-cell *matHeaderCellDef>Posición</th>
            <td mat-cell *matCellDef="let t">{{ t.position }}</td>
          </ng-container>
          <ng-container matColumnDef="momentum">
            <th mat-header-cell *matHeaderCellDef>Momentum</th>
            <td mat-cell *matCellDef="let t" [style.color]="t.momentum >= 0 ? '#16a34a' : '#dc2626'">
              {{ t.momentum > 0 ? '+' : '' }}{{ t.momentum?.toFixed(1) }}
            </td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
    }
  `,
  styles: [`
    .loading { display: flex; align-items: center; gap: 12px; padding: 32px; color: var(--mat-sys-on-surface-variant); }
    .empty { text-align: center; padding: 48px; color: var(--mat-sys-on-surface-variant); }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
  `]
})
export class OverviewComponent {
  private analyticsService = inject(AnalyticsService);
  loading = signal(true);
  hasData = signal(false);
  trends = signal<any[]>([]);
  columns = ['team_name', 'points', 'position', 'momentum'];

  constructor() { this.load(); }

  async load() {
    try {
      const data = await this.analyticsService.getTrends();
      const teams = data?.teams || data?.data?.teams || [];
      this.trends.set(teams);
      this.hasData.set(teams.length > 0);
    } catch { this.hasData.set(false); }
    finally { this.loading.set(false); }
  }
}
