import { Component, inject, signal } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions } from 'chart.js';
import { StatsService } from '../../core/services/stats.service';
import { UserStats } from '../../core/models/stats.model';

const COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4', '#795548', '#607D8B', '#E91E63'];

@Component({
  selector: 'app-stats',
  standalone: true,
  imports: [MatProgressSpinnerModule, BaseChartDirective],
  template: `
    <h1>📈 Estadísticas</h1>

    @if (loading()) {
      <div class="loading-container">
        <mat-spinner diameter="40" />
        <span>Cargando estadísticas...</span>
      </div>
    } @else if (error()) {
      <div class="error-message">{{ error() }}</div>
    } @else if (!hasData()) {
      <div class="empty-state">
        <p>📊 No hay estadísticas disponibles todavía.</p>
      </div>
    } @else {
      <div class="charts-grid">
        <div class="chart-card">
          <h2>🔄 Operaciones por Equipo</h2>
          <div class="chart-wrapper">
            <canvas baseChart type="bar" [data]="opsChartData()" [options]="chartOptions"></canvas>
          </div>
        </div>
        <div class="chart-card">
          <h2>💸 Gasto Neto por Equipo</h2>
          <div class="chart-wrapper">
            <canvas baseChart type="bar" [data]="spentChartData()" [options]="chartOptions"></canvas>
          </div>
        </div>
      </div>
    }
  `,
  styles: [`
    .loading-container { display: flex; align-items: center; gap: 16px; padding: 40px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .error-message { padding: 16px; background: var(--mat-sys-error-container); color: var(--mat-sys-on-error-container); border-radius: 8px; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); }
    .charts-grid { display: grid; gap: 24px; }
    .chart-card { background: var(--mat-sys-surface); border-radius: 12px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); h2 { margin: 0 0 16px; font-size: 1.1em; } }
    .chart-wrapper { position: relative; height: 300px; }
  `]
})
export class StatsComponent {
  private statsService = inject(StatsService);

  loading = signal(true);
  error = signal('');
  hasData = signal(false);

  opsChartData = signal<ChartConfiguration<'bar'>['data']>({ labels: [], datasets: [] });
  spentChartData = signal<ChartConfiguration<'bar'>['data']>({ labels: [], datasets: [] });

  chartOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
  };

  constructor() {
    this.loadData();
  }

  async loadData() {
    this.loading.set(true);
    try {
      const data = await this.statsService.getUserStats();
      if (!data.users.length) { this.hasData.set(false); return; }

      // Excluir Mercado y javier.ortega
      const EXCLUDED_IDS = new Set(['market_team', 'market_user', '6a5f95dd7b7923198912eb44']);
      const EXCLUDED_NAMES = new Set(['mercado', 'javier.ortega']);
      const filtered = data.users.filter(u =>
        !EXCLUDED_IDS.has(u.team_id) &&
        !EXCLUDED_IDS.has(u.user_id) &&
        !EXCLUDED_NAMES.has(u.team_name.toLowerCase()) &&
        !EXCLUDED_NAMES.has(u.username.toLowerCase())
      );

      if (!filtered.length) { this.hasData.set(false); return; }

      this.hasData.set(true);
      const users = filtered.sort((a, b) => b.transaction_count - a.transaction_count);
      const labels = users.map(u => u.team_name);

      this.opsChartData.set({
        labels,
        datasets: [{
          data: users.map(u => u.transaction_count),
          backgroundColor: COLORS,
        }],
      });

      this.spentChartData.set({
        labels,
        datasets: [{
          data: users.map(u => u.total_spent - u.total_received),
          backgroundColor: users.map(u => (u.total_spent - u.total_received) >= 0 ? '#dc2626' : '#16a34a'),
        }],
      });
    } catch (err: any) {
      this.error.set(err.message || 'Error');
    } finally {
      this.loading.set(false);
    }
  }
}
