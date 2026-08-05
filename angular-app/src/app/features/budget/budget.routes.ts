import { Routes } from '@angular/router';

export const budgetRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./budget-overview/budget-overview.component').then(m => m.BudgetOverviewComponent),
  },
  {
    path: ':teamId',
    loadComponent: () => import('./budget-detail/budget-detail.component').then(m => m.BudgetDetailComponent),
  },
];

export default budgetRoutes;
