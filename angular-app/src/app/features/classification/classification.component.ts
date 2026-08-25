import { Component, inject, signal, computed, effect, ViewChild } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { DecimalPipe } from '@angular/common';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { PageHeaderComponent } from '../../shared/components/page-header.component';
import { ScrollTopComponent } from '../../shared/components/scroll-top.component';
import { AnalyticsService } from '../../core/services/analytics.service';
import { ChampionshipService } from '../../core/services/championship.service';

interface ClassificationEntry {
  rank: number;
  team_name: string;
  total_points: number;
  average_points: number;
  matches_count: number;
  max_points: number;
  min_points: number;
  trend: number;
  momentum: number;
}

@Component({
  selector: 'app-classification',
  standalone: true,
  imports: [
    MatProgressSpinnerModule, MatTableModule, MatSortModule,
    MatButtonModule, MatButtonToggleModule, MatFormFieldModule,
    MatInputModule, MatIconModule, FormsModule, DecimalPipe,
    MoneyPipe, PageHeaderComponent, ScrollTopComponent,
  ],
  template: `
    <app-page-header title="Clasificación" icon="leaderboard" description="Clasificación del campeonato con puntos, media y momentum. Filtra por las últimas N jornadas." />

    <!-- Controls -->
    <div class="controls">
      <mat-button-toggle-group [value]="windowMode()" (change)="setWindowMode($event.value)" hideSingleSelectionIndicator>
        <mat-button-toggle value="all">Todas</mat-button-toggle>
        <mat-button-toggle value="5">Últ. 5</mat-button-toggle>
        <mat-button-toggle value="10">Últ. 10</mat-button-toggle>
        <mat-button-toggle value="custom">Personalizado</mat-button-toggle>
      </mat-button-toggle-group>
      @if (windowMode() === 'custom') {
        <mat-form-field appearance="outline" class="window-field" subscriptSizing="dynamic">
          <mat-label>Jornadas</mat-label>
          <input matInput type="number" [(ngModel)]="customWindow" min="1" max="38" (keyup.enter)="loadData()">
        </mat-form-field>
        <button mat-icon-button color="primary" (click)="loadData()"><mat-icon>refresh</mat-icon></button>
      }
    </div>

    @if (loading()) {
      <div class="loading"><mat-spinner diameter="36" /> <span>Cargando clasificación...</span></div>
    } @else if (!dataSource.data.length) {
      <div class="empty">No hay datos de clasificación disponibles.</div>
    } @else {
      <p class="info">{{ includedMatchdays() }} jornadas incluidas</p>

      <!-- View toggle -->
      <div class="view-toggle">
        <mat-button-toggle-group [value]="viewMode()" (change)="setViewMode($event.value)" hideSingleSelectionIndicator>
          <mat-button-toggle value="cards"><mat-icon>grid_view</mat-icon></mat-button-toggle>
          <mat-button-toggle value="table"><mat-icon>table_rows</mat-icon></mat-button-toggle>
        </mat-button-toggle-group>
      </div>

      <!-- Table view -->
      @if (viewMode() === 'table') {
        <div class="table-container">
          <table mat-table [dataSource]="dataSource" matSort>
            <ng-container matColumnDef="rank">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>#</th>
              <td mat-cell *matCellDef="let t" class="rank-cell">{{ t.rank }}</td>
            </ng-container>
            <ng-container matColumnDef="team_name">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Equipo</th>
              <td mat-cell *matCellDef="let t"><strong>{{ t.team_name }}</strong></td>
            </ng-container>
            <ng-container matColumnDef="total_points">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Puntos</th>
              <td mat-cell *matCellDef="let t" class="points-cell">{{ t.total_points }}</td>
            </ng-container>
            <ng-container matColumnDef="average_points">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Media</th>
              <td mat-cell *matCellDef="let t">{{ t.average_points | number:'1.1-1' }}</td>
            </ng-container>
            <ng-container matColumnDef="matches_count">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>PJ</th>
              <td mat-cell *matCellDef="let t">{{ t.matches_count }}</td>
            </ng-container>
            <ng-container matColumnDef="max_points">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Máx</th>
              <td mat-cell *matCellDef="let t" class="max-cell">{{ t.max_points }}</td>
            </ng-container>
            <ng-container matColumnDef="min_points">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Mín</th>
              <td mat-cell *matCellDef="let t" class="min-cell">{{ t.min_points }}</td>
            </ng-container>
            <ng-container matColumnDef="momentum">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Momentum</th>
              <td mat-cell *matCellDef="let t" [class]="t.momentum > 0 ? 'momentum-up' : t.momentum < 0 ? 'momentum-down' : ''">
                @if (t.momentum !== 0) { {{ t.momentum > 0 ? '▲' : '▼' }} {{ t.momentum | number:'1.1-1' }} } @else { - }
              </td>
            </ng-container>
            <ng-container matColumnDef="trend">
              <th mat-header-cell *matHeaderCellDef mat-sort-header>Últ. J</th>
              <td mat-cell *matCellDef="let t" [class]="t.trend > 0 ? 'trend-up' : t.trend < 0 ? 'trend-down' : ''">
                @if (t.trend !== 0) { {{ t.trend > 0 ? '+' : '' }}{{ t.trend }} } @else { = }
              </td>
            </ng-container>
            <tr mat-header-row *matHeaderRowDef="columns"></tr>
            <tr mat-row *matRowDef="let row; columns: columns"></tr>
          </table>
        </div>
      }

      <!-- Cards view -->
      @if (viewMode() === 'cards') {
        <div class="cards-container">
          @for (t of dataSource.data; track t.team_name) {
            <article class="team-card" [class.podium]="t.rank <= 3">
              <div class="card-rank">#{{ t.rank }}</div>
              <div class="card-body">
                <h3 class="card-team-name">{{ t.team_name }}</h3>
                <div class="card-stats-grid">
                  <div class="card-stat">
                    <span class="card-stat-label">PUNTOS</span>
                    <span class="card-stat-val points-val">{{ t.total_points }}</span>
                  </div>
                  <div class="card-stat">
                    <span class="card-stat-label">MEDIA</span>
                    <span class="card-stat-val">{{ t.average_points | number:'1.1-1' }}</span>
                  </div>
                  <div class="card-stat">
                    <span class="card-stat-label">MÁX</span>
                    <span class="card-stat-val max-val">{{ t.max_points }}</span>
                  </div>
                  <div class="card-stat">
                    <span class="card-stat-label">MÍN</span>
                    <span class="card-stat-val min-val">{{ t.min_points }}</span>
                  </div>
                </div>
                <div class="card-bottom-row">
                  <span class="card-momentum" [class.up]="t.momentum > 0" [class.down]="t.momentum < 0">
                    @if (t.momentum !== 0) { {{ t.momentum > 0 ? '▲' : '▼' }} {{ t.momentum | number:'1.1-1' }} } @else { = }
                  </span>
                  <span class="card-trend" [class.up]="t.trend > 0" [class.down]="t.trend < 0">
                    Últ.J: @if (t.trend !== 0) { {{ t.trend > 0 ? '+' : '' }}{{ t.trend }} } @else { = }
                  </span>
                  <span class="card-pj">{{ t.matches_count }} PJ</span>
                </div>
              </div>
            </article>
          }
        </div>
        <app-scroll-top />
      }
    }
  `,
  styles: [`
    .controls { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
    .window-field { width: 100px; }
    .loading { display: flex; align-items: center; gap: 16px; padding: 60px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .empty { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); font-size: 1.1em; }
    .info { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin-bottom: 12px; }
    .view-toggle { display: flex; justify-content: flex-end; margin-bottom: 16px; }

    /* Table */
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .rank-cell { font-weight: 800; color: var(--mat-sys-primary); }
    .points-cell { font-weight: 700; }
    .max-cell { color: #2e7d32; }
    .min-cell { color: #d32f2f; }
    .momentum-up { color: #2e7d32; font-weight: 600; }
    .momentum-down { color: #d32f2f; font-weight: 600; }
    .trend-up { color: #2e7d32; font-weight: 600; }
    .trend-down { color: #d32f2f; font-weight: 600; }

    /* Cards */
    .cards-container { display: grid; grid-template-columns: 1fr; gap: 12px; }
    @media (min-width: 700px) { .cards-container { grid-template-columns: repeat(2, 1fr); } }
    @media (min-width: 1100px) { .cards-container { grid-template-columns: repeat(3, 1fr); } }

    .team-card {
      display: flex; align-items: flex-start; gap: 16px;
      padding: 16px 20px; border-radius: 16px;
      background: var(--mat-sys-surface-container);
      border: 1px solid var(--mat-sys-outline-variant);
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .team-card.podium { border-color: var(--mat-sys-primary); border-width: 2px; }
    :host-context(.dark-theme) .team-card { border-color: rgba(20, 255, 0, 0.15); }
    :host-context(.dark-theme) .team-card.podium { border-color: rgba(20, 255, 0, 0.4); }

    .card-rank { font-size: 1.8em; font-weight: 900; color: var(--mat-sys-primary); min-width: 40px; text-align: center; }
    .card-body { flex: 1; display: flex; flex-direction: column; gap: 10px; }
    .card-team-name { font-size: 1.1em; font-weight: 700; margin: 0; color: var(--mat-sys-on-surface); }

    .card-stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
    .card-stat { display: flex; flex-direction: column; gap: 2px; }
    .card-stat-label { font-size: 0.6em; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--mat-sys-on-surface-variant); }
    .card-stat-val { font-size: 1em; font-weight: 600; color: var(--mat-sys-on-surface); }
    .points-val { font-weight: 800; color: var(--mat-sys-primary); }
    .max-val { color: #2e7d32; }
    .min-val { color: #d32f2f; }

    .card-bottom-row { display: flex; gap: 12px; align-items: center; font-size: 0.85em; padding-top: 8px; border-top: 1px solid var(--mat-sys-outline-variant); }
    .card-momentum { font-weight: 600; }
    .card-momentum.up { color: #2e7d32; }
    .card-momentum.down { color: #d32f2f; }
    .card-trend { color: var(--mat-sys-on-surface-variant); }
    .card-trend.up { color: #2e7d32; }
    .card-trend.down { color: #d32f2f; }
    .card-pj { margin-left: auto; color: var(--mat-sys-on-surface-variant); }
  `]
})
export class ClassificationPageComponent {
  private svc = inject(AnalyticsService);
  private championshipService = inject(ChampionshipService);
  private breakpointObserver = inject(BreakpointObserver);

