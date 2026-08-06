import { Component, inject, signal, effect, ViewChild } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { ChampionshipService } from '../../core/services/championship.service';
import { SofascoreDetailDialogComponent } from '../market/sofascore-detail-dialog.component';
import { ConfirmDialogComponent } from '../market/confirm-dialog.component';

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
  imports: [
    MatTableModule, MatSortModule, MatProgressSpinnerModule,
    MatChipsModule, MatIconModule, MatTooltipModule, MatButtonModule, MatButtonToggleModule, MatSnackBarModule, MoneyPipe
  ],
  template: `
    <h1>⭐ Favoritos</h1>
    <p class="description">Jugadores libres que tienes marcados como favoritos. Se actualizan con cada sincronización.</p>

    @if (loading()) {
      <div class="loading"><mat-spinner diameter="40" /> <span>Cargando favoritos...</span></div>
    } @else if (error()) {
      <div class="error-message">{{ error() }}</div>
    } @else if (!dataSource.data.length) {
      <div class="empty">⭐ No tienes jugadores favoritos libres. Marca jugadores como favoritos en la app de Futmondo y sincroniza.</div>
    } @else {
      <p class="count">{{ dataSource.data.length }} jugadores favoritos libres</p>
      <!-- View toggle + sort -->
      <div class="view-toggle">
        @if (viewMode() === 'cards') {
          <select class="sort-select" [value]="sortField()" (change)="onSortChange($event)">
            <option value="value">Valor</option>
            <option value="change">Tendencia</option>
            <option value="sofascore_rating">Sofascore</option>
            <option value="starter_pct">Titularidad</option>
            <option value="points">Puntos</option>
          </select>
        }
        <mat-button-toggle-group [value]="viewMode()" (change)="setViewMode($event.value)" hideSingleSelectionIndicator>
          <mat-button-toggle value="cards"><mat-icon>grid_view</mat-icon></mat-button-toggle>
          <mat-button-toggle value="table"><mat-icon>table_rows</mat-icon></mat-button-toggle>
        </mat-button-toggle-group>
      </div>
      @if (viewMode() === 'table') {
      <div class="table-container">
        <table mat-table [dataSource]="dataSource" matSort>
          <!-- Name -->
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
                <img [src]="getTeamLogo(p.team_logo)" class="team-logo" [alt]="p.team" loading="lazy"
                     (error)="$event.target.style.display='none'" />
                <span>{{ p.team }}</span>
              </div>
            </td>
          </ng-container>

          <!-- Sofascore -->
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

          <!-- Starter % -->
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

          <!-- Value -->
          <ng-container matColumnDef="value">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Valor</th>
            <td mat-cell *matCellDef="let p">{{ p.value | money }}</td>
          </ng-container>

          <!-- Trend -->
          <ng-container matColumnDef="change">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Tendencia</th>
            <td mat-cell *matCellDef="let p" [class]="p.change > 0 ? 'trend-up' : p.change < 0 ? 'trend-down' : 'trend-neutral'">
              @if (p.change !== 0) {
                {{ p.change > 0 ? '▲' : '▼' }} {{ p.change | money }}
              } @else {
                -
              }
            </td>
          </ng-container>

          <!-- Points -->
          <ng-container matColumnDef="points">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Puntos</th>
            <td mat-cell *matCellDef="let p">
              <strong>{{ p.points }}</strong>
              @if (p.matches > 0) {
                <span class="matches-info">({{ p.matches }}J)</span>
              }
            </td>
          </ng-container>

          <!-- Average -->
          <ng-container matColumnDef="average">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Media</th>
            <td mat-cell *matCellDef="let p">
              @if (p.average > 0) {
                <span class="average-main" [matTooltip]="getAverageTooltip(p)">{{ p.average.toFixed(1) }}</span>
                @if (p.home_average != null || p.away_average != null) {
                  <span class="average-detail">
                    @if (p.home_average != null) { 🏠{{ p.home_average.toFixed(1) }} }
                    @if (p.away_average != null) { ✈️{{ p.away_average.toFixed(1) }} }
                  </span>
                }
              } @else {
                <span class="sofascore-na">-</span>
              }
            </td>
          </ng-container>

          <!-- Unfollow -->
          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let p">
              <button mat-mini-fab class="unfollow-btn"
                      (click)="unfollow(p, $event)"
                      [disabled]="unfollowing()"
                      title="Dejar de seguir">
                <mat-icon>delete</mat-icon>
              </button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns"></tr>
        </table>
      </div>
      }

      @if (viewMode() === 'cards') {
      <div class="cards-container">
        @for (p of dataSource.data; track p.player_id) {
          <article class="player-card">
            <div class="card-header">
              @if (p.sofascore_url) {
                <a [href]="p.sofascore_url" target="_blank" class="card-avatar">
                  <img [src]="getPlayerPhoto(p.slug)" [alt]="p.name" loading="lazy"
                       (error)="$event.target.style.display='none'" />
                </a>
              } @else {
                <div class="card-avatar">
                  <img [src]="getPlayerPhoto(p.slug)" [alt]="p.name" loading="lazy"
                       (error)="$event.target.style.display='none'" />
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
                  <img [src]="getTeamLogo(p.team_logo)" class="card-team-logo" [alt]="p.team" loading="lazy"
                       (error)="$event.target.style.display='none'" />
                  <span class="card-team-name">{{ p.team }}</span>
                </div>
                <div class="card-badges">
                  @if (p.sofascore_rating != null) {
                    <span class="card-badge sofascore" (click)="openSofascoreDetail(p, $event)">
                      <span class="card-badge-label">Sofa</span>
                      <span class="card-badge-value">{{ p.sofascore_rating.toFixed(1) }}</span>
                    </span>
                  }
                  @if (p.starter_pct != null) {
                    <span class="card-badge starter">
                      <span class="card-badge-label">Tit</span>
                      <span class="card-badge-value">{{ p.starter_pct }}%</span>
                    </span>
                  }
                </div>
              </div>
              <span class="pos-chip card-pos-top" [class]="'pos-' + getPositionKey(p.position)">{{ getPositionLabel(p.position) }}</span>
              @if (p.position2) {
                <span class="pos-chip card-pos-top card-pos-secondary" [class]="'pos-' + getPositionKey(p.position2)">{{ getPositionLabel(p.position2) }}</span>
              }
            </div>
            <div class="card-stats-box">
              <div class="card-stats-grid">
                <div class="card-stat-item">
                  <span class="card-stat-label">VALOR</span>
                  <span class="card-stat-val">{{ p.value | money }}</span>
                </div>
                <div class="card-stat-item">
                  <span class="card-stat-label">TENDENCIA</span>
                  <span class="card-stat-val trend" [class.up]="p.change > 0" [class.down]="p.change < 0">
                    @if (p.change !== 0) { {{ p.change > 0 ? '↗' : '↘' }} {{ p.change | money }} } @else { - }
                  </span>
                </div>
              </div>
              <div class="card-stats-grid" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--mat-sys-outline-variant);">
                <div class="card-stat-item">
                  <span class="card-stat-label">PUNTOS</span>
                  <span class="card-stat-val">{{ p.points > 0 ? p.points : '-' }}@if (p.matches > 0) { ({{ p.matches }}J) }</span>
                </div>
                <div class="card-stat-item">
                  <span class="card-stat-label">MEDIA</span>
                  <span class="card-stat-val">{{ p.average > 0 ? p.average.toFixed(1) : '-' }}</span>
                </div>
              </div>
            </div>
            <button class="card-unfollow-btn" (click)="unfollow(p, $event)" [disabled]="unfollowing()">
              <mat-icon>delete</mat-icon>
              QUITAR DE FAVORITOS
            </button>
          </article>
        }
      </div>
      }
    }
  `,
  styles: [`
    .description { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin-bottom: 24px; }
    .loading { display: flex; align-items: center; gap: 16px; padding: 60px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .error-message { padding: 16px; background: #ffebee; color: #d32f2f; border-radius: 8px; }
    .empty { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); font-size: 1.1em; }
    .count { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin-bottom: 16px; }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .player-cell { }
    .player-cell .player-wrapper { display: inline-flex; align-items: center; gap: 10px; }
    .player-photo { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; background: #f0f0f0; flex-shrink: 0; vertical-align: middle; }
    .team-cell { }
    .team-cell .team-wrapper { display: inline-flex; align-items: center; gap: 8px; }
    .team-logo { width: 40px; height: 40px; object-fit: contain; flex-shrink: 0; vertical-align: middle; }
    .pos-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; color: #333; }
    .pos-secondary { margin-left: 3px; opacity: 0.8; }
    .pos-fwd { background: #e57373; }
    .pos-mid { background: #64b5f6; }
    .pos-def { background: #ffb74d; }
    .pos-gk { background: #4caf50; }
    .trend-up { color: #2e7d32; font-weight: 600; }
    .trend-down { color: #d32f2f; font-weight: 600; }
    .trend-neutral { color: var(--mat-sys-on-surface-variant); }
    .player-link { color: var(--mat-sys-on-surface); text-decoration: none; }
    .player-link:hover { text-decoration: underline; }
    .sofascore-badge { display: inline-block; padding: 6px 8px; border-radius: 8px; font-size: 0.8em; font-weight: 700; color: #fff; cursor: pointer; transition: transform 0.15s; width: fit-content; text-align: center; line-height: 1; }
    .sofascore-badge:hover { transform: scale(1.1); }
    .sofascore-s90 { background: #374DF5; }
    .sofascore-s80 { background: #00ADC4; }
    .sofascore-s70 { background: #00C424; }
    .sofascore-s65 { background: #D9AF00; }
    .sofascore-s60 { background: #ED7E07; }
    .sofascore-na { color: var(--mat-sys-on-surface-variant); }
    .starter-badge { display: inline-block; padding: 6px 8px; border-radius: 8px; font-size: 0.8em; font-weight: 700; color: #fff; width: fit-content; text-align: center; line-height: 1; }
    .starter-high { background: #16a34a; }
    .starter-mid { background: #ca8a04; }
    .starter-low { background: #dc2626; }
    .matches-info { font-size: 0.8em; color: var(--mat-sys-on-surface-variant); margin-left: 4px; }
    .average-main { font-weight: 700; font-size: 1.1em; }
    .average-detail { font-size: 0.75em; color: var(--mat-sys-on-surface-variant); margin-left: 6px; white-space: nowrap; }
    .unfollow-btn { transform: scale(0.7); background-color: #d32f2f; color: white; }
    .view-toggle { display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-bottom: 16px; }
    .sort-select { flex: 1; padding: 8px 12px; border-radius: 8px; border: 1px solid var(--mat-sys-outline-variant); background: var(--mat-sys-surface-container); color: var(--mat-sys-on-surface); font-size: 0.85em; font-weight: 600; cursor: pointer; }
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
    .dark-theme .player-card { border-color: rgba(20, 255, 0, 0.15); }
    .card-header { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 16px; position: relative; }
    .card-avatar { width: 56px; height: 56px; border-radius: 50%; overflow: hidden; border: 2px solid var(--mat-sys-primary); padding: 2px; flex-shrink: 0; display: block; }
    .card-avatar img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
    .card-name-block { flex: 1; display: flex; flex-direction: column; gap: 4px; }
    .card-player-name { font-size: 1.25em; font-weight: 700; margin: 0; color: var(--mat-sys-on-surface); }
    .card-team-row { display: flex; align-items: center; gap: 8px; }
    .card-team-logo { width: 22px; height: 22px; object-fit: contain; }
    .card-team-name { font-size: 0.95em; color: var(--mat-sys-on-surface-variant); font-weight: 500; }
    .card-pos-top { position: absolute; top: 0; right: 0; }
    .card-pos-secondary { top: 28px; opacity: 0.8; }
    .card-badges { display: flex; gap: 10px; margin-top: 8px; }
    .card-badge { display: inline-flex; align-items: center; gap: 5px; padding: 5px 10px; border-radius: 8px; font-size: 0.85em; font-weight: 700; border: 1px solid; }
    .card-badge.sofascore { background: rgba(0, 196, 36, 0.1); color: #00C424; border-color: rgba(0, 196, 36, 0.25); cursor: pointer; }
    .card-badge.starter { background: rgba(0, 196, 36, 0.1); color: #00C424; border-color: rgba(0, 196, 36, 0.25); }
    .card-badge-label { font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.03em; opacity: 0.8; }
    .card-badge-value { font-weight: 800; font-size: 1.1em; }
    .card-stats-box { background: var(--mat-sys-surface-container-highest); border-radius: 12px; padding: 14px; border: 1px solid var(--mat-sys-outline-variant); margin-bottom: 12px; }
    .dark-theme .card-stats-box { background: rgba(53,53,52,0.5); border-color: rgba(132,150,124,0.2); }
    .card-stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .card-stat-item { display: flex; flex-direction: column; gap: 2px; }
    .card-stat-label { font-size: 0.65em; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--mat-sys-on-surface-variant); }
    .card-stat-val { font-size: 1.05em; font-weight: 600; color: var(--mat-sys-on-surface); }
    .card-stat-val.trend.up { color: #00C424; }
    .dark-theme .card-stat-val.trend.up { color: #14FF00; }
    .card-stat-val.trend.down { color: #d32f2f; }
    .card-unfollow-btn { width: 100%; padding: 12px; border-radius: 12px; border: 1px solid #d32f2f; background: rgba(211, 47, 47, 0.08); color: #d32f2f; font-weight: 700; font-size: 0.8em; letter-spacing: 0.03em; text-transform: uppercase; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 12px; transition: background 0.15s; }
    .card-unfollow-btn:hover { background: rgba(211, 47, 47, 0.15); }
    .card-unfollow-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .card-unfollow-btn mat-icon { font-size: 18px; width: 18px; height: 18px; }
  `]
})
export class FavoritesComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  private breakpointObserver = inject(BreakpointObserver);

  isMobile = toSignal(
    this.breakpointObserver.observe([Breakpoints.Handset]).pipe(map(r => r.matches)),
    { initialValue: false }
  );

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
      const params = new HttpParams().set('championship_id', this.championshipService.activeId());
      const data = await firstValueFrom(this.http.get<any>('/api/v1/favorites/my', { params }));
      this.dataSource.data = data.players || [];
    } catch (err: any) {
      this.error.set(err?.error?.detail || err.message || 'Error cargando favoritos');
    } finally {
      this.loading.set(false);
    }
  }

  getPlayerPhoto(slug: string): string {
    return `https://static01.mondocore.com/futmondo/img/faces/64/${slug}.png`;
  }

  getTeamLogo(logo: string): string {
    return `https://static02.mondocore.com/futmondo/img/teams/64/${logo}`;
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

  onSortChange(event: Event) {
    this.sortField.set((event.target as HTMLSelectElement).value);
    this.sortCards();
  }

  setViewMode(mode: 'cards' | 'table') {
    this.viewMode.set(mode);
    localStorage.setItem('futmondo_view_favorites', mode);
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
    return position;
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
      const params = new HttpParams()
        .set('championship_id', this.championshipService.activeId())
        .set('player_id', player.player_id);
      await firstValueFrom(this.http.post<any>('/api/v1/favorites/unfollow', {}, { params }));
      this.snackBar.open(`⭐ ${player.name} eliminado de favoritos`, 'OK', { duration: 3000 });
      await this.loadData();
    } catch (err: any) {
      this.snackBar.open(`❌ Error: ${err?.error?.detail || 'No se pudo eliminar'}`, 'OK', { duration: 4000 });
    } finally {
      this.unfollowing.set(false);
    }
  }
}
