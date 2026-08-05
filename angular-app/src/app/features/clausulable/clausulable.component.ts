import { Component, inject, signal } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { DecimalPipe } from '@angular/common';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { StatsService } from '../../core/services/stats.service';
import { ClausulablePlayer } from '../../core/models/stats.model';

@Component({
  selector: 'app-clausulable',
  standalone: true,
  imports: [MatTableModule, MatProgressSpinnerModule, DecimalPipe, MoneyPipe],
  template: `
    <h1>⚽ Jugadores Clausulables</h1>
    <p class="description">Jugadores con mejor relación calidad/cláusula para fichar.</p>

    @if (loading()) {
      <div class="loading-container">
        <mat-spinner diameter="40" />
        <span>Cargando jugadores...</span>
      </div>
    } @else if (error()) {
      <div class="error-message">{{ error() }}</div>
    } @else if (!players().length) {
      <div class="empty-state">
        <p>⚽ No hay datos de jugadores clausulables.</p>
        <p>Se mostrarán cuando haya jornadas jugadas y métricas de rendimiento.</p>
      </div>
    } @else {
      <div class="table-container">
        <table mat-table [dataSource]="players()">
          <ng-container matColumnDef="player_name">
            <th mat-header-cell *matHeaderCellDef>Jugador</th>
            <td mat-cell *matCellDef="let p"><strong>{{ p.player_name }}</strong></td>
          </ng-container>
          <ng-container matColumnDef="team">
            <th mat-header-cell *matHeaderCellDef>Equipo</th>
            <td mat-cell *matCellDef="let p">{{ p.team }}</td>
          </ng-container>
          <ng-container matColumnDef="position">
            <th mat-header-cell *matHeaderCellDef>Posición</th>
            <td mat-cell *matCellDef="let p">{{ p.position }}</td>
          </ng-container>
          <ng-container matColumnDef="average_points">
            <th mat-header-cell *matHeaderCellDef>Media Pts</th>
            <td mat-cell *matCellDef="let p">{{ p.average_points | number:'1.1-1' }}</td>
          </ng-container>
          <ng-container matColumnDef="clause_price">
            <th mat-header-cell *matHeaderCellDef>Cláusula</th>
            <td mat-cell *matCellDef="let p">{{ p.clause_price | money }}</td>
          </ng-container>
          <ng-container matColumnDef="score">
            <th mat-header-cell *matHeaderCellDef>Score</th>
            <td mat-cell *matCellDef="let p" class="score">{{ p.score | number:'1.2-2' }}</td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
    }
  `,
  styles: [`
    .description { color: var(--mat-sys-on-surface-variant); font-size: 0.9em; margin-bottom: 16px; }
    .loading-container { display: flex; align-items: center; gap: 16px; padding: 40px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .error-message { padding: 16px; background: var(--mat-sys-error-container); color: var(--mat-sys-on-error-container); border-radius: 8px; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .score { color: #4CAF50; font-weight: 700; }
  `]
})
export class ClausulableComponent {
  private statsService = inject(StatsService);

  loading = signal(true);
  error = signal('');
  players = signal<ClausulablePlayer[]>([]);
  columns = ['player_name', 'team', 'position', 'average_points', 'clause_price', 'score'];

  constructor() {
    this.loadData();
  }

  async loadData() {
    this.loading.set(true);
    try {
      const data = await this.statsService.getClausulablePlayers();
      this.players.set(data.players || []);
    } catch (err: any) {
      this.error.set(err.message || 'Error');
    } finally {
      this.loading.set(false);
    }
  }
}
