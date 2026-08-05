import { Component, inject, signal, effect, ViewChild } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { ChampionshipService } from '../../core/services/championship.service';

interface MarketPlayer {
  player_id: string;
  name: string;
  team: string;
  position: string;
  value: number;
  market_price: number;
  change: number;
  current_bid: number;
  average: number;
  suggested_bid: number;
  bid_confidence: string;
  bid_based_on: number;
  overpay_pct: number;
  expiration: string;
}

@Component({
  selector: 'app-market',
  standalone: true,
  imports: [MatTableModule, MatSortModule, MatProgressSpinnerModule, MatChipsModule, MoneyPipe],
  template: `
    <h1>🛒 Mercado de Hoy</h1>
    <p class="description">Jugadores del computer disponibles para fichar. La puja sugerida se basa en el historial de compras similares.</p>

    @if (loading()) {
      <div class="loading"><mat-spinner diameter="40" /> <span>Cargando mercado...</span></div>
    } @else if (error()) {
      <div class="error-message">{{ error() }}</div>
    } @else if (!dataSource.data.length) {
      <div class="empty">🛒 No hay jugadores del computer en el mercado ahora mismo.</div>
    } @else {
      <p class="count">{{ dataSource.data.length }} jugadores disponibles</p>
      <div class="table-container">
        <table mat-table [dataSource]="dataSource" matSort>
          <ng-container matColumnDef="name">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Jugador</th>
            <td mat-cell *matCellDef="let p"><strong>{{ p.name }}</strong></td>
          </ng-container>
          <ng-container matColumnDef="team">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Equipo</th>
            <td mat-cell *matCellDef="let p">{{ p.team }}</td>
          </ng-container>
          <ng-container matColumnDef="position">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Pos</th>
            <td mat-cell *matCellDef="let p">{{ p.position }}</td>
          </ng-container>
          <ng-container matColumnDef="value">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Valor</th>
            <td mat-cell *matCellDef="let p">{{ p.value | money }}</td>
          </ng-container>
          <ng-container matColumnDef="change">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Tendencia</th>
            <td mat-cell *matCellDef="let p" [class]="p.change >= 0 ? 'trend-up' : 'trend-down'">
              {{ p.change >= 0 ? '▲' : '▼' }} {{ p.change | money }}
            </td>
          </ng-container>
          <ng-container matColumnDef="market_price">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Precio Mercado</th>
            <td mat-cell *matCellDef="let p">{{ p.market_price | money }}</td>
          </ng-container>
          <ng-container matColumnDef="current_bid">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Puja Actual</th>
            <td mat-cell *matCellDef="let p" class="current-bid">
              {{ p.current_bid ? (p.current_bid | money) : '-' }}
            </td>
          </ng-container>
          <ng-container matColumnDef="suggested_bid">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Puja Sugerida</th>
            <td mat-cell *matCellDef="let p" class="suggested">
              {{ p.suggested_bid | money }}
              <span class="confidence" [class]="'conf-' + p.bid_confidence">
                {{ p.bid_confidence === 'high' ? '🎯' : p.bid_confidence === 'medium' ? '📊' : '❓' }}
              </span>
            </td>
          </ng-container>
          <ng-container matColumnDef="avg_paid_similar">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Sobrepuja Media</th>
            <td mat-cell *matCellDef="let p" class="overpay">+{{ p.overpay_pct }}%</td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
      <p class="legend">🎯 Alta confianza (10+ transacciones similares) · 📊 Media (3-9) · ❓ Baja (&lt;3)</p>
    }
  `,
  styles: [`
    .description { color: var(--mat-sys-on-surface-variant); font-size: 0.9em; margin-bottom: 16px; }
    .loading { display: flex; align-items: center; gap: 16px; padding: 40px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .error-message { padding: 16px; background: var(--mat-sys-error-container); color: var(--mat-sys-on-error-container); border-radius: 8px; }
    .empty { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); font-size: 1.1em; }
    .count { color: var(--mat-sys-on-surface-variant); font-size: 0.85em; margin-bottom: 12px; }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .suggested { font-weight: 700; color: #4CAF50; }
    .overpay { color: #d97706; font-weight: 600; }
    .trend-up { color: #16a34a; font-weight: 600; }
    .trend-down { color: #dc2626; font-weight: 600; }
    .current-bid { color: #7c3aed; font-weight: 600; }
    .confidence { margin-left: 4px; font-size: 0.9em; }
    .legend { color: var(--mat-sys-on-surface-variant); font-size: 0.8em; margin-top: 12px; }
  `]
})
export class MarketComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  dataSource = new MatTableDataSource<MarketPlayer>([]);
  loading = signal(true);
  error = signal('');
  columns = ['name', 'team', 'position', 'value', 'change', 'market_price', 'current_bid', 'suggested_bid', 'avg_paid_similar'];

  constructor() {
    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadData();
    });
  }

  async loadData() {
    this.loading.set(true);
    this.error.set('');
    try {
      let params = new HttpParams().set('championship_id', this.championshipService.activeId());
      const data = await firstValueFrom(this.http.get<any>('/api/v1/market/today', { params }));
      this.dataSource.data = data.players || [];
    } catch (err: any) {
      this.error.set(err.message || 'Error cargando mercado');
    } finally {
      this.loading.set(false);
    }
  }
}
