import { Component, ChangeDetectionStrategy, inject, signal, effect, ViewChild, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
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
import { SofascoreDetailDialogComponent } from '../market/sofascore-detail-dialog.component';
import { PageHeaderComponent } from '../../shared/components/page-header.component';
import { getPlayerPhoto, getTeamLogo, getPositionKey, getPositionLabel, onImgError } from '../../shared/utils/player.utils';

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
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    MatTableModule, MatSortModule, MatProgressSpinnerModule,
    MatChipsModule, MatIconModule, MatTooltipModule, MatButtonModule, MatButtonToggleModule, MatFormFieldModule, MatSelectModule, MoneyPipe, StarterBadgeComponent, StarterCardBadgeComponent, SofascoreBadgeComponent, SofascoreCardBadgeComponent, ScrollTopComponent, PageHeaderComponent, LoadingStateComponent, ViewToggleComponent, PositionChipComponent
  ],
  templateUrl: './my-roster.component.html',
  styleUrl: './my-roster.component.scss'
})
export class MyRosterComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);
  private dialog = inject(MatDialog);

  isMobile = injectIsMobile();

  viewMode = signal<'cards' | 'table'>(
    (localStorage.getItem('futmondo_view_roster') as 'cards' | 'table') || 'table'
  );
  sortField = signal<string>('value');

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  dataSource = new MatTableDataSource<RosterPlayer>([]);
  loading = signal(true);
  error = signal('');
  summary = signal<RosterSummary | null>(null);

  columns = ['name', 'position', 'team', 'sofascore_rating', 'starter_pct', 'value', 'change', 'profit', 'points', 'average'];

  sortOptions = [
    { value: 'value', label: 'Valor' },
    { value: 'change', label: 'Tendencia' },
    { value: 'profit', label: 'Plusvalía' },
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
    if (this.isMobile() && !localStorage.getItem('futmondo_view_roster')) this.viewMode.set('cards');

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
    localStorage.setItem('futmondo_view_roster', mode);
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
