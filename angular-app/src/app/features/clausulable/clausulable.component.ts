import { Component, inject, signal, computed, effect, ViewChild } from '@angular/core';
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
  imports: [
    MatTableModule, MatSortModule, MatProgressSpinnerModule,
    MatIconModule, MatButtonModule, MatButtonToggleModule,
    MatFormFieldModule, MatSelectModule, MatInputModule,
    MatPaginatorModule, DecimalPipe, MoneyPipe,
    SofascoreBadgeComponent, SofascoreCardBadgeComponent,
    StarterBadgeComponent, StarterCardBadgeComponent,
    ScrollTopComponent, PageHeaderComponent,
  ],
  template: `
    <app-page-header title="Clausulables" icon="sports_soccer" description="Jugadores con mejor relación calidad/cláusula para clausular a otros equipos." />

    @if (loading()) {
      <div class="loading"><mat-spinner diameter="36" /> <span>Cargando clausulables...</span></div>
    } @else if (!allPlayers().length) {
      <div class="empty">⚽ No hay datos de jugadores clausulables.</div>
    } @else {
      <!-- Filters -->
      <div class="filters-row">
        <mat-form-field appearance="outline" class="filter-name" subscriptSizing="dynamic">
          <mat-label>Buscar jugador</mat-label>
          <input matInput [value]="filterName()" (input)="onFilterName($event)" placeholder="Nombre...">
          @if (filterName()) {
            <button matSuffix mat-icon-button (click)="clearFilterName()"><mat-icon>close</mat-icon></button>
          }
        </mat-form-field>
        <mat-form-field appearance="outline" class="filter-select" subscriptSizing="dynamic">
          <mat-label>Dueño</mat-label>
          <mat-select [value]="filterOwner()" (selectionChange)="onFilterOwner($event.value)">
            <mat-option value="">Todos</mat-option>
            @for (o of availableOwners(); track o) {
              <mat-option [value]="o">{{ o }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
        <mat-form-field appearance="outline" class="filter-select" subscriptSizing="dynamic">
          <mat-label>Posición</mat-label>
          <mat-select [value]="filterPosition()" (selectionChange)="onFilterPosition($event.value)">
            <mat-option value="">Todas</mat-option>
            <mat-option value="Portero">PT</mat-option>
            <mat-option value="Defensa">DF</mat-option>
            <mat-option value="Centrocampista">MC</mat-option>
            <mat-option value="Delantero">DL</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <!-- Clause price filter -->
      <div class="clause-filter-row">
        <span class="clause-filter-label">Inferior a:</span>
        <mat-button-toggle-group [value]="filterMaxClause()" (change)="onFilterMaxClause($event.value)" hideSingleSelectionIndicator>
          <mat-button-toggle value="0">Todas</mat-button-toggle>
          <mat-button-toggle value="10000000">10M</mat-button-toggle>
          <mat-button-toggle value="20000000">20M</mat-button-toggle>
          <mat-button-toggle value="30000000">30M</mat-button-toggle>
          <mat-button-toggle value="40000000">40M</mat-button-toggle>
          <mat-button-toggle value="50000000">50M</mat-button-toggle>
          <mat-button-toggle value="60000000">60M</mat-button-toggle>
        </mat-button-toggle-group>
      </div>

      <p class="count">{{ filteredPlayers().length }} jugadores clausulables</p>

      <!-- Controls -->
      <div class="controls-row">
        @if (viewMode() === 'cards') {
          <mat-form-field appearance="outline" class="sort-field" subscriptSizing="dynamic">
            <mat-label>Ordenar por</mat-label>
            <mat-select [value]="sortField()" (selectionChange)="onSortChange($event.value)">
              <mat-option value="score">Score (mayor)</mat-option>
              <mat-option value="average_last_five">Media últ.5 (mayor)</mat-option>
              <mat-option value="clause_price_asc">Cláusula (menor)</mat-option>
              <mat-option value="clause_price_desc">Cláusula (mayor)</mat-option>
              <mat-option value="sofascore_rating">Sofascore</mat-option>
              <mat-option value="player_name">Nombre (A-Z)</mat-option>
            </mat-select>
          </mat-form-field>
        }
        <mat-button-toggle-group [value]="viewMode()" (change)="setViewMode($event.value)" hideSingleSelectionIndicator>
          <mat-button-toggle value="cards"><mat-icon>grid_view</mat-icon></mat-button-toggle>
          <mat-button-toggle value="table"><mat-icon>table_rows</mat-icon></mat-button-toggle>
        </mat-button-toggle-group>
      </div>

      <!-- Table -->
      @if (viewMode() === 'table') {
        <div class="table-container">
          <table mat-table [dataSource]="dataSource" matSort>
            <ng-container matColumnDef="player_name">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Jugador</th>
              <td mat-cell *matCellDef="let p" class="player-cell">
                <div class="player-wrapper">
                  <img [src]="getPlayerPhoto(p.slug)" class="player-photo" [alt]="p.player_name" loading="lazy" (error)="onImgError($event)" />
                  <strong>{{ p.player_name }}</strong>
                </div>
              </td>
            </ng-container>
            <ng-container matColumnDef="position">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Pos</th>
              <td mat-cell *matCellDef="let p">
                <span class="pos-chip" [class]="'pos-' + getPositionKey(p.position)">{{ getPositionLabel(p.position) }}</span>
              </td>
            </ng-container>
            <ng-container matColumnDef="team">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Equipo Real</th>
              <td mat-cell *matCellDef="let p">
                <div class="team-wrapper">
                  <img [src]="getTeamLogo(p.real_team_id)" class="team-logo" [alt]="p.team" loading="lazy" (error)="onImgError($event)" />
                  <span>{{ p.team }}</span>
                </div>
              </td>
            </ng-container>
            <ng-container matColumnDef="owner_name">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Dueño</th>
              <td mat-cell *matCellDef="let p" class="owner-cell">{{ p.owner_name }}</td>
            </ng-container>
            <ng-container matColumnDef="sofascore_rating">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Sofa</th>
              <td mat-cell *matCellDef="let p"><app-sofascore-badge [rating]="p.sofascore_rating" /></td>
            </ng-container>
            <ng-container matColumnDef="average_last_five">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Media</th>
              <td mat-cell *matCellDef="let p" class="average-cell">{{ p.average_last_five | number:'1.1-1' }}</td>
            </ng-container>
            <ng-container matColumnDef="clause_price">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Cláusula</th>
              <td mat-cell *matCellDef="let p">{{ p.clause_price | money }}</td>
            </ng-container>
            <ng-container matColumnDef="value">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Valor</th>
              <td mat-cell *matCellDef="let p">{{ p.value | money }}</td>
            </ng-container>
            <ng-container matColumnDef="score">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Score</th>
              <td mat-cell *matCellDef="let p" class="score-cell">{{ (p.score * 100) | number:'1.0-0' }}%</td>
            </ng-container>
            <tr mat-header-row *matHeaderRowDef="columns"></tr>
            <tr mat-row *matRowDef="let row; columns: columns"></tr>
          </table>
        </div>
        <mat-paginator [length]="filteredPlayers().length" [pageSize]="pageSize()" [pageSizeOptions]="[20, 50, 100]" [pageIndex]="pageIndex()" (page)="onPage($event)" showFirstLastButtons />
      }

      <!-- Cards -->
      @if (viewMode() === 'cards') {
        <div class="cards-container">
          @for (p of paginatedCards(); track p.player_id) {
            <article class="player-card">
              <div class="card-header">
                <div class="card-avatar">
                  <img [src]="getPlayerPhoto(p.slug)" [alt]="p.player_name" loading="lazy" (error)="onImgError($event)" />
                </div>
                <div class="card-name-block">
                  <h3 class="card-player-name">{{ p.player_name }}</h3>
                  <div class="card-team-row">
                    <img [src]="getTeamLogo(p.real_team_id)" class="card-team-logo" [alt]="p.team" loading="lazy" (error)="onImgError($event)" />
                    <span class="card-team-name">{{ p.team }}</span>
                  </div>
                  <div class="card-badges">
                    <app-sofascore-card-badge [rating]="p.sofascore_rating" />
                    <app-starter-card-badge [pct]="p.starter_pct" />
                  </div>
                </div>
                <div class="card-top-right">
                  <span class="pos-chip" [class]="'pos-' + getPositionKey(p.position)">{{ getPositionLabel(p.position) }}</span>
                  <span class="score-badge">{{ (p.score * 100) | number:'1.0-0' }}%</span>
                </div>
              </div>
              <div class="card-stats-box">
                <div class="card-stats-grid">
                  <div class="card-stat-item">
                    <span class="card-stat-label">MEDIA ÚLT.5</span>
                    <span class="card-stat-val average-highlight">{{ p.average_last_five | number:'1.1-1' }}</span>
                  </div>
                  <div class="card-stat-item">
                    <span class="card-stat-label">CLÁUSULA</span>
                    <span class="card-stat-val">{{ p.clause_price | money }}</span>
                  </div>
                </div>
                <div class="card-stats-grid card-stats-bottom">
                  <div class="card-stat-item">
                    <span class="card-stat-label">VALOR</span>
                    <span class="card-stat-val">{{ p.value | money }}</span>
                  </div>
                  <div class="card-stat-item">
                    <span class="card-stat-label">DUEÑO</span>
                    <span class="card-stat-val owner-val">{{ p.owner_name }}</span>
                  </div>
                </div>
              </div>
            </article>
          }
        </div>
        <mat-paginator [length]="sortedCards().length" [pageSize]="pageSize()" [pageSizeOptions]="[20, 50, 100]" [pageIndex]="pageIndex()" (page)="onPage($event)" showFirstLastButtons />
        <app-scroll-top />
      }
    }
  `,
  styles: [`
    .loading { display: flex; align-items: center; gap: 16px; padding: 60px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .empty { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); font-size: 1.1em; }
    .count { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin-bottom: 16px; }
    .filters-row { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; align-items: center; }
    .filter-name { flex: 2; min-width: 180px; }
    .filter-select { flex: 1; min-width: 130px; }
    .clause-filter-row { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
    .clause-filter-label { font-size: 0.9em; font-weight: 600; color: var(--mat-sys-on-surface-variant); white-space: nowrap; }
    .controls-row { display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-bottom: 16px; }
    .sort-field { flex: 1; font-size: 0.9em; }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .player-cell .player-wrapper { display: inline-flex; align-items: center; gap: 10px; }
    .player-photo { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: #f0f0f0; flex-shrink: 0; }
    .team-wrapper { display: inline-flex; align-items: center; gap: 8px; }
    .team-logo { width: 28px; height: 28px; object-fit: contain; flex-shrink: 0; }
    .average-cell { font-weight: 700; color: var(--mat-sys-primary); }
    .score-cell { font-weight: 700; color: #4CAF50; }
    .owner-cell { color: var(--mat-sys-on-surface-variant); font-style: italic; }
    .pos-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; color: #333; }
    .pos-fwd { background: #e57373; } .pos-mid { background: #64b5f6; } .pos-def { background: #ffb74d; } .pos-gk { background: #4caf50; }
    .cards-container { display: grid; grid-template-columns: 1fr; gap: 16px; }
    @media (min-width: 900px) { .cards-container { grid-template-columns: repeat(2, 1fr); } }
    @media (min-width: 1300px) { .cards-container { grid-template-columns: repeat(3, 1fr); } }
    @media (min-width: 1700px) { .cards-container { grid-template-columns: repeat(4, 1fr); } }
    .player-card { padding: 20px; border-radius: 16px; background: var(--mat-sys-surface-container); border: 1px solid var(--mat-sys-outline-variant); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    :host-context(.dark-theme) .player-card { border-color: rgba(20, 255, 0, 0.15); }
    .card-header { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 16px; position: relative; }
    .card-avatar { width: 56px; height: 56px; border-radius: 50%; overflow: hidden; border: 2px solid var(--mat-sys-primary); padding: 2px; flex-shrink: 0; }
    .card-avatar img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
    .card-name-block { flex: 1; display: flex; flex-direction: column; gap: 4px; }
    .card-player-name { font-size: 1.15em; font-weight: 700; margin: 0; color: var(--mat-sys-on-surface); }
    .card-team-row { display: flex; align-items: center; gap: 8px; }
    .card-team-logo { width: 22px; height: 22px; object-fit: contain; }
    .card-team-name { font-size: 0.9em; color: var(--mat-sys-on-surface-variant); font-weight: 500; }
    .card-top-right { position: absolute; top: 0; right: 0; display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
    .score-badge { background: #4CAF50; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 700; }
    .card-badges { display: flex; gap: 10px; margin-top: 8px; }
    .card-stats-box { background: var(--mat-sys-surface-container-highest); border-radius: 12px; padding: 14px; border: 1px solid var(--mat-sys-outline-variant); }
    :host-context(.dark-theme) .card-stats-box { background: rgba(53,53,52,0.5); border-color: rgba(132,150,124,0.2); }
    .card-stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .card-stats-bottom { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--mat-sys-outline-variant); }
    .card-stat-item { display: flex; flex-direction: column; gap: 2px; }
    .card-stat-label { font-size: 0.65em; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--mat-sys-on-surface-variant); }
    .card-stat-val { font-size: 1.05em; font-weight: 600; color: var(--mat-sys-on-surface); }
    .average-highlight { color: var(--mat-sys-primary); font-weight: 800; }
    .owner-val { font-style: italic; font-size: 0.9em; }
  `]
})
export class ClausulableComponent {
  private statsService = inject(StatsService);
  private championshipService = inject(ChampionshipService);
  private breakpointObserver = inject(BreakpointObserver);

