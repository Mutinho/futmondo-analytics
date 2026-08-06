import { Component, signal, inject, computed, effect } from '@angular/core';
import { Router, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDialog } from '@angular/material/dialog';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { ChampionshipService, Championship } from './core/services/championship.service';
import { AuthService } from './core/services/auth.service';
import { SyncDialogComponent } from './features/budget/sync-dialog/sync-dialog.component';

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
  private dialog = inject(MatDialog);
  private http = inject(HttpClient);
  private router = inject(Router);
  private authService = inject(AuthService);
  championshipService = inject(ChampionshipService);

  sidenavOpened = signal(true);

  /** True when on login/splash — hides the app shell */
  isLoginPage = signal(true);

  isMobile = toSignal(
    this.breakpointObserver.observe([Breakpoints.Handset]).pipe(map(result => result.matches)),
    { initialValue: false }
  );

  allNavItems: NavItem[] = [
    { label: 'Presupuesto', icon: 'account_balance_wallet', route: '/budget' },
    { label: 'Mercado', icon: 'shopping_cart', route: '/market' },
    { label: 'Evolución', icon: 'trending_up', route: '/evolution' },
    { label: 'Estadísticas', icon: 'bar_chart', route: '/stats' },
    { label: 'Finanzas', icon: 'payments', route: '/finances' },
    { label: 'Clausulables', icon: 'sports_soccer', route: '/clausulable', requiresClauses: true },
    { label: 'Analytics', icon: 'analytics', route: '/analytics' },
    { label: 'Ajustes', icon: 'settings', route: '/settings' },
  ];

  navItems = computed(() => {
    const hasClauses = this.championshipService.hasClauses();
    return this.allNavItems.filter(item => !item.requiresClauses || hasClauses);
  });

  constructor() {
    this.championshipService.load();
    this.loadTheme();
    this.loadLastSync();

    // Track route to hide shell on login/splash pages — also reset body bg
    this.router.events.subscribe(() => {
      const url = this.router.url;
      const hideShell = url === '/login' || url === '/';
      this.isLoginPage.set(hideShell);
      if (!hideShell) {
        document.body.removeAttribute('style');
      }
    });

    // Recargar lastSync al cambiar de campeonato
    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadLastSync();
    });
  }

  // Last sync
  lastSync = signal('');

  private async loadLastSync() {
    const id = this.championshipService.activeId();
    if (!id) return;
    try {
      const resp = await firstValueFrom(this.http.get<any>(`/api/v1/sync/last-sync?championship_id=${id}`));
      if (resp.last_sync) {
        const date = new Date(resp.last_sync);
        this.lastSync.set(date.toLocaleString('es-ES', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' }));
      } else {
        this.lastSync.set('');
      }
    } catch {
      this.lastSync.set('');
    }
  }

  // Dark mode
  darkMode = signal(false);

  toggleDarkMode() {
    this.darkMode.update(v => !v);
    this.applyTheme();
    localStorage.setItem('futmondo_dark_mode', this.darkMode() ? 'dark' : 'light');
  }

  private loadTheme() {
    const saved = localStorage.getItem('futmondo_dark_mode');
    if (saved === 'dark') {
      this.darkMode.set(true);
    } else if (saved === 'light') {
      this.darkMode.set(false);
    } else {
      // Usar preferencia del sistema
      this.darkMode.set(window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
    this.applyTheme();
  }

  private applyTheme() {
    const body = document.body;
    const html = document.documentElement;
    if (this.darkMode()) {
      body.classList.add('dark-theme');
      html.style.colorScheme = 'dark';
      body.style.colorScheme = 'dark';
    } else {
      body.classList.remove('dark-theme');
      html.style.colorScheme = 'light';
      body.style.colorScheme = 'light';
    }
  }

  onChampionshipChange(championship: Championship) {
    this.championshipService.setActive(championship);
  }

  toggleSidenav() {
    this.sidenavOpened.update(v => !v);
  }

  sync() {
    const dialogRef = this.dialog.open(SyncDialogComponent, {
      width: '500px',
      disableClose: false,
    });
    dialogRef.afterClosed().subscribe(() => {
      this.loadLastSync();
    });
  }

  logout() {
    this.authService.logout();
  }
}
