import { Component, inject, signal, effect, ViewChild, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog } from '@angular/material/dialog';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { ChampionshipService } from '../../core/services/championship.service';
import { SofascoreDetailDialogComponent } from '../market/sofascore-detail-dialog.component';

interface RosterPlayer {
  player_id: string;
  name: string;
  slug: string;
  position: string;
  position2: string;
  team: string;
  team_logo: string;
  value: number;
  buy_price: number;
  profit: number;
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

interface RosterSummary {
  total_players: number;
  total_value: number;
  total_invested: number;
  total_profit: number;
}

@Component({
  selector: 'app-my-roster',
  standalone: true,
  imports: [
    MatTableModule, MatSortModule, MatProgressSpinnerModule,
    MatChipsModule, MatIconModule, MatTooltipModule, MoneyPipe
  ],
  template: `
    <h1>👤 Mi Plantilla</h1>
    <p class="description">Tu plantilla actual con rendimiento y valoración.</p>

    @if (loading()) {
      <div class="loading"><mat-spinner diameter="40" /> <span>Cargando plantilla...</span></div>
    } @else if (error()) {
      <div class="error-message">{{ error() }}</div>
    } @else {
      <!-- Summary banner -->
      @if (summary()) {
        <div class="summary-banner">
          <div class="info-item">
            <span class="info-label">Jugadores</span>
            <span class="info-value">{{ summary()!.total_players }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Valor plantilla</span>
            <span class="info-value">{{ summary()!.total_value | money }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Invertido</span>
            <span class="info-value invested">{{ summary()!.total_invested | money }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Plusvalía</span>
            <span class="info-value" [class]="summary()!.total_profit >= 0 ? 'profit-positive' : 'profit-negative'">
              {{ summary()!.total_profit >= 0 ? '+' : '' }}{{ summary()!.total_profit | money }}
            </span>
          </div>
        </div>
      }

      <!-- Sell recommendations widget -->
      @if (sellRecommendations().length) {
        <div class="sell-widget">
          <h3>🔻 Ventas recomendadas</h3>
          <div class="sell-cards">
            @for (r of sellRecommendations(); track r.name) {
              <div class="sell-card">
                <div class="sell-card-header">
                  <img [src]="getPlayerPhoto(r.slug)" class="sell-photo" [alt]="r.name" loading="lazy"
                       (error)="$event.target.style.display='none'" />
                  <div>
                    <strong>{{ r.name }}</strong>
                    <span class="sell-team">{{ r.team }}</span>
                  </div>
                </div>
                <div class="sell-card-reasons">
                  @for (reason of r.reasons; track reason) {
                    <span class="sell-reason">{{ reason }}</span>
                  }
                </div>
                <div class="sell-card-footer">
                  <span class="sell-profit" [class]="r.profit >= 0 ? 'trend-up' : 'trend-down'">
                    {{ r.profit >= 0 ? '+' : '' }}{{ r.profit | money }}
                  </span>
                  <span class="sell-value">{{ r.value | money }}</span>
                </div>
              </div>
            }
          </div>
        </div>
      }

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

          <!-- Profit -->
          <ng-container matColumnDef="profit">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Plusvalía</th>
            <td mat-cell *matCellDef="let p" [class]="p.profit >= 0 ? 'trend-up' : 'trend-down'">
              {{ p.profit >= 0 ? '+' : '' }}{{ p.profit | money }}
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
    .summary-banner {
      display: flex; gap: 32px; flex-wrap: wrap; padding: 20px 24px;
      background: var(--mat-sys-surface-container); border-radius: 12px; margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .info-item { display: flex; flex-direction: column; gap: 4px; }
    .info-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--mat-sys-on-surface-variant); font-weight: 600; }
    .info-value { font-size: 1.3em; font-weight: 700; color: var(--mat-sys-on-surface); }
    .info-value.invested { color: #1565c0; }
    .info-value.profit-positive { color: #2e7d32; }
    .info-value.profit-negative { color: #d32f2f; }
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    .sell-widget { margin-bottom: 24px; }
    .sell-widget h3 { margin: 0 0 12px; font-size: 1em; }
    .sell-cards { display: flex; gap: 16px; flex-wrap: wrap; }
    .sell-card {
      flex: 1; min-width: 220px; max-width: 320px;
      padding: 16px; border-radius: 12px;
      background: var(--mat-sys-surface-container);
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
      display: flex; flex-direction: column; gap: 10px;
    }
    .sell-card-header { display: flex; align-items: center; gap: 10px; }
    .sell-photo { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: #f0f0f0; flex-shrink: 0; }
    .sell-card-header div { display: flex; flex-direction: column; }
    .sell-team { font-size: 0.8em; color: var(--mat-sys-on-surface-variant); }
    .sell-card-reasons { display: flex; flex-wrap: wrap; gap: 6px; }
    .sell-reason { font-size: 0.75em; padding: 2px 8px; border-radius: 10px; background: #fee2e2; color: #991b1b; font-weight: 600; }
    .sell-card-footer { display: flex; justify-content: space-between; align-items: center; }
    .sell-profit { font-weight: 700; font-size: 0.9em; }
    .sell-value { font-size: 0.85em; color: var(--mat-sys-on-surface-variant); }
    table { width: 100%; }
    .player-cell { }
    .player-cell .player-wrapper { display: inline-flex; align-items: center; gap: 10px; }
    .player-photo { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; background: #f0f0f0; flex-shrink: 0; vertical-align: middle; }
    .player-info { display: inline; }
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
    .sofascore-green { background: #16a34a; }
    .sofascore-yellow { background: #ca8a04; }
    .sofascore-red { background: #dc2626; }
    .sofascore-na { color: var(--mat-sys-on-surface-variant); }
    .starter-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 700; color: #fff; }
    .starter-high { background: #16a34a; }
    .starter-mid { background: #ca8a04; }
    .starter-low { background: #dc2626; }
    .matches-info { font-size: 0.8em; color: var(--mat-sys-on-surface-variant); margin-left: 4px; }
    .average-main { font-weight: 700; font-size: 1.1em; }
    .average-detail { font-size: 0.75em; color: var(--mat-sys-on-surface-variant); margin-left: 6px; white-space: nowrap; }
  `]
})
export class MyRosterComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);
  private dialog = inject(MatDialog);

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  dataSource = new MatTableDataSource<RosterPlayer>([]);
  loading = signal(true);
  error = signal('');
  summary = signal<RosterSummary | null>(null);

  columns = ['name', 'position', 'team', 'sofascore_rating', 'starter_pct', 'value', 'change', 'profit', 'points', 'average'];

  sellRecommendations = computed(() => {
    const players = this.dataSource.data;
    if (!players.length) return [];

    const candidates: { name: string; slug: string; team: string; value: number; profit: number; reasons: string[]; score: number }[] = [];

    for (const p of players) {
      const reasons: string[] = [];
      let score = 0;

      // Dropping in value
      if (p.change < 0) {
        reasons.push(`▼ ${this.formatMoney(Math.abs(p.change))}`);
        score += 2;
        if (p.change < -100000) score += 1;
      }

      // Low starter %
      if (p.starter_pct != null && p.starter_pct < 70) {
        reasons.push(`Titular ${p.starter_pct}%`);
        score += 3;
        if (p.starter_pct < 40) score += 2;
      }

      // Negative profit (losing money)
      if (p.profit < 0) {
        reasons.push(`Pérdida ${this.formatMoney(Math.abs(p.profit))}`);
        score += 1;
      }

      // Low average points (when season is running)
      if (p.matches > 2 && p.average < 3) {
        reasons.push(`Media ${p.average.toFixed(1)} pts`);
        score += 2;
      }

      if (score >= 3 && reasons.length >= 2) {
        candidates.push({ name: p.name, slug: p.slug, team: p.team, value: p.value, profit: p.profit, reasons, score });
      }
    }

    return candidates.sort((a, b) => b.score - a.score).slice(0, 3);
  });

  private formatMoney(value: number): string {
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M€`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K€`;
    return `${value}€`;
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
      const params = new HttpParams().set('championship_id', this.championshipService.activeId());
      const data = await firstValueFrom(this.http.get<any>('/api/v1/roster/my', { params }));
      this.dataSource.data = data.players || [];
      this.summary.set(data.summary || null);
    } catch (err: any) {
      this.error.set(err?.error?.detail || err.message || 'Error cargando plantilla');
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
    if (rating >= 7) return 'sofascore-green';
    if (rating >= 6) return 'sofascore-yellow';
    return 'sofascore-red';
  }

  getStarterClass(pct: number): string {
    if (pct >= 75) return 'starter-high';
    if (pct >= 40) return 'starter-mid';
    return 'starter-low';
  }

  getAverageTooltip(p: RosterPlayer): string {
    let tip = `Media: ${p.average.toFixed(1)}`;
    if (p.home_average != null) tip += ` | Casa: ${p.home_average.toFixed(1)}`;
    if (p.away_average != null) tip += ` | Fuera: ${p.away_average.toFixed(1)}`;
    tip += ` | ${p.matches} partidos`;
    return tip;
  }

  openSofascoreDetail(player: RosterPlayer, event: Event) {
    event.stopPropagation();
    this.dialog.open(SofascoreDetailDialogComponent, {
      data: { player_name: player.name },
      width: '550px',
    });
  }
}
