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
  template: `
    <app-page-header title="Agentes Libres" icon="person_search" description="Jugadores libres (sin dueño) ordenados por media. Útil para encontrar fichajes baratos con buen rendimiento." />

    @if (loading()) {
      <div class="loading"><mat-spinner diameter="32" /> <span>Cargando watchlist...</span></div>
    } @else if (!allPlayers().length) {
      <div class="empty">💹 No hay datos de watchlist disponibles.</div>
    } @else {
      <!-- Filters -->
      <div class="filters-row">
        <mat-form-field appearance="outline" class="filter-name" subscriptSizing="dynamic">
          <mat-label>Buscar jugador</mat-label>
          <input matInput [value]="filterName()" (input)="onFilterName($event)" placeholder="Nombre...">
          @if (filterName()) {
            <button matSuffix mat-icon-button (click)="clearFilterName()">
              <mat-icon>close</mat-icon>
            </button>
          }
        </mat-form-field>
        <mat-form-field appearance="outline" class="filter-select" subscriptSizing="dynamic">
          <mat-label>Club</mat-label>
          <mat-select [value]="filterTeam()" (selectionChange)="onFilterTeam($event.value)">
            <mat-option value="">Todos</mat-option>
            @for (t of availableTeams(); track t) {
              <mat-option [value]="t">{{ t }}</mat-option>
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

      <p class="count">{{ filteredPlayers().length }} jugadores{{ filterName() || filterTeam() || filterPosition() ? ' (filtrados)' : '' }}</p>

      <!-- Controls row -->
      <div class="controls-row">
        @if (viewMode() === 'cards') {
          <mat-form-field appearance="outline" class="sort-field" subscriptSizing="dynamic">
            <mat-label>Ordenar por</mat-label>
            <mat-select [value]="sortField()" (selectionChange)="onSortChange($event.value)">
              <mat-option value="average">Media (mayor)</mat-option>
              <mat-option value="ratio">Ratio Pts/M€ (mayor)</mat-option>
              <mat-option value="streak">En forma primero</mat-option>
              <mat-option value="trend">Tendencia (mayor)</mat-option>
              <mat-option value="value_desc">Precio (mayor)</mat-option>
              <mat-option value="value_asc">Precio (menor)</mat-option>
              <mat-option value="sofascore_rating">Sofascore</mat-option>
              <mat-option value="starter_pct">% Titularidad</mat-option>
              <mat-option value="name">Nombre (A-Z)</mat-option>
              <mat-option value="team">Equipo (A-Z)</mat-option>
            </mat-select>
          </mat-form-field>
        }
        <mat-button-toggle-group [value]="viewMode()" (change)="setViewMode($event.value)" hideSingleSelectionIndicator>
          <mat-button-toggle value="cards"><mat-icon>grid_view</mat-icon></mat-button-toggle>
          <mat-button-toggle value="table"><mat-icon>table_rows</mat-icon></mat-button-toggle>
        </mat-button-toggle-group>
      </div>

      <!-- Table view -->
      @if (viewMode() === 'table') {
        <div class="table-container">
          <table mat-table [dataSource]="dataSource" matSort (matSortChange)="onTableSort()">
            <!-- Favorite -->
            <ng-container matColumnDef="favorite">
              <th mat-header-cell *matHeaderCellDef></th>
              <td mat-cell *matCellDef="let p">
                @if (p.is_favorite) {
                  <button mat-mini-fab class="fav-remove-btn"
                          (click)="toggleFavorite(p, $event)" [disabled]="togglingFav()"
                          title="Quitar de favoritos">
                    <mat-icon>delete</mat-icon>
                  </button>
                } @else {
                  <button mat-mini-fab class="fav-add-btn"
                          (click)="toggleFavorite(p, $event)" [disabled]="togglingFav()"
                          title="Añadir a favoritos">
                    <mat-icon>star_border</mat-icon>
                  </button>
                }
              </td>
            </ng-container>

            <!-- Name -->
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Jugador</th>
              <td mat-cell *matCellDef="let p" class="player-cell">
                <div class="player-wrapper">
                  <img [src]="getPlayerPhoto(p.slug)" class="player-photo" [alt]="p.name" loading="lazy"
                       (error)="onImgError($event)" />
                  @if (p.sofascore_url) {
                    <a [href]="p.sofascore_url" target="_blank" class="player-link"><strong>{{ p.name }}</strong></a>
                  } @else {
                    <strong>{{ p.name }}</strong>
                  }
                </div>
              </td>
            </ng-container>

            <!-- Position -->
            <ng-container matColumnDef="position">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Pos</th>
              <td mat-cell *matCellDef="let p">
                <span class="pos-chip" [class]="'pos-' + getPositionKey(p.position)">{{ getPositionLabel(p.position) }}</span>
                @if (p.position2) {
                  <span class="pos-chip pos-secondary" [class]="'pos-' + getPositionKey(p.position2)">{{ getPositionLabel(p.position2) }}</span>
                }
              </td>
            </ng-container>

            <!-- Team -->
            <ng-container matColumnDef="team">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Equipo</th>
              <td mat-cell *matCellDef="let p" class="team-cell">
                <div class="team-wrapper">
                  <img [src]="getTeamLogo(p.real_team_id)" class="team-logo" [alt]="p.team" loading="lazy"
                       (error)="onImgError($event)" />
                  <span>{{ p.team }}</span>
                </div>
              </td>
            </ng-container>

            <!-- Sofascore -->
            <ng-container matColumnDef="sofascore_rating">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Sofa</th>
              <td mat-cell *matCellDef="let p">
                <app-sofascore-badge [rating]="p.sofascore_rating" />
              </td>
            </ng-container>

            <!-- Starter % -->
            <ng-container matColumnDef="starter_pct">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Titular</th>
              <td mat-cell *matCellDef="let p">
                @if (p.starter_pct != null) {
                  <app-starter-badge [pct]="p.starter_pct" />
                } @else {
                  <span class="na">-</span>
                }
              </td>
            </ng-container>

            <!-- Average -->
            <ng-container matColumnDef="average">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Media</th>
              <td mat-cell *matCellDef="let p" class="average-cell">{{ p.average | number:'1.1-1' }}</td>
            </ng-container>

            <!-- Value -->
            <ng-container matColumnDef="value">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Precio</th>
              <td mat-cell *matCellDef="let p">{{ p.value | money }}</td>
            </ng-container>

            <!-- Ratio -->
            <ng-container matColumnDef="ratio">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Ratio</th>
              <td mat-cell *matCellDef="let p" class="ratio-cell">{{ p.ratio | number:'1.2-2' }}</td>
            </ng-container>

            <!-- Streak -->
            <ng-container matColumnDef="streak">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Forma</th>
              <td mat-cell *matCellDef="let p" class="streak-cell">
                @if (p.streak > 0) { 🔥 } @else { - }
              </td>
            </ng-container>

            <!-- Trend -->
            <ng-container matColumnDef="trend">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Tend.</th>
              <td mat-cell *matCellDef="let p" [class]="p.trend > 0 ? 'trend-up' : p.trend < 0 ? 'trend-down' : 'trend-neutral'">
                @if (p.trend !== 0) { {{ p.trend > 0 ? '▲' : '▼' }}{{ p.trend | number:'1.1-1' }} } @else { - }
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="columns"></tr>
            <tr mat-row *matRowDef="let row; columns: columns" [class.fav-row]="row.is_favorite"></tr>
          </table>
        </div>
        <mat-paginator
          [length]="filteredPlayers().length"
          [pageSize]="pageSize()"
          [pageSizeOptions]="[20, 50, 100]"
          [pageIndex]="pageIndex()"
          (page)="onPage($event)"
          showFirstLastButtons />
      }

      <!-- Cards view -->
      @if (viewMode() === 'cards') {
        <div class="cards-container">
          @for (p of paginatedCards(); track p.player_id) {
            <article class="player-card" [class.fav-card]="p.is_favorite">
              <div class="card-header">
                @if (p.sofascore_url) {
                  <a [href]="p.sofascore_url" target="_blank" class="card-avatar">
                    <img [src]="getPlayerPhoto(p.slug)" [alt]="p.name" loading="lazy"
                         (error)="onImgError($event)" />
                  </a>
                } @else {
                  <div class="card-avatar">
                    <img [src]="getPlayerPhoto(p.slug)" [alt]="p.name" loading="lazy"
                         (error)="onImgError($event)" />
                  </div>
                }
                <div class="card-name-block">
                  <h3 class="card-player-name">
                    @if (p.sofascore_url) {
                      <a [href]="p.sofascore_url" target="_blank" class="player-link">{{ p.name }}</a>
                    } @else {
                      {{ p.name }}
                    }
                  </h3>
                  <div class="card-team-row">
                    <img [src]="getTeamLogo(p.real_team_id)" class="card-team-logo" [alt]="p.team" loading="lazy"
                         (error)="onImgError($event)" />
                    <span class="card-team-name">{{ p.team }}</span>
                  </div>
                  <div class="card-badges">
                    <app-sofascore-card-badge [rating]="p.sofascore_rating" />
                    <app-starter-card-badge [pct]="p.starter_pct" />
                  </div>
                </div>
                <div class="card-top-actions">
                  <span class="pos-chip" [class]="'pos-' + getPositionKey(p.position)">{{ getPositionLabel(p.position) }}</span>
                  @if (p.position2) {
                    <span class="pos-chip pos-secondary" [class]="'pos-' + getPositionKey(p.position2)">{{ getPositionLabel(p.position2) }}</span>
                  }
                </div>
              </div>
              <div class="card-stats-box">
                <div class="card-stats-grid">
                  <div class="card-stat-item">
                    <span class="card-stat-label">MEDIA</span>
                    <span class="card-stat-val average-highlight">{{ p.average | number:'1.1-1' }}</span>
                  </div>
                  <div class="card-stat-item">
                    <span class="card-stat-label">PRECIO</span>
                    <span class="card-stat-val">{{ p.value | money }}</span>
                  </div>
                </div>
                <div class="card-stats-grid card-stats-bottom">
                  <div class="card-stat-item">
                    <span class="card-stat-label">RATIO PTS/M€</span>
                    <span class="card-stat-val ratio-highlight">{{ p.ratio | number:'1.2-2' }}</span>
                  </div>
                  <div class="card-stat-item">
                    <span class="card-stat-label">FORMA</span>
                    <span class="card-stat-val" [class.streak-highlight]="p.streak > 0">@if (p.streak > 0) { 🔥 En forma } @else { - }</span>
                  </div>
                </div>
                <div class="card-stats-grid card-stats-bottom">
                  <div class="card-stat-item">
                    <span class="card-stat-label">TENDENCIA</span>
                    <span class="card-stat-val" [class.trend-up]="p.trend > 0" [class.trend-down]="p.trend < 0">
                      @if (p.trend !== 0) { {{ p.trend > 0 ? '↗' : '↘' }} {{ p.trend | number:'1.1-1' }} } @else { - }
                    </span>
                  </div>
                  <div class="card-stat-item">
                    <span class="card-stat-label">POSICIÓN</span>
                    <span class="card-stat-val">{{ getPositionLabel(p.position) }}@if (p.position2) { / {{ getPositionLabel(p.position2) }} }</span>
                  </div>
                </div>
              </div>
              @if (p.is_favorite) {
                <button class="card-fav-remove-btn" (click)="toggleFavorite(p, $event)" [disabled]="togglingFav()">
                  <mat-icon>delete</mat-icon>
                  QUITAR DE FAVORITOS
                </button>
              } @else {
                <button class="card-fav-add-btn" (click)="toggleFavorite(p, $event)" [disabled]="togglingFav()">
                  <mat-icon>star_border</mat-icon>
                  AÑADIR A FAVORITOS
                </button>
              }
            </article>
          }
        </div>
        <mat-paginator
          [length]="sortedCards().length"
          [pageSize]="pageSize()"
          [pageSizeOptions]="[20, 50, 100]"
          [pageIndex]="pageIndex()"
          (page)="onPage($event)"
          showFirstLastButtons />
        <app-scroll-top />
      }
    }
  `,
  styles: [`
    .loading { display: flex; align-items: center; gap: 16px; padding: 60px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .empty { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); font-size: 1.1em; }
    .count { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin-bottom: 16px; }

    /* Filters */
    .filters-row { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; align-items: center; }
    .filter-name { flex: 2; min-width: 180px; }
    .filter-select { flex: 1; min-width: 130px; }

    /* Controls */
    .controls-row { display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-bottom: 16px; }
    .sort-field { flex: 1; font-size: 0.9em; }

    /* Table */
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .player-cell .player-wrapper { display: inline-flex; align-items: center; gap: 10px; }
    .player-photo { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: #f0f0f0; flex-shrink: 0; }
    .team-cell .team-wrapper { display: inline-flex; align-items: center; gap: 8px; }
    .team-logo { width: 32px; height: 32px; object-fit: contain; flex-shrink: 0; }
    .player-link { color: var(--mat-sys-on-surface); text-decoration: none; }
    .player-link:hover { text-decoration: underline; }
    .average-cell { font-weight: 700; color: var(--mat-sys-primary); }
    .ratio-cell { font-weight: 700; color: #4CAF50; }
    .streak-cell { font-weight: 700; }
    .trend-up { color: #2e7d32; font-weight: 600; }
    .trend-down { color: #d32f2f; font-weight: 600; }
    .trend-neutral { color: var(--mat-sys-on-surface-variant); }
    .na { color: var(--mat-sys-on-surface-variant); }

    /* Favorite buttons - table */
    .fav-remove-btn { transform: scale(0.7); background-color: #d32f2f !important; color: white !important; }
    .fav-add-btn { transform: scale(0.7); background-color: var(--mat-sys-primary) !important; color: white !important; }
    .fav-row { background: rgba(251, 191, 36, 0.18) !important; }
    .fav-row:hover { background: rgba(251, 191, 36, 0.28) !important; }
    :host-context(.dark-theme) .fav-row { background: rgba(251, 191, 36, 0.15) !important; }

    /* Position chips */
    .pos-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; color: #333; }
    .pos-secondary { margin-left: 3px; opacity: 0.8; }
    .pos-fwd { background: #e57373; }
    .pos-mid { background: #64b5f6; }
    .pos-def { background: #ffb74d; }
    .pos-gk { background: #4caf50; }

    /* Cards */
    .cards-container { display: grid; grid-template-columns: 1fr; gap: 16px; }
    @media (min-width: 900px) { .cards-container { grid-template-columns: repeat(2, 1fr); } }
    @media (min-width: 1300px) { .cards-container { grid-template-columns: repeat(3, 1fr); } }
    @media (min-width: 1700px) { .cards-container { grid-template-columns: repeat(4, 1fr); } }

    .player-card {
      padding: 20px; border-radius: 16px;
      background: var(--mat-sys-surface-container);
      border: 1px solid var(--mat-sys-outline-variant);
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .player-card.fav-card {
      border-color: rgba(255, 185, 0, 0.7);
      border-width: 2px;
      background: linear-gradient(135deg, rgba(255, 200, 0, 0.22), rgba(255, 170, 0, 0.08));
      box-shadow: 0 2px 12px rgba(255, 185, 0, 0.2);
    }
    :host-context(.dark-theme) .player-card { border-color: rgba(20, 255, 0, 0.15); }
    :host-context(.dark-theme) .player-card.fav-card { border-color: rgba(255, 200, 0, 0.6); border-width: 2px; background: linear-gradient(135deg, rgba(255, 200, 0, 0.25), rgba(255, 170, 0, 0.1)); box-shadow: 0 2px 12px rgba(255, 185, 0, 0.15); }
    .card-header { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 16px; position: relative; }
    .card-avatar { width: 56px; height: 56px; border-radius: 50%; overflow: hidden; border: 2px solid var(--mat-sys-primary); padding: 2px; flex-shrink: 0; display: block; }
    .card-avatar img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
    .card-name-block { flex: 1; display: flex; flex-direction: column; gap: 4px; }
    .card-player-name { font-size: 1.15em; font-weight: 700; margin: 0; color: var(--mat-sys-on-surface); }
    .card-team-row { display: flex; align-items: center; gap: 8px; }
    .card-team-logo { width: 22px; height: 22px; object-fit: contain; }
    .card-team-name { font-size: 0.9em; color: var(--mat-sys-on-surface-variant); font-weight: 500; }
    .card-top-actions { position: absolute; top: 0; right: 0; display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
    .card-fav-remove-btn, .card-fav-add-btn { width: 100%; padding: 12px; border-radius: 12px; font-weight: 700; font-size: 0.8em; letter-spacing: 0.03em; text-transform: uppercase; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 12px; transition: background 0.15s; border: 1px solid; }
    .card-fav-remove-btn { border-color: #d32f2f; background: rgba(211, 47, 47, 0.08); color: #d32f2f; }
    .card-fav-remove-btn:hover { background: rgba(211, 47, 47, 0.15); }
    .card-fav-add-btn { border-color: var(--mat-sys-primary); background: rgba(76, 175, 80, 0.08); color: var(--mat-sys-primary); }
    .card-fav-add-btn:hover { background: rgba(76, 175, 80, 0.18); }
    .card-fav-remove-btn:disabled, .card-fav-add-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .card-fav-remove-btn mat-icon, .card-fav-add-btn mat-icon { font-size: 18px; width: 18px; height: 18px; }
    .card-badges { display: flex; gap: 10px; margin-top: 8px; }
    .card-stats-box { background: var(--mat-sys-surface-container-highest); border-radius: 12px; padding: 14px; border: 1px solid var(--mat-sys-outline-variant); }
    :host-context(.dark-theme) .card-stats-box { background: rgba(53,53,52,0.5); border-color: rgba(132,150,124,0.2); }
    .card-stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .card-stats-bottom { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--mat-sys-outline-variant); }
    .card-stat-item { display: flex; flex-direction: column; gap: 2px; }
    .card-stat-label { font-size: 0.65em; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--mat-sys-on-surface-variant); }
    .card-stat-val { font-size: 1.05em; font-weight: 600; color: var(--mat-sys-on-surface); }
    .average-highlight { color: var(--mat-sys-primary); font-weight: 800; }
    .ratio-highlight { color: #4CAF50; font-weight: 800; }
    .streak-highlight { color: #FF6D00; font-weight: 800; }
    :host-context(.dark-theme) .ratio-highlight { color: #14FF00; }
  `]
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

  // Team logo map for real_team_id → logo filename
  private teamLogoMap: Record<string, string> = {
    '504e581e4d8bec9a670000c6': 'real-madrid.png',
    '504e581e4d8bec9a670000c7': 'barcelona.png',
    '504e581e4d8bec9a670000c8': 'atletico-de-madrid.png',
    '504e581e4d8bec9a670000c9': 'athletic-de-bilbao.png',
    '504e581e4d8bec9a670000ca': 'rayo-vallecano.png',
    '504e581e4d8bec9a670000cb': 'valencia.png',
    '504e581e4d8bec9a670000cc': 'betis.png',
    '504e581e4d8bec9a670000cd': 'getafe.png',
    '504e581e4d8bec9a670000ce': 'real-sociedad.png',
    '504e581e4d8bec9a670000cf': 'levante.png',
    '504e581e4d8bec9a670000d0': 'espanyol.png',
    '504e581e4d8bec9a670000d1': 'osasuna.png',
    '504e581e4d8bec9a670000d5': 'sevilla.png',
    '504e581e4d8bec9a670000d6': 'malaga.png',
    '504e581e4d8bec9a670000d8': 'deportivo-de-la-coruna.png',
    '504e581e4d8bec9a670000d9': 'celta-de-vigo.png',
    '51b889b1e401a15f2c0000f0': 'elche.png',
    '51b890f5b986415a2c000012': 'villarreal.png',
    '52038563b8d07d930b00008a': 'deportivo-alaves.png',
    '520e4ee4a776cc826b00004b': 'racing-santander.png',
  };

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
      const players: WatchlistPlayer[] = d?.players || [];
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
  getPlayerPhoto(slug: string): string {
    return slug ? `https://static01.mondocore.com/futmondo/img/faces/64/${slug}.png` : '';
  }

  getTeamLogo(realTeamId: string): string {
    const logo = this.teamLogoMap[realTeamId];
    return logo ? `https://static02.mondocore.com/futmondo/img/teams/64/${logo}` : '';
  }

  getPositionKey(position: string): string {
    const p = (position || '').toLowerCase();
    if (p.includes('delantero')) return 'fwd';
    if (p.includes('centrocampista')) return 'mid';
    if (p.includes('defensa')) return 'def';
    if (p.includes('portero')) return 'gk';
    return 'mid';
  }

  getPositionLabel(position: string): string {
    const p = (position || '').toLowerCase();
    if (p.includes('delantero')) return 'DL';
    if (p.includes('centrocampista')) return 'MC';
    if (p.includes('defensa')) return 'DF';
    if (p.includes('portero')) return 'PT';
    return position || '-';
  }

  onImgError(event: Event) {
    (event.target as HTMLElement).style.display = 'none';
  }
}
