import { Component, inject, signal, effect, ViewChild, computed } from '@angular/core';
import { Router } from '@angular/router';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';
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
    MatIconModule,
    MatProgressSpinnerModule,
    MoneyPipe,
  ],
  templateUrl: './budget-overview.component.html',
  styleUrl: './budget-overview.component.scss',
})
export class BudgetOverviewComponent {
  private budgetService = inject(BudgetService);
  private championshipService = inject(ChampionshipService);
  private router = inject(Router);

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
