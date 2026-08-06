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
import { BidDialogComponent, BidDialogData, BidDialogResult } from './bid-dialog.component';
import { SofascoreDetailDialogComponent } from './sofascore-detail-dialog.component';

interface MarketPlayer {
  player_id: string;
  slug: string;
  name: string;
  team: string;
  team_logo: string;
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
  sofascore_url: string | null;
  starter_pct: number | null;
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
            <td mat-cell *matCellDef="let p" class="player-cell">
              <div class="player-wrapper">
                <img [src]="getPlayerPhoto(p.slug)" class="player-photo" [alt]="p.name" loading="lazy"
                     (error)="$event.target.style.display='none'" />
                @if (p.sofascore_url) {
                  <a [href]="p.sofascore_url" target="_blank" class="player-link"><strong>{{ p.name }}</strong></a>
                } @else {
                  <strong>{{ p.name }}</strong>
                }
              </div>
            </td>
          </ng-container>
          <ng-container matColumnDef="team">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Equipo</th>
            <td mat-cell *matCellDef="let p" class="team-cell">
              <div class="team-wrapper">
                <img [src]="getTeamLogo(p.team_logo)" class="team-logo" [alt]="p.team" loading="lazy"
                     (error)="$event.target.style.display='none'" />
                <span>{{ p.team }}</span>
              </div>
            </td>
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
          <ng-container matColumnDef="starter_pct">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>% Titular</th>
            <td mat-cell *matCellDef="let p">
              @if (p.starter_pct != null) {
                <span class="starter-badge" [class]="getStarterClass(p.starter_pct)">{{ p.starter_pct }}%</span>
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
    }
  `,
  styles: [`
    .description { color: #666666; font-size: 13px; margin-bottom: 24px; }
    .loading { display: flex; align-items: center; gap: 16px; padding: 60px; justify-content: center; color: #666666; }
    .error-message { padding: 16px; background: #ffebee; color: #d32f2f; border-radius: 8px; }
    .empty { text-align: center; padding: 60px 20px; color: #666666; font-size: 1.1em; }
    .count { color: #666666; font-size: 13px; margin-bottom: 16px; }
    .user-info-banner {
      display: flex; gap: 32px; flex-wrap: wrap; padding: 20px 24px;
      background: var(--mat-sys-surface-container); border-radius: 12px; margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .info-item { display: flex; flex-direction: column; gap: 4px; }
    .info-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--mat-sys-on-surface-variant); font-weight: 600; }
    .info-value { font-size: 1.3em; font-weight: 700; color: var(--mat-sys-on-surface); }
    .info-value.bids { color: #7b1fa2; }
    .info-value.max { color: #1565c0; }
    .info-value.available { color: #2e7d32; }
    .info-value.danger { color: #d32f2f; }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .player-cell { }
    .player-cell .player-wrapper { display: inline-flex; align-items: center; gap: 10px; }
    .player-photo { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; background: #f0f0f0; flex-shrink: 0; vertical-align: middle; }
    .player-info { display: inline; }
    .team-cell { }
    .team-cell .team-wrapper { display: inline-flex; align-items: center; gap: 8px; }
    .team-logo { width: 40px; height: 40px; object-fit: contain; flex-shrink: 0; vertical-align: middle; }
    .suggested { font-weight: 700; color: #2e7d32; }
    .overpay { color: #f57c00; font-weight: 600; }
    .pos-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; color: #fff; text-transform: capitalize; }
    .pos-secondary { margin-left: 3px; opacity: 0.8; }
    .pos-fwd { background: #e57373; }
    .pos-mid { background: #64b5f6; }
    .pos-def { background: #ffb74d; }
    .pos-gk { background: #ffd54f; color: #5d4037; }
    .trend-up { color: #2e7d32; font-weight: 600; }
    .trend-down { color: #d32f2f; font-weight: 600; }
    .player-link { color: #1565c0; text-decoration: none; &:hover { text-decoration: underline; } }
    .current-bid { color: #7b1fa2; font-weight: 600; }
    .bid-btn { transform: scale(0.75); vertical-align: middle;  position: relative; padding: 0; }
    .cancel-btn { transform: scale(0.7); vertical-align: middle; position: relative; padding: 0; top:1px; }
    .confidence { margin-left: 4px; font-size: 0.9em; }
    .legend { color: #666666; font-size: 12px; margin-top: 16px; }
    .sofascore-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 700; color: #fff; cursor: pointer; transition: transform 0.15s; }
    .sofascore-badge:hover { transform: scale(1.1); }
    .sofascore-s90 { background: #374DF5; }
    .sofascore-s80 { background: #00ADC4; }
    .sofascore-s70 { background: #00C424; }
    .sofascore-s65 { background: #D9AF00; }
    .sofascore-s60 { background: #ED7E07; }
    .sofascore-na { color: var(--mat-sys-on-surface-variant); }
    .starter-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 700; color: #fff; }
    .starter-high { background: #16a34a; }
    .starter-mid { background: #ca8a04; }
    .starter-low { background: #dc2626; }
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
  columns = ['name', 'team', 'position', 'sofascore_rating', 'starter_pct', 'value', 'change', 'market_price', 'current_bid', 'suggested_bid'];

  getPositionKey(position: string): string {
    const p = (position || '').toLowerCase();
    if (p.includes('delantero') || p.includes('forward')) return 'fwd';
    if (p.includes('centrocampista') || p.includes('medio') || p.includes('mid')) return 'mid';
    if (p.includes('defensa') || p.includes('defender')) return 'def';
    if (p.includes('portero') || p.includes('keeper')) return 'gk';
    return 'mid';
  }

  getPlayerPhoto(slug: string): string {
    return `https://static01.mondocore.com/futmondo/img/faces/64/${slug}.png`;
  }

  getTeamLogo(logo: string): string {
    return `https://static02.mondocore.com/futmondo/img/teams/64/${logo}`;
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

    const userInfoData = this.userInfo();
    const maxBid = userInfoData?.available_for_bids || userInfoData?.max_bid || player.suggested_bid;

    const dialogRef = this.dialog.open(BidDialogComponent, {
      data: {
        playerName: player.name,
        team: player.team,
        suggestedBid: player.suggested_bid,
        marketPrice: player.market_price,
        maxBid: maxBid,
      } as BidDialogData,
      width: '420px',
    });

    const result: BidDialogResult | undefined = await firstValueFrom(dialogRef.afterClosed());
    if (!result?.confirmed) return;

    this.bidding.set(true);
    try {
      let params = new HttpParams()
        .set('championship_id', this.championshipService.activeId())
        .set('player_id', player.player_id)
        .set('player_slug', player.slug)
        .set('price', result.price)
        .set('is_clause', 'false');

      const apiResult = await firstValueFrom(this.http.post<any>('/api/v1/market/bid', {}, { params }));
      if (apiResult.success) {
        this.snackBar.open(`✅ Puja realizada: ${moneyFmt.format(result.price)} por ${player.name}`, 'OK', { duration: 4000 });
        await this.loadData();
      } else {
        this.snackBar.open(`❌ Error: ${apiResult.message}`, 'OK', { duration: 5000 });
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
    if (rating >= 9) return 'sofascore-s90';
    if (rating >= 8) return 'sofascore-s80';
    if (rating >= 7) return 'sofascore-s70';
    if (rating >= 6.5) return 'sofascore-s65';
    return 'sofascore-s60';
  }

  getStarterClass(pct: number): string {
    if (pct >= 75) return 'starter-high';
    if (pct >= 40) return 'starter-mid';
    return 'starter-low';
  }

  openSofascoreDetail(player: MarketPlayer, event: Event) {
    event.stopPropagation();
    this.dialog.open(SofascoreDetailDialogComponent, {
      data: { player_name: player.name },
      width: '550px',
    });
  }
}
