import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { DatePipe } from '@angular/common';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';
import { BudgetService } from '../../../core/services/budget.service';
import { TeamDetailResponse, Transaction } from '../../../core/models/budget.model';

@Component({
  selector: 'app-budget-detail',
  standalone: true,
  imports: [
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    DatePipe,
    MoneyPipe,
  ],
  templateUrl: './budget-detail.component.html',
  styleUrl: './budget-detail.component.scss',
})
export class BudgetDetailComponent {
  private budgetService = inject(BudgetService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  detail = signal<TeamDetailResponse | null>(null);
  loading = signal(true);
  error = signal('');

  purchaseColumns = ['player_name', 'price', 'from', 'date'];
  saleColumns = ['player_name', 'price', 'to', 'date'];

  constructor() {
    const teamId = this.route.snapshot.paramMap.get('teamId');
    if (teamId) {
      this.loadDetail(teamId);
    }
  }

  async loadDetail(teamId: string) {
    this.loading.set(true);
    this.error.set('');
    try {
      const data = await this.budgetService.getTeamDetail(teamId);
      this.detail.set(data);
    } catch (err: any) {
      this.error.set(err.message || 'Error cargando detalle');
    } finally {
      this.loading.set(false);
    }
  }

  goBack() {
    this.router.navigate(['/budget']);
  }

  getBalanceClass(): string {
    const d = this.detail();
    if (!d) return '';
    if (d.balance >= d.initial_budget) return 'money-positive';
    if (d.balance >= d.initial_budget * 0.5) return 'money-neutral';
    return 'money-negative';
  }
}
