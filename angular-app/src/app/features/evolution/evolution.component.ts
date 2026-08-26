import { Component, ChangeDetectionStrategy, inject, signal, effect } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions } from 'chart.js';
import { EvolutionService } from '../../core/services/evolution.service';
import { ChampionshipService } from '../../core/services/championship.service';
import { PageHeaderComponent } from '../../shared/components/page-header.component';
import { TeamEvolution } from '../../core/models/evolution.model';

// Colores para los equipos
const TEAM_COLORS = [
  '#4CAF50', '#2196F3', '#FF9800', '#9C27B0',
  '#F44336', '#00BCD4', '#795548', '#607D8B',
  '#E91E63', '#3F51B5',
];

@Component({
  selector: 'app-evolution',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [MatProgressSpinnerModule, BaseChartDirective, PageHeaderComponent],
  templateUrl: './evolution.component.html',
  styleUrl: './evolution.component.scss',
})
export class EvolutionComponent {
  private evolutionService = inject(EvolutionService);
  private championshipService = inject(ChampionshipService);

  loading = signal(true);
  error = signal('');
  hasData = signal(false);

  pointsChartData = signal<ChartConfiguration<'line'>['data']>({ labels: [], datasets: [] });
  positionsChartData = signal<ChartConfiguration<'line'>['data']>({ labels: [], datasets: [] });

  pointsChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
      title: { display: false },
    },
    scales: {
      y: { title: { display: true, text: 'Puntos' } },
      x: { title: { display: true, text: 'Jornada' } },
    },
  };

  positionsChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
      title: { display: false },
    },
    scales: {
      y: {
        reverse: true,
        title: { display: true, text: 'Posición' },
        ticks: { stepSize: 1 },
        min: 1,
      },
      x: { title: { display: true, text: 'Jornada' } },
    },
  };

  constructor() {
    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadData(id);
    });
  }

  async loadData(championshipId: string) {
    this.loading.set(true);
    this.error.set('');
    try {
      const response = await this.evolutionService.getEvolution(championshipId);
      const data = response.data;

      if (!data.matchdays.length || !data.teams.length) {
        this.hasData.set(false);
        return;
      }

      this.hasData.set(true);
      const labels = data.matchdays.map(m => `J${m}`);

      this.pointsChartData.set({
        labels,
        datasets: data.teams.map((team, i) => ({
          label: team.team_name,
          data: team.points_evolution,
          borderColor: TEAM_COLORS[i % TEAM_COLORS.length],
          backgroundColor: TEAM_COLORS[i % TEAM_COLORS.length] + '20',
          tension: 0.3,
          pointRadius: 3,
        })),
      });

      this.positionsChartData.set({
        labels,
        datasets: data.teams.map((team, i) => ({
          label: team.team_name,
          data: team.positions_evolution,
          borderColor: TEAM_COLORS[i % TEAM_COLORS.length],
          backgroundColor: TEAM_COLORS[i % TEAM_COLORS.length] + '20',
          tension: 0.3,
          pointRadius: 4,
        })),
      });
    } catch (err: any) {
      this.error.set(err.message || 'Error cargando evolución');
    } finally {
      this.loading.set(false);
    }
  }
}
