import { Component, ChangeDetectionStrategy, inject, signal, effect } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule, MAT_DATE_LOCALE, DateAdapter, MAT_DATE_FORMATS } from '@angular/material/core';
import { SpanishDateAdapter, ES_DATE_FORMATS } from '../../shared/utils/spanish-date-adapter';
import { getPlayerPhoto, getPositionKey, getPositionLabel } from '../../shared/utils/player.utils';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { StarterCardBadgeComponent } from '../../shared/components/starter-card-badge.component';
import { ScrollTopComponent } from '../../shared/components/scroll-top.component';
import { ChampionshipService } from '../../core/services/championship.service';
import { PageHeaderComponent } from '../../shared/components/page-header.component';

interface Transaction {
  transaction_id: number;
  player_id: string;
  player_name: string;
  player_slug: string;
  player_role: string;
  player_role2: string;
  real_team_name: string;
  real_team_logo: string;
  price: number;
  market_value: number | null;
  overpay_pct: number | null;
  team_id: string;
  team_name: string;
  seller_name?: string;
  buyer_name?: string;
  sofascore_rating: number | null;
  sofascore_url: string | null;
  starter_pct: number | null;
  bids: { name: string; bid: number }[];
  // Sale-specific
  original_buy_price?: number | null;
  sale_profit?: number | null;
  sale_vs_market_pct?: number | null;
}

interface DateGroup {
  date: string;
  purchases: Transaction[];
  sales: Transaction[];
}

interface Team {
  team_id: string;
  team_name: string;
}

@Component({
  selector: 'app-transactions',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    FormsModule, MatProgressSpinnerModule, MatSelectModule,
    MatFormFieldModule, MatInputModule, MatIconModule, MatButtonModule,
    MatDatepickerModule, MatNativeDateModule, MoneyPipe, ScrollTopComponent, StarterCardBadgeComponent, PageHeaderComponent
  ],
  providers: [
    { provide: MAT_DATE_LOCALE, useValue: 'es-ES' },
    { provide: DateAdapter, useClass: SpanishDateAdapter },
    { provide: MAT_DATE_FORMATS, useValue: ES_DATE_FORMATS },
  ],

  templateUrl: './transactions.component.html',
  styleUrl: './transactions.component.scss'
})
export class TransactionsComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);

  loading = signal(true);
  error = signal('');
  groups = signal<DateGroup[]>([]);
  teams = signal<Team[]>([]);
  totalTransactions = signal(0);

  filtersOpen = false;
  filterTeam = '';
  dateFrom: Date | null = null;
  dateTo: Date | null = null;
  openDates = new Set<string>();

  constructor() {
    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadData();
    });
  }

  onDateChange() {
    this.loadData();
  }

  async loadData() {
    this.loading.set(true);
    this.error.set('');
    try {
      let params = new HttpParams().set('championship_id', this.championshipService.activeId());
      if (this.filterTeam) params = params.set('team_id', this.filterTeam);
      if (this.dateFrom) params = params.set('date_from', this.formatDateISO(this.dateFrom));
      if (this.dateTo) params = params.set('date_to', this.formatDateISO(this.dateTo));

      const data = await firstValueFrom(this.http.get<any>('/api/v1/transactions/history', { params }));
      this.groups.set(data.groups || []);
      this.teams.set(data.teams || []);
      this.totalTransactions.set(data.total_transactions || 0);
      // Open all dates by default
      this.openDates = new Set((data.groups || []).map((g: DateGroup) => g.date));
    } catch (err: any) {
      this.error.set(err?.error?.detail || err.message || 'Error cargando transacciones');
    } finally {
      this.loading.set(false);
    }
  }

  clearFilters() {
    this.filterTeam = '';
    this.dateFrom = null;
    this.dateTo = null;
    this.loadData();
  }

  toggleDate(date: string) {
    if (this.openDates.has(date)) {
      this.openDates.delete(date);
    } else {
      this.openDates.add(date);
    }
  }

  isDateOpen(date: string): boolean {
    return this.openDates.has(date);
  }

  formatDate(dateStr: string): string {
    try {
      const d = new Date(dateStr + 'T00:00:00');
      return d.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
    } catch {
      return dateStr;
    }
  }

  private formatDateISO(date: Date): string {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  // Shared utils as class properties for template access
  getPlayerPhoto = getPlayerPhoto;
  getPositionKey = getPositionKey;
  getPositionLabel = getPositionLabel;

  getTeamLogo(teamName: string): string {
    const slug = (teamName || '').toLowerCase().replace(/ /g, '-').replace(/á/g,'a').replace(/é/g,'e').replace(/í/g,'i').replace(/ó/g,'o').replace(/ú/g,'u').replace(/ñ/g,'n');
    return `https://static02.mondocore.com/futmondo/img/teams/64/${slug}.png`;
  }
}
