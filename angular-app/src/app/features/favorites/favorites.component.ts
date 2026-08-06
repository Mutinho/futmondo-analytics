import { Component, inject, signal, effect, ViewChild } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
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
    MatChipsModule, MatIconModule, MatTooltipModule, MatButtonModule, MatSnackBarModule, MoneyPipe
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
    .pos-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; color: #fff; }
    .pos-secondary { margin-left: 3px; opacity: 0.8; }
    .pos-fwd { background: #e57373; }
    .pos-mid { background: #64b5f6; }
    .pos-def { background: #ffb74d; }
    .pos-gk { background: #ffd54f; color: #5d4037; }
    .trend-up { color: #2e7d32; font-weight: 600; }
    .trend-down { color: #d32f2f; font-weight: 600; }
    .trend-neutral { color: var(--mat-sys-on-surface-variant); }
    .player-link { color: #1565c0; text-decoration: none; &:hover { text-decoration: underline; } }
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
    .matches-info { font-size: 0.8em; color: var(--mat-sys-on-surface-variant); margin-left: 4px; }
    .average-main { font-weight: 700; font-size: 1.1em; }
    .average-detail { font-size: 0.75em; color: var(--mat-sys-on-surface-variant); margin-left: 6px; white-space: nowrap; }
    .unfollow-btn { transform: scale(0.7); background-color: #d32f2f; color: white; }
  `]
})
export class FavoritesComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  dataSource = new MatTableDataSource<FavoritePlayer>([]);
  loading = signal(true);
  error = signal('');
  unfollowing = signal(false);

  columns = ['name', 'position', 'team', 'sofascore_rating', 'starter_pct', 'value', 'change', 'points', 'average', 'actions'];

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
