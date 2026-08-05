import { Component, signal, inject, computed } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { ChampionshipService, Championship } from './core/services/championship.service';

interface NavItem {
  label: string;
  icon: string;
  route: string;
  requiresClauses?: boolean;
}

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  private breakpointObserver = inject(BreakpointObserver);
  championshipService = inject(ChampionshipService);

  sidenavOpened = signal(true);

  isMobile = toSignal(
    this.breakpointObserver.observe([Breakpoints.Handset]).pipe(map(result => result.matches)),
    { initialValue: false }
  );

  allNavItems: NavItem[] = [
    { label: 'Presupuesto', icon: 'account_balance_wallet', route: '/budget' },
    { label: 'Evolución', icon: 'trending_up', route: '/evolution' },
    { label: 'Estadísticas', icon: 'bar_chart', route: '/stats' },
    { label: 'Finanzas', icon: 'payments', route: '/finances' },
    { label: 'Clausulables', icon: 'sports_soccer', route: '/clausulable', requiresClauses: true },
    { label: 'Analytics', icon: 'analytics', route: '/analytics' },
  ];

  navItems = computed(() => {
    const hasClauses = this.championshipService.hasClauses();
    return this.allNavItems.filter(item => !item.requiresClauses || hasClauses);
  });

  constructor() {
    this.championshipService.load();
  }

  onChampionshipChange(championship: Championship) {
    this.championshipService.setActive(championship);
  }

  toggleSidenav() {
    this.sidenavOpened.update(v => !v);
  }
}
