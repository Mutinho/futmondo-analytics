import { InfoCardComponent } from '../../../shared/components/info-card.component';
import { Component, inject, signal } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { DecimalPipe } from '@angular/common';
import { AnalyticsService, PlayerForm } from '../../../core/services/analytics.service';

@Component({
  selector: 'app-analytics-players',
  standalone: true,
  imports: [MatProgressSpinnerModule, MatTableModule, DecimalPipe, InfoCardComponent],
  template: `
    <h3>🔥 Forma de Jugadores</h3>
    <app-info-card>Top jugadores por rendimiento reciente. Muestra media de puntos y tendencia al alza o a la baja para detectar jugadores en racha.</app-info-card>
    @if (loading()) {
      <div class="loading"><mat-spinner diameter="32" /> Cargando...</div>
    } @else if (!players().length) {
      <div class="empty">🔥 No hay datos de rendimiento de jugadores todavía.</div>
    } @else {
      <div class="table-container">
        <table mat-table [dataSource]="players()">
          <ng-container matColumnDef="name"><th mat-header-cell *matHeaderCellDef>Jugador</th><td mat-cell *matCellDef="let p">{{ p.name }}</td></ng-container>
          <ng-container matColumnDef="team"><th mat-header-cell *matHeaderCellDef>Equipo</th><td mat-cell *matCellDef="let p">{{ p.team }}</td></ng-container>
          <ng-container matColumnDef="average"><th mat-header-cell *matHeaderCellDef>Media</th><td mat-cell *matCellDef="let p">{{ p.average | number:'1.1-1' }}</td></ng-container>
          <ng-container matColumnDef="trend"><th mat-header-cell *matHeaderCellDef>Tendencia</th><td mat-cell *matCellDef="let p" [style.color]="p.trend >= 0 ? '#16a34a' : '#dc2626'">{{ p.trend > 0 ? '+' : '' }}{{ p.trend | number:'1.1-1' }}</td></ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
    }
  `,
  styles: [`.loading { display: flex; align-items: center; gap: 12px; padding: 32px; color: var(--mat-sys-on-surface-variant); } .empty { text-align: center; padding: 48px; color: var(--mat-sys-on-surface-variant); } .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); } table { width: 100%; } .section-desc { color: #666666; font-size: 13px; margin: -4px 0 20px; }`]
})
export class PlayersComponent {
  private svc = inject(AnalyticsService);
  loading = signal(true);
  players = signal<PlayerForm[]>([]);
  columns = ['name', 'team', 'average', 'trend'];
  constructor() { this.load(); }
  async load() {
    try { const d = await this.svc.getPlayerForm(); this.players.set(d.players); }
    catch {}
    finally { this.loading.set(false); }
  }
}