  isMobile = toSignal(
    this.breakpointObserver.observe([Breakpoints.Handset]).pipe(map(r => r.matches)),
    { initialValue: false }
  );

  loading = signal(true);
  windowMode = signal<string>('all');
  customWindow = 5;
  includedMatchdays = signal('');
  viewMode = signal<'cards' | 'table'>(
    (localStorage.getItem('futmondo_view_classification') as 'cards' | 'table') || 'table'
  );

  dataSource = new MatTableDataSource<ClassificationEntry>([]);
  columns = ['rank', 'team_name', 'total_points', 'average_points', 'matches_count', 'max_points', 'min_points', 'momentum', 'trend'];

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  constructor() {
    if (this.isMobile() && !localStorage.getItem('futmondo_view_classification')) {
      this.viewMode.set('cards');
    }
    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadData();
    });
  }

  setWindowMode(value: string) {
    this.windowMode.set(value);
    if (value !== 'custom') {
      this.loadData();
    }
  }

  setViewMode(mode: 'cards' | 'table') {
    this.viewMode.set(mode);
    localStorage.setItem('futmondo_view_classification', mode);
  }

  async loadData() {
    this.loading.set(true);
    try {
      const mode = this.windowMode();
      const window = mode === 'all' ? undefined : mode === 'custom' ? this.customWindow : parseInt(mode, 10);

      const data = await this.svc.getClassificationFull(window, this.championshipService.activeId());
      const teams: any[] = data?.classification || [];

      const entries: ClassificationEntry[] = teams.map((t: any, idx: number) => ({
        rank: t.rank || idx + 1,
        team_name: t.team_name || t.team_id,
        total_points: t.total_points || t.points || 0,
        average_points: t.average_points || t.average || 0,
        matches_count: t.matches_count || 0,
        max_points: t.max_points || 0,
        min_points: t.min_points || 0,
        trend: t.trend || 0,
        momentum: t.momentum || 0,
      }));

      this.dataSource.data = entries;
      this.includedMatchdays.set(
        data?.included_matchdays?.length
          ? `${data.included_matchdays.length}`
          : entries[0]?.matches_count ? `${entries[0].matches_count}` : ''
      );
    } catch { this.dataSource.data = []; }
    finally { this.loading.set(false); }
  }
}
