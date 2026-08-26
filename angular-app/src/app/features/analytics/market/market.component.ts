import { Component, inject, signal, computed, effect, ViewChild } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule, MatPaginator, PageEvent } from '@angular/material/paginator';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { DecimalPipe } from '@angular/common';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';
import { SofascoreBadgeComponent } from '../../../shared/components/sofascore-badge.component';
import { SofascoreCardBadgeComponent } from '../../../shared/components/sofascore-card-badge.component';
import { StarterBadgeComponent } from '../../../shared/components/starter-badge.component';
import { StarterCardBadgeComponent } from '../../../shared/components/starter-card-badge.component';
import { ScrollTopComponent } from '../../../shared/components/scroll-top.component';
import { PageHeaderComponent } from '../../../shared/components/page-header.component';
import { AnalyticsService } from '../../../core/services/analytics.service';
import { ChampionshipService } from '../../../core/services/championship.service';
import { getPlayerPhoto, getPositionKey, getPositionLabel, onImgError } from '../../../shared/utils/player.utils';
import { getTeamLogoById } from '../../../shared/utils/team-logos';

interface WatchlistPlayer {
  player_id: string;
  name: string;
  slug: string;
  position: string;
  position2: string;
  team: string;
  real_team_id: string;
  value: number;
  change: number;
  average: number;
  ratio: number;
  sofascore_rating: number | null;
  sofascore_url: string | null;
  starter_pct: number | null;
  is_favorite: boolean;
  streak: number;
  trend: number;
}

@Component({
  selector: 'app-analytics-market',
  standalone: true,
  imports: [
    MatTableModule, MatSortModule, MatProgressSpinnerModule,
    MatIconModule, MatButtonModule, MatButtonToggleModule,
    MatFormFieldModule, MatSelectModule, MatInputModule,
    MatPaginatorModule, MatSnackBarModule,
    DecimalPipe, MoneyPipe,
    SofascoreBadgeComponent, SofascoreCardBadgeComponent,
    StarterBadgeComponent, StarterCardBadgeComponent,
    ScrollTopComponent, PageHeaderComponent,
  ],
  templateUrl: './market.component.html',
  styleUrl: './market.component.scss'
})
export class MarketComponent {
  private svc = inject(AnalyticsService);
  private http = inject(HttpClient);
  private snackBar = inject(MatSnackBar);
  private championshipService = inject(ChampionshipService);
  private breakpointObserver = inject(BreakpointObserver);

  // Responsive
  isMobile = toSignal(
    this.breakpointObserver.observe([Breakpoints.Handset]).pipe(map(r => r.matches)),
    { initialValue: false }
  );

  // State
  loading = signal(true);
  allPlayers = signal<WatchlistPlayer[]>([]);
  togglingFav = signal(false);
  viewMode = signal<'cards' | 'table'>(
    (localStorage.getItem('futmondo_view_watchlist') as 'cards' | 'table') || 'table'
  );
  sortField = signal<string>('average');
  pageIndex = signal(0);
  pageSize = signal(
    parseInt(localStorage.getItem('futmondo_watchlist_pageSize') || '20', 10)
  );

  // Filters
  filterName = signal('');
  filterTeam = signal('');
  filterPosition = signal('');

  // Derived: available teams for filter dropdown
  availableTeams = computed(() => {
    const teams = [...new Set(this.allPlayers().map(p => p.team).filter(t => t))];
    return teams.sort();
  });

  // Derived: filtered players
  filteredPlayers = computed(() => {
    let players = this.allPlayers();
    const name = this.filterName().toLowerCase();
    const team = this.filterTeam();
    const position = this.filterPosition().toLowerCase();

    if (name) {
      players = players.filter(p => p.name.toLowerCase().includes(name));
    }
    if (team) {
      players = players.filter(p => p.team === team);
    }
    if (position) {
      players = players.filter(p =>
        p.position.toLowerCase().includes(position) ||
        (p.position2 && p.position2.toLowerCase().includes(position))
      );
    }
    return players;
  });

  // Table
  dataSource = new MatTableDataSource<WatchlistPlayer>([]);
  columns = ['name', 'position', 'team', 'sofascore_rating', 'starter_pct', 'average', 'value', 'ratio', 'streak', 'trend', 'favorite'];

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  @ViewChild(MatPaginator) set matPaginator(paginator: MatPaginator) {
    if (paginator) this.dataSource.paginator = paginator;
  }

