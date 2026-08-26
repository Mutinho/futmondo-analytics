import { Component, ChangeDetectionStrategy, inject, signal, effect, ViewChild } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { injectIsMobile } from '../../shared/utils/responsive';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
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
import { FavoritesService } from '../../core/services/favorites.service';
import { SofascoreDetailDialogComponent } from '../market/sofascore-detail-dialog.component';
import { ConfirmDialogComponent } from '../market/confirm-dialog.component';
import { PageHeaderComponent } from '../../shared/components/page-header.component';
import { getPlayerPhoto, getTeamLogo, getPositionKey, getPositionLabel, onImgError } from '../../shared/utils/player.utils';

interface FavoritePlayer {
  player_id: string;
  name: string;
  slug: string;
  position: string;
  position2: string;
  team: string;
  team_logo: string;
  value: number;
  change: number;
  points: number;
  average: number;
  home_average: number | null;
  away_average: number | null;
  matches: number;
  rating: number;
  sofascore_rating: number | null;
  sofascore_url: string | null;
  starter_pct: number | null;
  status: string;
}

@Component({
  selector: 'app-favorites',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    MatTableModule, MatSortModule, MatProgressSpinnerModule,
    MatChipsModule, MatIconModule, MatTooltipModule, MatButtonModule, MatButtonToggleModule, MatFormFieldModule, MatSelectModule, MatSnackBarModule, MoneyPipe, StarterBadgeComponent, StarterCardBadgeComponent, SofascoreBadgeComponent, SofascoreCardBadgeComponent, ScrollTopComponent, PageHeaderComponent, LoadingStateComponent, ViewToggleComponent, PositionChipComponent
  ],
  templateUrl: './favorites.component.html',
  styleUrl: './favorites.component.scss'
})
export class FavoritesComponent {
  private favoritesService = inject(FavoritesService);
  private championshipService = inject(ChampionshipService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  isMobile = injectIsMobile();

  viewMode = signal<'cards' | 'table'>(
    (localStorage.getItem('futmondo_view_favorites') as 'cards' | 'table') || 'table'
  );
  sortField = signal<string>('value');

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  dataSource = new MatTableDataSource<FavoritePlayer>([]);
  loading = signal(true);
  error = signal('');
  unfollowing = signal(false);

  columns = ['name', 'position', 'team', 'sofascore_rating', 'starter_pct', 'value', 'change', 'points', 'average', 'actions'];

  sortOptions = [
    { value: 'value', label: 'Valor' },
    { value: 'change', label: 'Tendencia' },
    { value: 'sofascore_rating', label: 'Sofascore' },
    { value: 'starter_pct', label: 'Titularidad' },
    { value: 'points', label: 'Puntos' },
  ];

  // Shared utils as class properties for template access
  getPlayerPhoto = getPlayerPhoto;
  getTeamLogo = getTeamLogo;
  getPositionKey = getPositionKey;
  getPositionLabel = getPositionLabel;
  onImgError = onImgError;

  constructor() {
    if (this.isMobile() && !localStorage.getItem('futmondo_view_favorites')) this.viewMode.set('cards');

    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadData();
    });
  }

  async loadData() {
    this.loading.set(true);
    this.error.set('');
    try {
      const data = await this.favoritesService.getMyFavorites(this.championshipService.activeId());
      this.dataSource.data = data.players || [];
    } catch (err: any) {
      this.error.set(err?.error?.detail || err.message || 'Error cargando favoritos');
    } finally {
      this.loading.set(false);
    }
  }

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
    localStorage.setItem('futmondo_view_favorites', mode);
  }

  getAverageTooltip(p: FavoritePlayer): string {
    let tip = `Media: ${p.average.toFixed(1)}`;
    if (p.home_average != null) tip += ` | Casa: ${p.home_average.toFixed(1)}`;
    if (p.away_average != null) tip += ` | Fuera: ${p.away_average.toFixed(1)}`;
    tip += ` | ${p.matches} partidos`;
    return tip;
  }

  openSofascoreDetail(player: FavoritePlayer, event: Event) {
    event.stopPropagation();
    this.dialog.open(SofascoreDetailDialogComponent, {
      data: { player_name: player.name },
      width: '550px',
    });
  }

  async unfollow(player: FavoritePlayer, event: Event) {
    event.stopPropagation();

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: '⭐ Quitar de favoritos',
        message: `¿Quitar a ${player.name} de tus favoritos?`,
        confirmText: 'Quitar',
        color: 'warn',
      },
      width: '400px',
    });

    const confirmed = await firstValueFrom(dialogRef.afterClosed());
    if (!confirmed) return;

    this.unfollowing.set(true);
    try {
      await this.favoritesService.unfollow(this.championshipService.activeId(), player.player_id);
      this.snackBar.open(`⭐ ${player.name} eliminado de favoritos`, 'OK', { duration: 3000 });
      await this.loadData();
    } catch (err: any) {
      this.snackBar.open(`❌ Error: ${err?.error?.detail || 'No se pudo eliminar'}`, 'OK', { duration: 4000 });
    } finally {
      this.unfollowing.set(false);
    }
  }
}
