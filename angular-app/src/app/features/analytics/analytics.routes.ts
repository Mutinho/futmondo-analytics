import { Routes } from '@angular/router';
import { AnalyticsShellComponent } from './analytics-shell.component';

export const analyticsRoutes: Routes = [
  {
    path: '',
    component: AnalyticsShellComponent,
    children: [
      { path: '', redirectTo: 'overview', pathMatch: 'full' },
      { path: 'overview', loadComponent: () => import('./overview/overview.component').then(m => m.OverviewComponent) },
      { path: 'classification', loadComponent: () => import('./classification/classification.component').then(m => m.ClassificationComponent) },
      { path: 'players', loadComponent: () => import('./players/players.component').then(m => m.PlayersComponent) },
      { path: 'market', loadComponent: () => import('./market/market.component').then(m => m.MarketComponent) },
      { path: 'opportunities', loadComponent: () => import('./opportunities/opportunities.component').then(m => m.OpportunitiesComponent) },
      { path: 'projections', loadComponent: () => import('./projections/projections.component').then(m => m.ProjectionsComponent) },
    ],
  },
];

export default analyticsRoutes;
