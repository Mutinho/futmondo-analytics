import { Component, inject, signal } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { StatsService } from '../../core/services/stats.service';
import { PlayerFinance } from '../../core/models/stats.model';
import { PageHeaderComponent } from '../../shared/components/page-header.component';

@Component({
  selector: 'app-finances',
  standalone: true,
  imports: [MatTableModule, MatProgressSpinnerModule, MoneyPipe, PageHeaderComponent],
  template: `
    <app-page-header title="Finanzas" icon="account_balance_wallet" description="Desglose económico detallado por usuario." />

    @if (loading()) {
      <div class="loading-container">
        <mat-spinner diameter="40" />
        <span>Cargando finanzas...</span>
      </div>
    } @else if (error()) {
      <div class="error-message">{{ error() }}</div>
    } @else if (!users().length) {
      <div class="empty-state">
        <p>💰 No hay datos financieros disponibles.</p>
        <p>Se mostrarán cuando haya jornadas jugadas con puntos.</p>
      </div>
    } @else {
      <div class="table-container">
        <table mat-table [dataSource]="users()">
          <ng-container matColumnDef="team_name">
            <th mat-header-cell *matHeaderCellDef>Equipo</th>
            <td mat-cell *matCellDef="let u"><strong>{{ u.team_name }}</strong></td>
          </ng-container>
          <ng-container matColumnDef="total_points">
            <th mat-header-cell *matHeaderCellDef>Puntos</th>
            <td mat-cell *matCellDef="let u">{{ u.total_points }}</td>
          </ng-container>
          <ng-container matColumnDef="points_money">
            <th mat-header-cell *matHeaderCellDef>€ Puntos</th>
            <td mat-cell *matCellDef="let u">{{ u.points_money | money }}</td>
          </ng-container>
          <ng-container matColumnDef="ranking_money">
            <th mat-header-cell *matHeaderCellDef>Ranking</th>
            <td mat-cell *matCellDef="let u">{{ u.ranking_money | money }}</td>
          </ng-container>
          <ng-container matColumnDef="mvp_bonus">
            <th mat-header-cell *matHeaderCellDef>MVP / Once</th>
            <td mat-cell *matCellDef="let u">{{ (u.mvp_bonus + u.ideal_team_bonus) | money }}</td>
          </ng-container>
          <ng-container matColumnDef="transaction_profit">
            <th mat-header-cell *matHeaderCellDef>Profit Trans.</th>
            <td mat-cell *matCellDef="let u" [class]="u.transaction_profit >= 0 ? 'pos' : 'neg'">{{ u.transaction_profit | money:true }}</td>
          </ng-container>
          <ng-container matColumnDef="net_adjustment">
            <th mat-header-cell *matHeaderCellDef>Ajustes</th>
            <td mat-cell *matCellDef="let u" [class]="u.net_adjustment >= 0 ? 'pos' : 'neg'">{{ u.net_adjustment | money:true }}</td>
          </ng-container>
          <ng-container matColumnDef="total_money">
            <th mat-header-cell *matHeaderCellDef>Total</th>
            <td mat-cell *matCellDef="let u"><strong>{{ u.total_money | money }}</strong></td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
    }
  `,
  styles: [`
    .loading-container { display: flex; align-items: center; gap: 16px; padding: 40px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .error-message { padding: 16px; background: var(--mat-sys-error-container); color: var(--mat-sys-on-error-container); border-radius: 8px; }
    .empty-state { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .pos { color: #16a34a; font-weight: 600; }
    .neg { color: #dc2626; font-weight: 600; }
  `]
})
export class FinancesComponent {
  private statsService = inject(StatsService);

  loading = signal(true);
  error = signal('');
  users = signal<PlayerFinance[]>([]);
  columns = ['team_name', 'total_points', 'points_money', 'ranking_money', 'mvp_bonus', 'transaction_profit', 'net_adjustment', 'total_money'];

  constructor() {
    this.loadData();
  }

  async loadData() {
    this.loading.set(true);
    try {
      const data = await this.statsService.getPlayerFinances();
      this.users.set(data.users || []);
    } catch (err: any) {
      this.error.set(err.message || 'Error');
    } finally {
      this.loading.set(false);
    }
  }
}
