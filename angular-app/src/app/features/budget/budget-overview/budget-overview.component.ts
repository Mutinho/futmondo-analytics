import { Component, inject, signal, effect, ViewChild, computed } from '@angular/core';
import { Router } from '@angular/router';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';
import { ScrollTopComponent } from '../../../shared/components/scroll-top.component';
import { BudgetService } from '../../../core/services/budget.service';
import { ChampionshipService } from '../../../core/services/championship.service';
import { TeamBudget } from '../../../core/models/budget.model';

@Component({
  selector: 'app-budget-overview',
  standalone: true,
  imports: [
    MatTableModule,
    MatSortModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatFormFieldModule,
    MatSelectModule,
    MoneyPipe,
    ScrollTopComponent,
  ],
  templateUrl: './budget-overview.component.html',
  styleUrl: './budget-overview.component.scss',
})
export class BudgetOverviewComponent {
  private budgetService = inject(BudgetService);
  private championshipService = inject(ChampionshipService);
  private router = inject(Router);
  private breakpointObserver = inject(BreakpointObserver);

  isMobile = toSignal(
    this.breakpointObserver.observe([Breakpoints.Handset]).pipe(map(r => r.matches)),
    { initialValue: false }
  );

  viewMode = signal<'cards' | 'table'>(
    (localStorage.getItem('futmondo_view_budget') as 'cards' | 'table') || 'table'
  );
  sortField = signal<string>('balance');

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) {
      this.dataSource.sort = sort;
    }
  }

  dataSource = new MatTableDataSource<TeamBudget>([]);
  loading = signal(true);
  error = signal('');

  displayedColumns = ['team_name', 'balance', 'team_value', 'total_spent', 'total_income', 'ops', 'performance', 'max_bid'];

  championshipBudget = computed(() => {
    const budget = this.championshipService.activeChampionship()?.initial_budget || 200000000;
    return `${Math.round(budget / 1000000)}M`;
  });

  constructor() {
    if (this.isMobile() && !localStorage.getItem('futmondo_view_budget')) this.viewMode.set('cards');

    this.dataSource.sortingDataAccessor = (item: TeamBudget, property: string) => {
      if (property === 'ops') return item.purchases_count + item.sales_count;
      return (item as any)[property];
    };

    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadData();
    });
  }

  async loadData() {
    this.loading.set(true);
    this.error.set('');
    try {
      const data = await this.budgetService.getBalances(this.championshipService.activeId());
      this.dataSource.data = data.teams;
    } catch (err: any) {
      this.error.set(err.message || 'Error cargando datos');
    } finally {
      this.loading.set(false);
    }
  }

  setViewMode(mode: 'cards' | 'table') {
    this.viewMode.set(mode);
    localStorage.setItem('futmondo_view_budget', mode);
  }

  onSortChange(event: Event) {
    this.sortField.set((event.target as HTMLSelectElement).value);
    this.sortCards();
  }

  onMatSortChange(value: string) {
    this.sortField.set(value);
    this.sortCards();
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

  openDetail(team: TeamBudget) {
    this.router.navigate(['/budget', team.team_id]);
  }

  getBalanceClass(balance: number): string {
    return balance >= 0 ? 'money-positive' : 'money-negative';
  }

  getPerformanceClass(value: number): string {
    return value >= 0 ? 'money-positive' : 'money-negative';
  }
}
