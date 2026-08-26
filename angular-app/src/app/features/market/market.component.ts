import { Component, ChangeDetectionStrategy, inject, signal, effect, ViewChild } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { injectIsMobile } from '../../shared/utils/responsive';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { StarterBadgeComponent } from '../../shared/components/starter-badge.component';
import { StarterCardBadgeComponent } from '../../shared/components/starter-card-badge.component';
import { SofascoreBadgeComponent } from '../../shared/components/sofascore-badge.component';
import { SofascoreCardBadgeComponent } from '../../shared/components/sofascore-card-badge.component';
import { ScrollTopComponent } from '../../shared/components/scroll-top.component';
import { LoadingStateComponent } from '../../shared/components/loading-state/loading-state.component';
import { ViewToggleComponent } from '../../shared/components/view-toggle/view-toggle.component';
import { PositionChipComponent } from '../../shared/components/position-chip/position-chip.component';
import { ChampionshipService } from '../../core/services/championship.service';
import { ConfirmDialogComponent } from './confirm-dialog.component';
import { BidDialogComponent, BidDialogData, BidDialogResult } from './bid-dialog.component';
import { SofascoreDetailDialogComponent } from './sofascore-detail-dialog.component';
import { PageHeaderComponent } from '../../shared/components/page-header.component';
import { getPlayerPhoto, getTeamLogo, getPositionKey, getPositionLabel, onImgError } from '../../shared/utils/player.utils';

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
  points: number;
  home_average: number | null;
  away_average: number | null;
  matches: number;
  suggested_bid: number;
  bid_confidence: string;
  bid_based_on: number;
  overpay_pct: number;
  expiration: string;
  sofascore_rating: number | null;
  sofascore_url: string | null;
  starter_pct: number | null;
  is_favorite: boolean;
}

@Component({
  selector: 'app-market',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [MatTableModule, MatSortModule, MatProgressSpinnerModule, MatChipsModule, MatButtonModule, MatButtonToggleModule, MatIconModule, MatFormFieldModule, MatSelectModule, MatSnackBarModule, MoneyPipe, StarterBadgeComponent, StarterCardBadgeComponent, SofascoreBadgeComponent, SofascoreCardBadgeComponent, ScrollTopComponent, PageHeaderComponent, LoadingStateComponent, ViewToggleComponent, PositionChipComponent],
  templateUrl: './market.component.html',
  styleUrl: './market.component.scss'
})
export class MarketComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  isMobile = injectIsMobile();

  viewMode = signal<'cards' | 'table'>(
    (localStorage.getItem('futmondo_view_market') as 'cards' | 'table') || 'table'
  );
  sortField = signal<string>('value');

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  dataSource = new MatTableDataSource<MarketPlayer>([]);
  loading = signal(true);
  error = signal('');
  bidding = signal(false);
  userInfo = signal<{ balance: number; team_value: number; max_bid: number; active_bids_total: number; available_for_bids: number } | null>(null);
  columns = ['name', 'team', 'position', 'sofascore_rating', 'starter_pct', 'value', 'change', 'points', 'average', 'market_price', 'current_bid', 'suggested_bid'];

  sortOptions = [
    { value: 'value', label: 'Valor' },
    { value: 'change', label: 'Tendencia' },
    { value: 'sofascore_rating', label: 'Sofascore' },
    { value: 'starter_pct', label: 'Titularidad' },
    { value: 'suggested_bid', label: 'Puja sugerida' },
    { value: 'points', label: 'Puntos' },
    { value: 'average', label: 'Media' },
  ];

  // Shared utils as class properties for template access
  getPlayerPhoto = getPlayerPhoto;
  getTeamLogo = getTeamLogo;
  getPositionKey = getPositionKey;
  getPositionLabel = getPositionLabel;
  onImgError = onImgError;

  sortCards() {
    const field = this.sortField();
    const sorted = [...this.dataSource.data].sort((a: any, b: any) => {
      const va = a[field] ?? -Infinity;
      const vb = b[field] ?? -Infinity;
      return vb - va;
    });
    this.dataSource.data = sorted;
  }

  onSortChange(value: string) {
    this.sortField.set(value);
    this.sortCards();
  }

  setViewMode(mode: 'cards' | 'table') {
    this.viewMode.set(mode);
    localStorage.setItem('futmondo_view_market', mode);
  }

  constructor() {
    if (this.isMobile() && !localStorage.getItem('futmondo_view_market')) this.viewMode.set('cards');

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




  openSofascoreDetail(player: MarketPlayer, event: Event) {
    event.stopPropagation();
    this.dialog.open(SofascoreDetailDialogComponent, {
      data: { player_name: player.name },
      width: '550px',
    });
  }
}
