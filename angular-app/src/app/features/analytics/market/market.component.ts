import { InfoCardComponent } from '../../../shared/components/info-card.component';
import { Component, inject, signal } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { DecimalPipe } from '@angular/common';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';
import { AnalyticsService } from '../../../core/services/analytics.service';

@Component({
  selector: 'app-analytics-market',
  standalone: true,
  imports: [MatProgressSpinnerModule, MatTableModule, DecimalPipe, MoneyPipe, InfoCardComponent],
  template: `
    <h3>💹 Watchlist — Agentes Libres</h3>
    <app-info-card>Jugadores libres (sin dueño) ordenados por su relación puntos/cláusula. Útil para encontrar fichajes baratos con buen rendimiento.</app-info-card>
    @if (loading()) {
      <div class="loading"><mat-spinner diameter="32" /> Cargando...</div>
    } @else if (!players().length) {
      <div class="empty">💹 No hay datos de watchlist disponibles.</div>
    } @else {
      <div class="table-container">
        <table mat-table [dataSource]="players()">
          <ng-container matColumnDef="name"><th mat-header-cell *matHeaderCellDef>Jugador</th><td mat-cell *matCellDef="let p"><strong>{{ p.name }}</strong></td></ng-container>
          <ng-container matColumnDef="team"><th mat-header-cell *matHeaderCellDef>Equipo Real</th><td mat-cell *matCellDef="let p">{{ p.team }}</td></ng-container>
          <ng-container matColumnDef="average"><th mat-header-cell *matHeaderCellDef>Media</th><td mat-cell *matCellDef="let p">{{ p.average | number:'1.1-1' }}</td></ng-container>
          <ng-container matColumnDef="clause"><th mat-header-cell *matHeaderCellDef>Cláusula</th><td mat-cell *matCellDef="let p">{{ p.clause | money }}</td></ng-container>
          <ng-container matColumnDef="ratio"><th mat-header-cell *matHeaderCellDef>Ratio Pts/€</th><td mat-cell *matCellDef="let p" class="score">{{ p.ratio | number:'1.3-3' }}</td></ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
    }
  `,
  styles: [`.loading { display: flex; align-items: center; gap: 12px; padding: 32px; color: var(--mat-sys-on-surface-variant); } .empty { text-align: center; padding: 48px; color: var(--mat-sys-on-surface-variant); } .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); } table { width: 100%; } .score { color: #4CAF50; font-weight: 700; } .section-desc { color: #666666; font-size: 13px; margin: -4px 0 20px; }`]
})
export class MarketComponent {
  private svc = inject(AnalyticsService);
  loading = signal(true);
  players = signal<any[]>([]);
  columns = ['name', 'team', 'average', 'clause', 'ratio'];
  constructor() { this.load(); }
  async load() {
    try { const d = await this.svc.getWatchlist(); this.players.set(d?.players || []); }
    catch {}
    finally { this.loading.set(false); }
  }
}
