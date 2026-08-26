import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/splash/splash.component').then(m => m.SplashComponent),
    pathMatch: 'full',
  },
  {
    path: 'login',
    loadComponent: () => import('./features/login/login.component').then(m => m.LoginComponent),
  },
  {
    path: 'budget',
    canActivate: [authGuard],
    loadChildren: () => import('./features/budget/budget.routes'),
  },
  {
    path: 'evolution',
    canActivate: [authGuard],
    loadComponent: () => import('./features/evolution/evolution.component').then(m => m.EvolutionComponent),
  },
  {
    path: 'stats',
    canActivate: [authGuard],
    loadComponent: () => import('./features/stats/stats.component').then(m => m.StatsComponent),
  },
  {
    path: 'finances',
    canActivate: [authGuard],
    loadComponent: () => import('./features/finances/finances.component').then(m => m.FinancesComponent),
  },
  {
    path: 'clausulable',
    canActivate: [authGuard],
    loadComponent: () => import('./features/clausulable/clausulable.component').then(m => m.ClausulableComponent),
  },
  {
    path: 'market',
    canActivate: [authGuard],
    loadComponent: () => import('./features/market/market.component').then(m => m.MarketComponent),
  },
  {
    path: 'favorites',
    canActivate: [authGuard],
    loadComponent: () => import('./features/favorites/favorites.component').then(m => m.FavoritesComponent),
  },
  {
    path: 'transactions',
    canActivate: [authGuard],
    loadComponent: () => import('./features/transactions/transactions.component').then(m => m.TransactionsComponent),
  },
  {
    path: 'my-roster',
    canActivate: [authGuard],
    loadComponent: () => import('./features/my-roster/my-roster.component').then(m => m.MyRosterComponent),
  },
  {
    path: 'calculator',
    canActivate: [authGuard],
    loadComponent: () => import('./features/calculator/calculator.component').then(m => m.CalculatorComponent),
  },
  {
    path: 'free-agents',
    canActivate: [authGuard],
    loadComponent: () => import('./features/analytics/market/market.component').then(m => m.MarketComponent),
  },
  {
    path: 'classification',
    canActivate: [authGuard],
    loadComponent: () => import('./features/classification/classification.component').then(m => m.ClassificationPageComponent),
  },
  {
    path: 'settings',
    canActivate: [authGuard],
    loadComponent: () => import('./features/settings/championships-config.component').then(m => m.ChampionshipsConfigComponent),
  },
  { path: '**', redirectTo: '/budget' },
];
