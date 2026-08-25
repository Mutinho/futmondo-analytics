import { Component, inject, signal, effect, ViewChild } from '@angular/core';
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
    MoneyPipe, PageHeaderComponent,
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
      <div class="table-container">
        <table mat-table [dataSource]="dataSource" matSort>
          <!-- Rank -->
          <ng-container matColumnDef="rank">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>#</th>
            <td mat-cell *matCellDef="let t" class="rank-cell">{{ t.rank }}</td>
          </ng-container>

          <!-- Team -->
          <ng-container matColumnDef="team_name">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Equipo</th>
            <td mat-cell *matCellDef="let t"><strong>{{ t.team_name }}</strong></td>
          </ng-container>

          <!-- Points -->
          <ng-container matColumnDef="total_points">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Puntos</th>
            <td mat-cell *matCellDef="let t" class="points-cell">{{ t.total_points }}</td>
          </ng-container>

          <!-- Average -->
          <ng-container matColumnDef="average_points">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Media</th>
            <td mat-cell *matCellDef="let t">{{ t.average_points | number:'1.1-1' }}</td>
          </ng-container>

          <!-- Matches -->
          <ng-container matColumnDef="matches_count">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>PJ</th>
            <td mat-cell *matCellDef="let t">{{ t.matches_count }}</td>
          </ng-container>

          <!-- Max -->
          <ng-container matColumnDef="max_points">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Máx</th>
            <td mat-cell *matCellDef="let t" class="max-cell">{{ t.max_points }}</td>
          </ng-container>

          <!-- Min -->
          <ng-container matColumnDef="min_points">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Mín</th>
            <td mat-cell *matCellDef="let t" class="min-cell">{{ t.min_points }}</td>
          </ng-container>

          <!-- Momentum -->
          <ng-container matColumnDef="momentum">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Momentum</th>
            <td mat-cell *matCellDef="let t" [class]="t.momentum > 0 ? 'momentum-up' : t.momentum < 0 ? 'momentum-down' : ''">
              @if (t.momentum !== 0) { {{ t.momentum > 0 ? '▲' : '▼' }} {{ t.momentum | number:'1.1-1' }} } @else { - }
            </td>
          </ng-container>

          <!-- Trend (last matchday diff) -->
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
  `,
  styles: [`
    .controls { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
    .window-field { width: 100px; }
    .loading { display: flex; align-items: center; gap: 16px; padding: 60px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .empty { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); font-size: 1.1em; }
    .info { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin-bottom: 12px; }
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
  `]
})
export class ClassificationPageComponent {
  private svc = inject(AnalyticsService);
  private championshipService = inject(ChampionshipService);

  loading = signal(true);
  windowMode = signal<string>('all');
  customWindow = 5;
  includedMatchdays = signal('');

  dataSource = new MatTableDataSource<ClassificationEntry>([]);
  columns = ['rank', 'team_name', 'total_points', 'average_points', 'matches_count', 'max_points', 'min_points', 'momentum', 'trend'];

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  constructor() {
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

  async loadData() {
    this.loading.set(true);
    try {
      const mode = this.windowMode();
      const window = mode === 'all' ? undefined : mode === 'custom' ? this.customWindow : parseInt(mode, 10);

      // Single combined endpoint — classification + momentum
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
