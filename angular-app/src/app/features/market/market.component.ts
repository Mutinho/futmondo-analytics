import { Component, inject, signal, effect, ViewChild } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { ChampionshipService } from '../../core/services/championship.service';
import { ConfirmDialogComponent } from './confirm-dialog.component';
import { SofascoreDetailDialogComponent } from './sofascore-detail-dialog.component';

interface MarketPlayer {
  player_id: string;
  slug: string;
  name: string;
  team: string;
  position: string;
  position2: string;
  value: number;
  market_price: number;
  change: number;
  current_bid: number;
  current_bid_id: string;
  average: number;
  suggested_bid: number;
  bid_confidence: string;
  bid_based_on: number;
  overpay_pct: number;
  expiration: string;
  sofascore_rating: number | null;
}

@Component({
  selector: 'app-market',
  standalone: true,
  imports: [MatTableModule, MatSortModule, MatProgressSpinnerModule, MatChipsModule, MatButtonModule, MatIconModule, MatSnackBarModule, MoneyPipe],
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
      <!-- Banner info usuario -->
      @if (userInfo()) {
        <div class="user-info-banner">
          <div class="info-item">
            <span class="info-label">Presupuesto</span>
            <span class="info-value">{{ userInfo()!.balance | money }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">En pujas</span>
            <span class="info-value bids">{{ userInfo()!.active_bids_total | money }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Puja máxima</span>
            <span class="info-value max">{{ userInfo()!.max_bid | money }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Disponible</span>
            <span class="info-value" [class]="userInfo()!.available_for_bids > 0 ? 'available' : 'danger'">
              {{ userInfo()!.available_for_bids | money }}
            </span>
          </div>
        </div>
      }
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
            <td mat-cell *matCellDef="let p">
              <span class="pos-chip" [class]="'pos-' + getPositionKey(p.position)">{{ getPositionLabel(p.position) }}</span>
              @if (p.position2) {
                <span class="pos-chip pos-secondary" [class]="'pos-' + getPositionKey(p.position2)">{{ getPositionLabel(p.position2) }}</span>
              }
            </td>
          </ng-container>
          <ng-container matColumnDef="sofascore_rating">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Sofascore</th>
            <td mat-cell *matCellDef="let p">
              @if (p.sofascore_rating != null) {
                <span class="sofascore-badge" [class]="getSofascoreClass(p.sofascore_rating)"
                      (click)="openSofascoreDetail(p, $event)">
                  {{ p.sofascore_rating.toFixed(1) }}
                </span>
              } @else {
                <span class="sofascore-na">-</span>
              }
            </td>
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
              @if (p.current_bid) {
                {{ p.current_bid | money }}
                <button mat-icon-button color="warn" class="cancel-btn"
                        (click)="cancelBid(p, $event)"
                        [disabled]="bidding()"
                        title="Cancelar puja">
                  <mat-icon>close</mat-icon>
                </button>
              } @else {
                -
              }
            </td>
          </ng-container>
          <ng-container matColumnDef="suggested_bid">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Puja Sugerida</th>
            <td mat-cell *matCellDef="let p" class="suggested">
              {{ p.suggested_bid | money }}
              <button mat-icon-button color="primary" class="bid-btn"
                      (click)="confirmBid(p, $event)"
                      [disabled]="bidding()"
                      title="Pujar por {{ p.suggested_bid | money }}">
                <mat-icon>gavel</mat-icon>
              </button>
            </td>
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
    .user-info-banner {
      display: flex; gap: 24px; flex-wrap: wrap; padding: 16px 20px;
      background: var(--mat-sys-surface-container); border-radius: 12px; margin-bottom: 16px;
    }
    .info-item { display: flex; flex-direction: column; gap: 2px; }
    .info-label { font-size: 0.75em; text-transform: uppercase; letter-spacing: 0.5px; color: var(--mat-sys-on-surface-variant); }
    .info-value { font-size: 1.2em; font-weight: 700; }
    .info-value.bids { color: #7c3aed; }
    .info-value.max { color: #2563eb; }
    .info-value.available { color: #16a34a; }
    .info-value.danger { color: #dc2626; }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .suggested { font-weight: 700; color: #4CAF50; }
    .overpay { color: #d97706; font-weight: 600; }
    .pos-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; color: #fff; text-transform: capitalize; }
    .pos-secondary { margin-left: 3px; opacity: 0.8; }
    .pos-fwd { background: #dc2626; }
    .pos-mid { background: #2563eb; }
    .pos-def { background: #ca8a04; }
    .pos-gk { background: #16a34a; }
    .trend-up { color: #16a34a; font-weight: 600; }
    .trend-down { color: #dc2626; font-weight: 600; }
    .current-bid { color: #7c3aed; font-weight: 600; }
    .bid-btn { transform: scale(0.75); vertical-align: middle;  position: relative; padding: 0; }
    .cancel-btn { transform: scale(0.7); vertical-align: middle; position: relative; padding: 0; top:1px; }
    .confidence { margin-left: 4px; font-size: 0.9em; }
    .legend { color: var(--mat-sys-on-surface-variant); font-size: 0.8em; margin-top: 12px; }
    .sofascore-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 700; color: #fff; cursor: pointer; transition: transform 0.15s; }
    .sofascore-badge:hover { transform: scale(1.1); }
    .sofascore-green { background: #16a34a; }
    .sofascore-yellow { background: #ca8a04; }
    .sofascore-red { background: #dc2626; }
    .sofascore-na { color: var(--mat-sys-on-surface-variant); }
  `]
})
export class MarketComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);

  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  dataSource = new MatTableDataSource<MarketPlayer>([]);
  loading = signal(true);
  error = signal('');
  bidding = signal(false);
  userInfo = signal<{ balance: number; team_value: number; max_bid: number; active_bids_total: number; available_for_bids: number } | null>(null);
  columns = ['name', 'team', 'position', 'sofascore_rating', 'value', 'change', 'market_price', 'current_bid', 'suggested_bid'];

  getPositionKey(position: string): string {
    const p = (position || '').toLowerCase();
    if (p.includes('delantero') || p.includes('forward')) return 'fwd';
    if (p.includes('centrocampista') || p.includes('medio') || p.includes('mid')) return 'mid';
    if (p.includes('defensa') || p.includes('defender')) return 'def';
    if (p.includes('portero') || p.includes('keeper')) return 'gk';
    return 'mid';
  }

  getPositionLabel(position: string): string {
    const p = (position || '').toLowerCase();
    if (p.includes('delantero')) return 'DL';
    if (p.includes('centrocampista')) return 'MC';
    if (p.includes('defensa')) return 'DF';
    if (p.includes('portero')) return 'PT';
    return position;
  }

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
      this.userInfo.set(data.user_info || null);
    } catch (err: any) {
      this.error.set(err.message || 'Error cargando mercado');
    } finally {
      this.loading.set(false);
    }
  }

  async confirmBid(player: MarketPlayer, event: Event) {
    event.stopPropagation();
    const moneyFmt = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: '🔨 Confirmar Puja',
        message: `¿Pujar ${moneyFmt.format(player.suggested_bid)} por ${player.name} (${player.team})?`,
        confirmText: 'Pujar',
        color: 'primary',
      },
      width: '400px',
    });

    const confirmed = await firstValueFrom(dialogRef.afterClosed());
    if (!confirmed) return;

    this.bidding.set(true);
    try {
      let params = new HttpParams()
        .set('championship_id', this.championshipService.activeId())
        .set('player_id', player.player_id)
        .set('player_slug', player.slug)
        .set('price', player.suggested_bid)
        .set('is_clause', 'false');

      const result = await firstValueFrom(this.http.post<any>('/api/v1/market/bid', {}, { params }));
      if (result.success) {
        this.snackBar.open(`✅ Puja realizada: ${moneyFmt.format(player.suggested_bid)} por ${player.name}`, 'OK', { duration: 4000 });
        await this.loadData();
      } else {
        this.snackBar.open(`❌ Error: ${result.message}`, 'OK', { duration: 5000 });
      }
    } catch (err: any) {
      this.snackBar.open(`❌ Error al pujar: ${err.message || 'Error desconocido'}`, 'OK', { duration: 5000 });
    } finally {
      this.bidding.set(false);
    }
  }

  async cancelBid(player: MarketPlayer, event: Event) {
    event.stopPropagation();
    const moneyFmt = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: '❌ Cancelar Puja',
        message: `¿Cancelar puja de ${moneyFmt.format(player.current_bid)} por ${player.name}?`,
        confirmText: 'Cancelar puja',
        color: 'warn',
      },
      width: '400px',
    });

    const confirmed = await firstValueFrom(dialogRef.afterClosed());
    if (!confirmed) return;

    this.bidding.set(true);
    try {
      let params = new HttpParams()
        .set('championship_id', this.championshipService.activeId())
        .set('bid_id', player.current_bid_id);

      const result = await firstValueFrom(this.http.post<any>('/api/v1/market/cancelbid', {}, { params }));
      if (result.success) {
        this.snackBar.open(`✅ Puja cancelada para ${player.name}`, 'OK', { duration: 4000 });
        await this.loadData();
      } else {
        this.snackBar.open(`❌ Error: ${result.message}`, 'OK', { duration: 5000 });
      }
    } catch (err: any) {
      this.snackBar.open(`❌ Error al cancelar: ${err.message || 'Error desconocido'}`, 'OK', { duration: 5000 });
    } finally {
      this.bidding.set(false);
    }
  }

  getSofascoreClass(rating: number): string {
    if (rating >= 7) return 'sofascore-green';
    if (rating >= 6) return 'sofascore-yellow';
    return 'sofascore-red';
  }

  openSofascoreDetail(player: MarketPlayer, event: Event) {
    event.stopPropagation();
    this.dialog.open(SofascoreDetailDialogComponent, {
      data: { player_name: player.name },
      width: '550px',
    });
  }
}
