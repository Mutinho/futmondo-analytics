import { Component, ChangeDetectionStrategy, inject, signal, computed, effect, ViewChild } from '@angular/core';
import { injectIsMobile } from '../../shared/utils/responsive';
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
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    MatProgressSpinnerModule, MatTableModule, MatSortModule,
    MatButtonModule, MatButtonToggleModule, MatFormFieldModule,
    MatInputModule, MatIconModule, FormsModule, DecimalPipe,
    PageHeaderComponent, ScrollTopComponent,
  ],
  templateUrl: './classification.component.html',
  styleUrl: './classification.component.scss'
})
export class ClassificationPageComponent {
  private svc = inject(AnalyticsService);
  private championshipService = inject(ChampionshipService);

  isMobile = injectIsMobile();

  loading = signal(true);
  error = signal<string | null>(null);
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
    this.error.set(null);
    try {
      const mode = this.windowMode();
      const window = mode === 'all' ? undefined : mode === 'custom' ? this.customWindow : parseInt(mode, 10);

      const data = await this.svc.getClassificationFull(window, this.championshipService.activeId());
      const teams = data.classification;

      const entries: ClassificationEntry[] = teams.map((t, idx) => ({
        rank: t.rank || idx + 1,
        team_name: t.team_name || t.team_id,
        total_points: t.total_points,
        average_points: t.average_points,
        matches_count: t.matches_count || 0,
        max_points: t.max_points || 0,
        min_points: t.min_points || 0,
        trend: t.trend || 0,
        momentum: t.momentum || 0,
      }));

      this.dataSource.data = entries;
      this.includedMatchdays.set(
        data.included_matchdays.length
          ? `${data.included_matchdays.length}`
          : entries[0]?.matches_count ? `${entries[0].matches_count}` : ''
      );
    } catch (e: any) {
      this.error.set('Error al cargar la clasificación.');
      this.dataSource.data = [];
    }
    finally { this.loading.set(false); }
  }
}
