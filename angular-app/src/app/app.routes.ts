import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'budget', pathMatch: 'full' },
  {
    path: 'budget',
    loadChildren: () => import('./features/budget/budget.routes'),
  },
  {
    path: 'evolution',
    loadComponent: () => import('./features/evolution/evolution.component').then(m => m.EvolutionComponent),
  },
  {
    path: 'stats',
    loadComponent: () => import('./features/stats/stats.component').then(m => m.StatsComponent),
  },
  {
    path: 'finances',
    loadComponent: () => import('./features/finances/finances.component').then(m => m.FinancesComponent),
  },
  {
    path: 'clausulable',
    loadComponent: () => import('./features/clausulable/clausulable.component').then(m => m.ClausulableComponent),
  },
  {
    path: 'analytics',
    loadChildren: () => import('./features/analytics/analytics.routes'),
  },
];