  // Cards: sorted list (from filtered)
  sortedCards = computed(() => {
    const players = [...this.filteredPlayers()];
    const field = this.sortField();
    return players.sort((a: any, b: any) => {
      switch (field) {
        case 'name': return (a.name || '').localeCompare(b.name || '');
        case 'team': return (a.team || '').localeCompare(b.team || '');
        case 'value_asc': return (a.value || 0) - (b.value || 0);
        case 'value_desc': return (b.value || 0) - (a.value || 0);
        default: return (b[field] ?? -Infinity) - (a[field] ?? -Infinity);
      }
    });
  });

  // Cards: paginated slice
  paginatedCards = computed(() => {
    const start = this.pageIndex() * this.pageSize();
    return this.sortedCards().slice(start, start + this.pageSize());
  });

  constructor() {
    if (this.isMobile() && !localStorage.getItem('futmondo_view_watchlist')) {
      this.viewMode.set('cards');
    }
    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.load();
    });
  }

  async load() {
    try {
      const d = await this.svc.getWatchlist(this.championshipService.activeId());
      const players: WatchlistPlayer[] = d.players;
      this.allPlayers.set(players);
      this.applyFiltersToTable();
    } catch { /* silently fail */ }
    finally { this.loading.set(false); }
  }

  // --- Filters ---
  onFilterName(event: Event) {
    this.filterName.set((event.target as HTMLInputElement).value);
    this.pageIndex.set(0);
    this.applyFiltersToTable();
  }

  clearFilterName() {
    this.filterName.set('');
    this.pageIndex.set(0);
    this.applyFiltersToTable();
  }

  onFilterTeam(value: string) {
    this.filterTeam.set(value);
    this.pageIndex.set(0);
    this.applyFiltersToTable();
  }

  onFilterPosition(value: string) {
    this.filterPosition.set(value);
    this.pageIndex.set(0);
    this.applyFiltersToTable();
  }

  private applyFiltersToTable() {
    this.dataSource.data = this.filteredPlayers();
  }

  // --- View mode ---
  setViewMode(mode: 'cards' | 'table') {
    this.viewMode.set(mode);
    localStorage.setItem('futmondo_view_watchlist', mode);
    this.pageIndex.set(0);
  }

  // --- Sort ---
  onSortChange(value: string) {
    this.sortField.set(value);
    this.pageIndex.set(0);
  }

  onTableSort() {
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  // --- Pagination ---
  onPage(event: PageEvent) {
    this.pageIndex.set(event.pageIndex);
    this.pageSize.set(event.pageSize);
    localStorage.setItem('futmondo_watchlist_pageSize', String(event.pageSize));
  }

  // --- Favorites ---
  async toggleFavorite(player: WatchlistPlayer, event: Event) {
    event.stopPropagation();
    this.togglingFav.set(true);

    const championshipId = this.championshipService.activeId();
    const params = new HttpParams()
      .set('championship_id', championshipId)
      .set('player_id', player.player_id);

    try {
      if (player.is_favorite) {
        // Unmark
        await firstValueFrom(this.http.post<any>('/api/v1/favorites/unfollow', {}, { params }));
        player.is_favorite = false;
        this.snackBar.open(`☆ ${player.name} quitado de favoritos`, 'OK', { duration: 2500 });
      } else {
        // Mark
        await firstValueFrom(this.http.post<any>('/api/v1/favorites/mark', {}, { params }));
        player.is_favorite = true;
        this.snackBar.open(`⭐ ${player.name} marcado como favorito`, 'OK', { duration: 2500 });
      }
      // Trigger re-render
      this.allPlayers.set([...this.allPlayers()]);
      this.applyFiltersToTable();
    } catch (err: any) {
      this.snackBar.open(`❌ Error: ${err?.error?.detail || 'No se pudo actualizar'}`, 'OK', { duration: 4000 });
    } finally {
      this.togglingFav.set(false);
    }
  }

  // --- Helpers ---
  getPlayerPhoto = getPlayerPhoto;
  getTeamLogo = getTeamLogoById;
  getPositionKey = getPositionKey;
  getPositionLabel = getPositionLabel;
  onImgError = onImgError;
}
