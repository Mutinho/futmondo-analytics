import { Component, ChangeDetectionStrategy, inject, signal, computed, effect, ViewChild } from '@angular/core';
import { injectIsMobile } from '../../shared/utils/responsive';
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
import { DecimalPipe } from '@angular/common';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { SofascoreBadgeComponent } from '../../shared/components/sofascore-badge.component';
import { SofascoreCardBadgeComponent } from '../../shared/components/sofascore-card-badge.component';
import { StarterBadgeComponent } from '../../shared/components/starter-badge.component';
import { StarterCardBadgeComponent } from '../../shared/components/starter-card-badge.component';
import { ScrollTopComponent } from '../../shared/components/scroll-top.component';
import { PageHeaderComponent } from '../../shared/components/page-header.component';
import { StatsService } from '../../core/services/stats.service';
import { ChampionshipService } from '../../core/services/championship.service';
import { getPlayerPhoto, getPositionKey, getPositionLabel, onImgError } from '../../shared/utils/player.utils';
import { getTeamLogoById } from '../../shared/utils/team-logos';

interface ClausulablePlayer {
  player_id: string;
  player_name: string;
  slug: string;
  position: string;
  position2: string;
  team: string;
  real_team_id: string;
  owner_name: string;
  average_last_five: number;
  average_overall: number;
  clause_price: number;
  suggested_clause: number;
  value: number;
  score: number;
  sofascore_rating: number | null;
  sofascore_url: string | null;
  starter_pct: number | null;
}

@Component({
  selector: 'app-clausulable',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    MatTableModule, MatSortModule, MatProgressSpinnerModule,
    MatIconModule, MatButtonModule, MatButtonToggleModule,
    MatFormFieldModule, MatSelectModule, MatInputModule,
    MatPaginatorModule, DecimalPipe, MoneyPipe,
    SofascoreBadgeComponent, SofascoreCardBadgeComponent,
    StarterBadgeComponent, StarterCardBadgeComponent,
    ScrollTopComponent, PageHeaderComponent,
  ],
  templateUrl: './clausulable.component.html',
  styleUrl: './clausulable.component.scss'
})
export class ClausulableComponent {
  private statsService = inject(StatsService);
  private championshipService = inject(ChampionshipService);

  isMobile = injectIsMobile();

  loading = signal(true);
  error = signal<string | null>(null);
  allPlayers = signal<ClausulablePlayer[]>([]);
  viewMode = signal<'cards' | 'table'>(
    (localStorage.getItem('futmondo_view_clausulable') as 'cards' | 'table') || 'table'
  );
  sortField = signal<string>('score');
  pageIndex = signal(0);
  pageSize = signal(parseInt(localStorage.getItem('futmondo_clausulable_pageSize') || '20', 10));

  // Filters
  filterName = signal('');
  filterOwner = signal('');
  filterPosition = signal('');
  filterMaxClause = signal('0');

  availableOwners = computed(() => {
    const owners = [...new Set(this.allPlayers().map(p => p.owner_name).filter(o => o))];
    return owners.sort();
  });

  filteredPlayers = computed(() => {
    let players = this.allPlayers();
    const name = this.filterName().toLowerCase();
    const owner = this.filterOwner();
    const position = this.filterPosition().toLowerCase();
    const maxClause = parseInt(this.filterMaxClause(), 10);
    if (name) players = players.filter(p => p.player_name.toLowerCase().includes(name));
    if (owner) players = players.filter(p => p.owner_name === owner);
    if (position) players = players.filter(p => p.position.toLowerCase().includes(position) || (p.position2 && p.position2.toLowerCase().includes(position)));
    if (maxClause > 0) players = players.filter(p => p.clause_price <= maxClause);
    return players;
  });

  dataSource = new MatTableDataSource<ClausulablePlayer>([]);
  columns = ['player_name', 'position', 'team', 'owner_name', 'sofascore_rating', 'average_last_five', 'value', 'clause_price', 'score'];

  @ViewChild(MatSort) set matSort(sort: MatSort) { if (sort) this.dataSource.sort = sort; }
  @ViewChild(MatPaginator) set matPaginator(paginator: MatPaginator) { if (paginator) this.dataSource.paginator = paginator; }

  sortedCards = computed(() => {
    const players = [...this.filteredPlayers()];
    const field = this.sortField();
    return players.sort((a: any, b: any) => {
      switch (field) {
        case 'player_name': return (a.player_name || '').localeCompare(b.player_name || '');
        case 'clause_price_asc': return (a.clause_price || 0) - (b.clause_price || 0);
        case 'clause_price_desc': return (b.clause_price || 0) - (a.clause_price || 0);
        default: return (b[field] ?? -Infinity) - (a[field] ?? -Infinity);
      }
    });
  });

  paginatedCards = computed(() => {
    const start = this.pageIndex() * this.pageSize();
    return this.sortedCards().slice(start, start + this.pageSize());
  });

  // Shared utils as class properties for template access
  getPlayerPhoto = getPlayerPhoto;
  getPositionKey = getPositionKey;
  getPositionLabel = getPositionLabel;
  onImgError = onImgError;

  getTeamLogo = getTeamLogoById;

  constructor() {
    if (this.isMobile() && !localStorage.getItem('futmondo_view_clausulable')) this.viewMode.set('cards');
    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadData();
    });
  }

  async loadData() {
    this.loading.set(true);
    this.error.set(null);
    try {
      const data = await this.statsService.getClausulablePlayers(this.championshipService.activeId()) as any;
      this.allPlayers.set(data.players || []);
      this.applyFiltersToTable();
    } catch (e: any) {
      this.error.set('Error al cargar jugadores clausulables.');
    }
    finally { this.loading.set(false); }
  }

  onFilterName(event: Event) { this.filterName.set((event.target as HTMLInputElement).value); this.pageIndex.set(0); this.applyFiltersToTable(); }
  clearFilterName() { this.filterName.set(''); this.pageIndex.set(0); this.applyFiltersToTable(); }
  onFilterOwner(value: string) { this.filterOwner.set(value); this.pageIndex.set(0); this.applyFiltersToTable(); }
  onFilterPosition(value: string) { this.filterPosition.set(value); this.pageIndex.set(0); this.applyFiltersToTable(); }
  onFilterMaxClause(value: string) { this.filterMaxClause.set(value); this.pageIndex.set(0); this.applyFiltersToTable(); }
  private applyFiltersToTable() { this.dataSource.data = this.filteredPlayers(); }

  setViewMode(mode: 'cards' | 'table') { this.viewMode.set(mode); localStorage.setItem('futmondo_view_clausulable', mode); this.pageIndex.set(0); }
  onSortChange(value: string) { this.sortField.set(value); this.pageIndex.set(0); }
  onPage(event: PageEvent) { this.pageIndex.set(event.pageIndex); this.pageSize.set(event.pageSize); localStorage.setItem('futmondo_clausulable_pageSize', String(event.pageSize)); }
}