  isMobile = toSignal(
    this.breakpointObserver.observe([Breakpoints.Handset]).pipe(map(r => r.matches)),
    { initialValue: false }
  );

  loading = signal(true);
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

  private teamLogoMap: Record<string, string> = {
    '504e581e4d8bec9a670000c6': 'real-madrid.png', '504e581e4d8bec9a670000c7': 'barcelona.png',
    '504e581e4d8bec9a670000c8': 'atletico-de-madrid.png', '504e581e4d8bec9a670000c9': 'athletic-de-bilbao.png',
    '504e581e4d8bec9a670000ca': 'rayo-vallecano.png', '504e581e4d8bec9a670000cb': 'valencia.png',
    '504e581e4d8bec9a670000cc': 'betis.png', '504e581e4d8bec9a670000cd': 'getafe.png',
    '504e581e4d8bec9a670000ce': 'real-sociedad.png', '504e581e4d8bec9a670000cf': 'levante.png',
    '504e581e4d8bec9a670000d0': 'espanyol.png', '504e581e4d8bec9a670000d1': 'osasuna.png',
    '504e581e4d8bec9a670000d5': 'sevilla.png', '504e581e4d8bec9a670000d6': 'malaga.png',
    '504e581e4d8bec9a670000d8': 'deportivo-de-la-coruna.png', '504e581e4d8bec9a670000d9': 'celta-de-vigo.png',
    '51b889b1e401a15f2c0000f0': 'elche.png', '51b890f5b986415a2c000012': 'villarreal.png',
    '52038563b8d07d930b00008a': 'deportivo-alaves.png', '520e4ee4a776cc826b00004b': 'racing-santander.png',
  };

