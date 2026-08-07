import { Component, inject, signal, effect } from '@angular/core';
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
import { MatNativeDateModule, MAT_DATE_LOCALE, DateAdapter, MAT_DATE_FORMATS, NativeDateAdapter } from '@angular/material/core';
import { MoneyPipe } from '../../shared/pipes/money.pipe';

const ES_DATE_FORMATS = {
  parse: { dateInput: 'dd/MM/yyyy' },
  display: {
    dateInput: { day: '2-digit', month: '2-digit', year: 'numeric' } as Intl.DateTimeFormatOptions,
    monthYearLabel: { year: 'numeric', month: 'short' } as Intl.DateTimeFormatOptions,
    dateA11yLabel: { year: 'numeric', month: 'long', day: 'numeric' } as Intl.DateTimeFormatOptions,
    monthYearA11yLabel: { year: 'numeric', month: 'long' } as Intl.DateTimeFormatOptions,
  },
};

class SpanishDateAdapter extends NativeDateAdapter {
  override format(date: Date, displayFormat: Object): string {
    if (displayFormat === ES_DATE_FORMATS.display.dateInput) {
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
    }
    return super.format(date, displayFormat);
  }
}
import { ChampionshipService } from '../../core/services/championship.service';

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
  imports: [
    FormsModule, MatProgressSpinnerModule, MatSelectModule,
    MatFormFieldModule, MatInputModule, MatIconModule, MatButtonModule,
    MatDatepickerModule, MatNativeDateModule, MoneyPipe
  ],
  providers: [
    { provide: MAT_DATE_LOCALE, useValue: 'es-ES' },
    { provide: DateAdapter, useClass: SpanishDateAdapter },
    { provide: MAT_DATE_FORMATS, useValue: ES_DATE_FORMATS },
  ],

  template: `
    <h1>📋 Transacciones</h1>
    <p class="description">Historial de compras y ventas del campeonato.</p>

    <!-- Filters -->
    <div class="filters-toggle" (click)="filtersOpen = !filtersOpen">
      <mat-icon>filter_list</mat-icon>
      <span>Filtros</span>
      <mat-icon class="toggle-arrow">{{ filtersOpen ? 'expand_less' : 'expand_more' }}</mat-icon>
    </div>
    @if (filtersOpen) {
      <div class="filters">
        <mat-form-field appearance="outline" class="filter-team" subscriptSizing="dynamic">
          <mat-label>Equipo</mat-label>
          <mat-select [(ngModel)]="filterTeam" (selectionChange)="loadData()">
            <mat-option value="">Todos</mat-option>
            @for (t of teams(); track t.team_id) {
              <mat-option [value]="t.team_id">{{ t.team_name }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
        <div class="filter-dates">
          <mat-form-field appearance="outline" class="filter-date" subscriptSizing="dynamic">
            <mat-label>Desde</mat-label>
            <input matInput [matDatepicker]="pickerFrom" [(ngModel)]="dateFrom" (dateChange)="onDateChange()" (focus)="pickerFrom.open()" readonly />
            <mat-datepicker-toggle matIconSuffix [for]="pickerFrom"></mat-datepicker-toggle>
            <mat-datepicker #pickerFrom></mat-datepicker>
          </mat-form-field>
          <mat-form-field appearance="outline" class="filter-date" subscriptSizing="dynamic">
            <mat-label>Hasta</mat-label>
            <input matInput [matDatepicker]="pickerTo" [(ngModel)]="dateTo" (dateChange)="onDateChange()" (focus)="pickerTo.open()" readonly />
            <mat-datepicker-toggle matIconSuffix [for]="pickerTo"></mat-datepicker-toggle>
            <mat-datepicker #pickerTo></mat-datepicker>
          </mat-form-field>
        </div>
        @if (filterTeam || dateFrom || dateTo) {
          <button mat-icon-button (click)="clearFilters()" title="Limpiar filtros" class="clear-btn desktop-only">
            <mat-icon>clear</mat-icon>
          </button>
          <button mat-flat-button color="primary" (click)="clearFilters()" class="clear-btn-mobile mobile-only">
            <mat-icon>clear</mat-icon>
            Limpiar filtros
          </button>
        }
      </div>
    }

    @if (loading()) {
      <div class="loading"><mat-spinner diameter="40" /> <span>Cargando transacciones...</span></div>
    } @else if (error()) {
      <div class="error-message">{{ error() }}</div>
    } @else if (!groups().length) {
      <div class="empty">📋 No hay transacciones para los filtros seleccionados.</div>
    } @else {
      <p class="count">{{ totalTransactions() }} transacciones</p>

      @for (group of groups(); track group.date) {
        <div class="date-block">
          <div class="date-header">📅 {{ formatDate(group.date) }}</div>
          <div class="date-content">
            <!-- Purchases -->
            <div class="txn-column">
              <h4 class="col-title purchases">🟢 Compras ({{ group.purchases.length }})</h4>
              @for (t of group.purchases; track t.transaction_id) {
                <div class="txn-card">
                  <div class="txn-header">
                    <img [src]="getPlayerPhoto(t.player_slug)" class="txn-photo" [alt]="t.player_name" loading="lazy"
                         (error)="$event.target.style.display='none'" />
                    <div class="txn-info">
                      <div class="txn-name-row">
                        <strong class="txn-player-name">{{ t.player_name }}</strong>
                        <span class="pos-chip" [class]="'pos-' + getPositionKey(t.player_role)">{{ getPositionLabel(t.player_role) }}</span>
                        @if (t.player_role2) {
                          <span class="pos-chip pos-secondary" [class]="'pos-' + getPositionKey(t.player_role2)">{{ getPositionLabel(t.player_role2) }}</span>
                        }
                      </div>
                      <div class="txn-team-row">
                        @if (t.real_team_logo) {
                          <img [src]="'https://static02.mondocore.com/futmondo/img/teams/64/' + t.real_team_logo" class="txn-team-logo" loading="lazy" (error)="$event.target.style.display='none'" />
                        }
                        <span>{{ t.real_team_name }}</span>
                      </div>
                    </div>
                    <div class="txn-right">
                      <strong class="txn-buyer-name">{{ t.team_name }}</strong>
                      @if (t.seller_name !== 'Mercado') {
                        <span class="txn-from">← {{ t.seller_name }}</span>
                      }
                    </div>
                  </div>
                  <div class="txn-price-block">
                    <div class="txn-price-main">
                      <span class="txn-price-label">Pagado</span>
                      <span class="txn-price-value">{{ t.price | money }}</span>
                    </div>
                    @if (t.market_value) {
                      <div class="txn-price-secondary">
                        <span class="txn-price-label">Valor mercado</span>
                        <span class="txn-price-value">{{ t.market_value | money }}</span>
                      </div>
                    }
                    @if (t.overpay_pct != null && t.market_value && t.overpay_pct > 0) {
                      <div class="txn-price-overpay">
                        <span class="txn-price-label">Sobrepago</span>
                        <span class="txn-price-value" [class]="t.overpay_pct > 20 ? 'overpay-extreme' : t.overpay_pct > 10 ? 'overpay-high' : 'overpay-mild'">
                          +{{ t.overpay_pct }}% ({{ t.price - t.market_value | money }})
                        </span>
                      </div>
                    }
                  </div>
                  <div class="txn-badges-row">
                    @if (t.sofascore_rating != null) {
                      <span class="badge-item"><span class="badge-label">Sofa</span><span class="badge-val">{{ t.sofascore_rating.toFixed(1) }}</span></span>
                    }
                    @if (t.starter_pct != null) {
                      <span class="badge-item"><span class="badge-label">Tit</span><span class="badge-val">{{ t.starter_pct }}%</span></span>
                    }
                    @if (t.bids && t.bids.length) {
                      <span class="badge-item badge-bids">{{ t.bids.length }} puja{{ t.bids.length > 1 ? 's' : '' }}</span>
                    }
                  </div>
                  @if (t.bids && t.bids.length) {
                    <div class="txn-bids">
                      <span class="txn-bids-title">🏷️ Otras pujas</span>
                      <div class="txn-bids-list">
                        @for (b of t.bids; track b.name) {
                          <div class="txn-bid-item">
                            <span class="txn-bid-name">{{ b.name }}</span>
                            <span class="txn-bid-amount">
                              {{ b.bid | money }}
                              @if (t.market_value && t.market_value > 0) {
                                <span class="txn-bid-overpay">(+{{ (((b.bid - t.market_value) / t.market_value) * 100).toFixed(1) }}%<span class="hide-mobile"> · {{ b.bid - t.market_value | money }}</span>)</span>
                              }
                            </span>
                          </div>
                        }
                      </div>
                    </div>
                  }
                </div>
              }
              @if (!group.purchases.length) {
                <div class="txn-empty">Sin compras</div>
              }
            </div>
            <!-- Sales -->
            <div class="txn-column">
              <h4 class="col-title sales">🔴 Ventas ({{ group.sales.length }})</h4>
              @for (t of group.sales; track t.transaction_id) {
                <div class="txn-card">
                  <div class="txn-header">
                    <img [src]="getPlayerPhoto(t.player_slug)" class="txn-photo" [alt]="t.player_name" loading="lazy"
                         (error)="$event.target.style.display='none'" />
                    <div class="txn-info">
                      <div class="txn-name-row">
                        <strong class="txn-player-name">{{ t.player_name }}</strong>
                        <span class="pos-chip" [class]="'pos-' + getPositionKey(t.player_role)">{{ getPositionLabel(t.player_role) }}</span>
                        @if (t.player_role2) {
                          <span class="pos-chip pos-secondary" [class]="'pos-' + getPositionKey(t.player_role2)">{{ getPositionLabel(t.player_role2) }}</span>
                        }
                      </div>
                      <div class="txn-team-row">
                        @if (t.real_team_logo) {
                          <img [src]="'https://static02.mondocore.com/futmondo/img/teams/64/' + t.real_team_logo" class="txn-team-logo" loading="lazy" (error)="$event.target.style.display='none'" />
                        }
                        <span>{{ t.real_team_name }}</span>
                      </div>
                    </div>
                    <div class="txn-right">
                      <strong class="txn-buyer-name">{{ t.team_name }}</strong>
                      @if (t.buyer_name !== 'Mercado') {
                        <span class="txn-from">→ {{ t.buyer_name }}</span>
                      }
                    </div>
                  </div>
                  <div class="txn-price-block">
                    <div class="txn-price-main">
                      <span class="txn-price-label">Vendido por</span>
                      <span class="txn-price-value">{{ t.price | money }}</span>
                    </div>
                    @if (t.market_value) {
                      <div class="txn-price-secondary">
                        <span class="txn-price-label">Valor mercado</span>
                        <span class="txn-price-value">{{ t.market_value | money }}</span>
                      </div>
                    }
                    @if (t.original_buy_price) {
                      <div class="txn-price-secondary">
                        <span class="txn-price-label">Fichado por</span>
                        <span class="txn-price-value">{{ t.original_buy_price | money }}</span>
                      </div>
                    }
                    @if (t.sale_profit != null) {
                      <div class="txn-price-overpay">
                        <span class="txn-price-label">Plusvalía</span>
                        <span class="txn-price-value" [class]="t.sale_profit >= 0 ? 'profit-positive' : 'profit-negative'">
                          {{ t.sale_profit >= 0 ? '+' : '' }}{{ t.sale_profit | money }}
                        </span>
                      </div>
                    }
                  </div>
                  <div class="txn-badges-row">
                    @if (t.sofascore_rating != null) {
                      <span class="badge-item"><span class="badge-label">Sofa</span><span class="badge-val">{{ t.sofascore_rating.toFixed(1) }}</span></span>
                    }
                    @if (t.starter_pct != null) {
                      <span class="badge-item"><span class="badge-label">Tit</span><span class="badge-val">{{ t.starter_pct }}%</span></span>
                    }
                  </div>
                </div>
              }
              @if (!group.sales.length) {
                <div class="txn-empty">Sin ventas</div>
              }
            </div>
          </div>
        </div>
      }
    }
  `,

  styles: [`
    .description { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin-bottom: 16px; }
    :host { display: block; overflow-x: hidden; }
    .loading { display: flex; align-items: center; gap: 16px; padding: 60px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .error-message { padding: 16px; background: #ffebee; color: #d32f2f; border-radius: 8px; }
    .empty { text-align: center; padding: 60px 20px; color: var(--mat-sys-on-surface-variant); font-size: 1.1em; }
    .count { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin-bottom: 16px; }
    .filters-toggle { display: flex; align-items: center; gap: 8px; padding: 10px 16px; margin-bottom: 12px; border-radius: 10px; background: var(--mat-sys-surface-container); cursor: pointer; font-weight: 600; font-size: 0.9em; color: var(--mat-sys-on-surface); }
    .filters-toggle:hover { background: var(--mat-sys-surface-container-highest); }
    .toggle-arrow { margin-left: auto; }
    .filters { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin-bottom: 20px; }
    .filter-team { flex: 1; min-width: 180px; }
    .filter-dates { display: flex; gap: 8px; flex: 1; min-width: 280px; }
    .filter-date { flex: 1; }
    .clear-btn { flex-shrink: 0; background-color: var(--mat-sys-primary); color: var(--mat-sys-on-primary); }
    .clear-btn-mobile { width: 100%; margin-top: 4px; }
    .desktop-only { display: inline-flex; }
    .mobile-only { display: none; }
    @media (max-width: 600px) { .filter-dates { min-width: 100%; } .desktop-only { display: none; } .mobile-only { display: block; } }
    .date-block { margin-bottom: 24px; }
    .date-header { font-weight: 700; font-size: 1em; padding: 10px 16px; background: var(--mat-sys-surface-container); border-radius: 10px; margin-bottom: 12px; color: var(--mat-sys-on-surface); }
    .date-content { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    @media (max-width: 768px) { .date-content { grid-template-columns: 1fr; } .txn-card { overflow: hidden; } }
    .txn-column { display: flex; flex-direction: column; gap: 8px; }
    .col-title { margin: 0 0 8px; font-size: 0.85em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }
    .col-title.purchases { color: #2e7d32; }
    .col-title.sales { color: #d32f2f; }
    .txn-card { padding: 14px; border-radius: 12px; background: var(--mat-sys-surface-container); border: 1px solid var(--mat-sys-outline-variant); }
    .dark-theme .txn-card { border-color: rgba(132,150,124,0.2); }
    .txn-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
    .txn-photo { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; background: #f0f0f0; flex-shrink: 0; }
    .txn-info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
    .txn-name-row { display: flex; align-items: center; gap: 8px; }
    .txn-player-name { font-size: 1.1em; }
    .pos-chip { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.7em; font-weight: 600; color: #333; }
    .pos-fwd { background: #e57373; }
    .pos-mid { background: #64b5f6; }
    .pos-def { background: #ffb74d; }
    .pos-gk { background: #4caf50; }
    .pos-secondary { opacity: 0.8; margin-left: 2px; }
    .txn-meta { font-size: 0.8em; color: var(--mat-sys-on-surface-variant); }
    .txn-team-row { display: flex; align-items: center; gap: 6px; font-size: 0.85em; color: var(--mat-sys-on-surface-variant); }
    .txn-team-logo { width: 18px; height: 18px; object-fit: contain; }
    .txn-right { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; flex-shrink: 0; }
    .txn-buyer-name { font-size: 0.85em; color: var(--mat-sys-on-surface); }
    .txn-from { font-size: 0.75em; color: var(--mat-sys-on-surface-variant); font-style: italic; }
    .txn-badges-row { display: flex; gap: 8px; margin-top: 8px; }
    .txn-badges { display: flex; flex-direction: column; gap: 4px; flex-shrink: 0; }
    .badge-item { display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 6px; font-size: 0.75em; font-weight: 700; background: rgba(0,196,36,0.1); color: #00C424; border: 1px solid rgba(0,196,36,0.25); }
    .badge-label { font-size: 0.85em; text-transform: uppercase; opacity: 0.8; }
    .badge-val { font-weight: 800; }
    .txn-price-block { background: var(--mat-sys-surface-container-highest); border-radius: 10px; padding: 12px; display: flex; gap: 12px; flex-wrap: wrap; align-items: center; justify-content: center; overflow: hidden; }
    .dark-theme .txn-price-block { background: rgba(53,53,52,0.5); }
    .txn-price-main, .txn-price-secondary, .txn-price-overpay { display: flex; flex-direction: column; align-items: center; gap: 2px; }
    .txn-price-label { font-size: 0.6em; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--mat-sys-on-surface-variant); }
    .txn-price-value { font-size: 1.1em; font-weight: 700; color: var(--mat-sys-on-surface); }
    .overpay-extreme { color: #b71c1c !important; }
    .overpay-high { color: #d32f2f !important; }
    .overpay-mild { color: #e65100 !important; }
    .profit-positive { color: #2e7d32 !important; }
    .profit-negative { color: #d32f2f !important; }
    .txn-badges-row { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
    .badge-bids { background: rgba(217, 70, 239, 0.1); color: #d946ef; border-color: rgba(217, 70, 239, 0.25); cursor: default; }
    .txn-bids { margin-top: 10px; padding: 10px 12px; border-radius: 10px; background: var(--mat-sys-surface-container-highest); border: 1px solid var(--mat-sys-outline-variant); }
    .dark-theme .txn-bids { background: rgba(53,53,52,0.5); border-color: rgba(132,150,124,0.15); }
    .txn-bids-title { font-size: 0.75em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #d946ef; display: block; margin-bottom: 8px; }
    .txn-bids-list { display: flex; flex-direction: column; gap: 6px; }
    .txn-bid-item { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px solid var(--mat-sys-outline-variant); }
    .txn-bid-item:last-child { border-bottom: none; }
    .txn-bid-name { font-size: 0.85em; color: var(--mat-sys-on-surface-variant); font-weight: 500; }
    .txn-bid-amount { font-size: 0.9em; font-weight: 700; color: var(--mat-sys-on-surface); }
    .txn-bid-overpay { font-size: 0.8em; font-weight: 500; color: #e65100; margin-left: 4px; }
    @media (max-width: 600px) { .hide-mobile { display: none; } .txn-bid-amount { font-size: 0.8em; } .txn-bid-name { font-size: 0.8em; } }
    .txn-empty { font-size: 0.85em; color: var(--mat-sys-on-surface-variant); padding: 12px; text-align: center; font-style: italic; }
  `]
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

  getPlayerPhoto(slug: string): string {
    return `https://static01.mondocore.com/futmondo/img/faces/64/${slug}.png`;
  }

  getTeamLogo(teamName: string): string {
    const slug = (teamName || '').toLowerCase().replace(/ /g, '-').replace(/á/g,'a').replace(/é/g,'e').replace(/í/g,'i').replace(/ó/g,'o').replace(/ú/g,'u').replace(/ñ/g,'n');
    return `https://static02.mondocore.com/futmondo/img/teams/64/${slug}.png`;
  }

  getPositionLabel(position: string): string {
    const p = (position || '').toLowerCase();
    if (p.includes('delantero')) return 'DL';
    if (p.includes('centrocampista')) return 'MC';
    if (p.includes('defensa')) return 'DF';
    if (p.includes('portero')) return 'PT';
    return position;
  }

  getPositionKey(position: string): string {
    const p = (position || '').toLowerCase();
    if (p.includes('delantero')) return 'fwd';
    if (p.includes('centrocampista')) return 'mid';
    if (p.includes('defensa')) return 'def';
    if (p.includes('portero')) return 'gk';
    return 'mid';
  }
}
