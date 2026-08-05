import { Component, inject, computed } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatTabsModule } from '@angular/material/tabs';
import { ChampionshipService } from '../../core/services/championship.service';

@Component({
  selector: 'app-analytics-shell',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, MatTabsModule],
  template: `
    <h1>📊 Analytics Avanzado</h1>
    <nav mat-tab-nav-bar [tabPanel]="tabPanel">
      @for (tab of visibleTabs(); track tab.route) {
        <a mat-tab-link
           [routerLink]="tab.route"
           routerLinkActive #rla="routerLinkActive"
           [active]="rla.isActive">
          {{ tab.icon }} {{ tab.label }}
        </a>
      }
    </nav>
    <mat-tab-nav-panel #tabPanel>
      <div class="tab-content">
        <router-outlet />
      </div>
    </mat-tab-nav-panel>
  `,
  styles: [`
    h1 { margin-bottom: 16px; }
    .tab-content { padding: 20px 0; }
  `]
})
export class AnalyticsShellComponent {
  private championshipService = inject(ChampionshipService);

  allTabs = [
    { label: 'General', icon: '🌐', route: 'overview', requiresClauses: false },
    { label: 'Clasificación', icon: '🏆', route: 'classification', requiresClauses: false },
    { label: 'Jugadores', icon: '🔥', route: 'players', requiresClauses: false },
    { label: 'Mercado', icon: '💹', route: 'market', requiresClauses: false },
    { label: 'Oportunidades', icon: '⚡', route: 'opportunities', requiresClauses: false },
    { label: 'Proyecciones', icon: '🎯', route: 'projections', requiresClauses: false },
  ];

  visibleTabs = computed(() => {
    const hasClauses = this.championshipService.hasClauses();
    return this.allTabs.filter(t => !t.requiresClauses || hasClauses);
  });
}
