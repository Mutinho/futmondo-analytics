import { Component, inject, signal } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';
import { AnalyticsService } from '../../../core/services/analytics.service';

@Component({
  selector: 'app-analytics-users',
  standalone: true,
  imports: [MatProgressSpinnerModule, MatTableModule, MoneyPipe],
  template: `
    <h3>👥 Actividad de Mercado por Usuario</h3>
    @if (loading()) {
      <div class="loading"><mat-spinner diameter="32" /> Cargando...</div>
    } @else if (!users().length) {
      <div class="empty">👥 No hay datos de actividad de mercado todavía.</div>
    } @else {
      <div class="table-container">
        <table mat-table [dataSource]="users()">
          <ng-container matColumnDef="team_name"><th mat-header-cell *matHeaderCellDef>Equipo</th><td mat-cell *matCellDef="let u"><strong>{{ u.team_name }}</strong></td></ng-container>
          <ng-container matColumnDef="purchases"><th mat-header-cell *matHeaderCellDef>Compras</th><td mat-cell *matCellDef="let u">{{ u.purchases }}</td></ng-container>
          <ng-container matColumnDef="sales"><th mat-header-cell *matHeaderCellDef>Ventas</th><td mat-cell *matCellDef="let u">{{ u.sales }}</td></ng-container>
          <ng-container matColumnDef="spent"><th mat-header-cell *matHeaderCellDef>Gastado</th><td mat-cell *matCellDef="let u" class="neg">{{ u.total_spent | money }}</td></ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
    }
  `,
  styles: [`.loading { display: flex; align-items: center; gap: 12px; padding: 32px; color: var(--mat-sys-on-surface-variant); } .empty { text-align: center; padding: 48px; color: var(--mat-sys-on-surface-variant); } .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); } table { width: 100%; } .neg { color: #dc2626; font-weight: 600; }`]
})
export class UsersComponent {
  private svc = inject(AnalyticsService);
  loading = signal(true);
  users = signal<any[]>([]);
  columns = ['team_name', 'purchases', 'sales', 'spent'];
  constructor() { this.load(); }
  async load() {
    try { const d = await this.svc.getUserMarketActivity(); this.users.set(d?.users || d?.teams || []); }
    catch {}
    finally { this.loading.set(false); }
  }
}