  constructor() {
    if (this.isMobile() && !localStorage.getItem('futmondo_view_clausulable')) this.viewMode.set('cards');
    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadData();
    });
  }

  async loadData() {
    this.loading.set(true);
    try {
      const data = await this.statsService.getClausulablePlayers(this.championshipService.activeId()) as any;
      this.allPlayers.set(data.players || []);
      this.applyFiltersToTable();
    } catch { }
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

  getPlayerPhoto(slug: string): string { return slug ? `https://static01.mondocore.com/futmondo/img/faces/64/${slug}.png` : ''; }
  getTeamLogo(id: string): string { const l = this.teamLogoMap[id]; return l ? `https://static02.mondocore.com/futmondo/img/teams/64/${l}` : ''; }
  getPositionKey(p: string): string { const s = (p || '').toLowerCase(); if (s.includes('delantero')) return 'fwd'; if (s.includes('centrocampista')) return 'mid'; if (s.includes('defensa')) return 'def'; if (s.includes('portero')) return 'gk'; return 'mid'; }
  getPositionLabel(p: string): string { const s = (p || '').toLowerCase(); if (s.includes('delantero')) return 'DL'; if (s.includes('centrocampista')) return 'MC'; if (s.includes('defensa')) return 'DF'; if (s.includes('portero')) return 'PT'; return p || '-'; }
  onImgError(event: Event) { (event.target as HTMLElement).style.display = 'none'; }
}
