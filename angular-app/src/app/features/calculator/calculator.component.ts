import { Component, ChangeDetectionStrategy, inject, signal, effect, ViewChild, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { injectIsMobile } from '../../shared/utils/responsive';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatInputModule } from '@angular/material/input';
import { MAT_DATE_LOCALE, MAT_DATE_FORMATS, DateAdapter, MatNativeDateModule } from '@angular/material/core';
import { FormsModule } from '@angular/forms';
import { SpanishDateAdapter, ES_DATE_FORMATS } from '../../shared/utils/spanish-date-adapter';
import { getPlayerPhoto, getTeamLogo, getPositionKey, getPositionLabel } from '../../shared/utils/player.utils';
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { StarterBadgeComponent } from '../../shared/components/starter-badge.component';
import { StarterCardBadgeComponent } from '../../shared/components/starter-card-badge.component';
import { SofascoreBadgeComponent } from '../../shared/components/sofascore-badge.component';
import { SofascoreCardBadgeComponent } from '../../shared/components/sofascore-card-badge.component';
import { ScrollTopComponent } from '../../shared/components/scroll-top.component';
import { ChampionshipService } from '../../core/services/championship.service';
import { RosterService } from '../../core/services/roster.service';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../market/confirm-dialog.component';
import { PageHeaderComponent } from '../../shared/components/page-header.component';

interface RosterPlayer {
  player_id: string;
  name: string;
  slug: string;
  position: string;
  position2: string;
  team: string;
  team_logo: string;
  value: number;
  buy_price: number;
  profit: number;
  change: number;
  points: number;
  average: number;
  matches: number;
  sofascore_rating: number | null;
  sofascore_url: string | null;
  starter_pct: number | null;
  status: string;
}

@Component({
  selector: 'app-calculator',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    { provide: MAT_DATE_LOCALE, useValue: 'es-ES' },
    { provide: DateAdapter, useClass: SpanishDateAdapter },
    { provide: MAT_DATE_FORMATS, useValue: ES_DATE_FORMATS },
  ],
  imports: [
    MatTableModule, MatSortModule, MatProgressSpinnerModule,
    MatCheckboxModule, MatIconModule, MatTooltipModule, MatButtonModule,
    MatButtonToggleModule, MatFormFieldModule, MatSelectModule,
    MatDatepickerModule, MatNativeDateModule, MatInputModule, FormsModule,
    MoneyPipe, StarterCardBadgeComponent,
    SofascoreCardBadgeComponent, ScrollTopComponent, PageHeaderComponent
  ],
  templateUrl: './calculator.component.html',
  styleUrl: './calculator.component.scss'
})
export class CalculatorComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);
  private rosterService = inject(RosterService);
  private dialog = inject(MatDialog);

  isMobile = injectIsMobile();

  viewMode = signal<'cards' | 'table'>(
    (localStorage.getItem('futmondo_view_calculator') as 'cards' | 'table') || 'table'
  );
  sortField = signal<string>('value');

  @ViewChild(MatSort) set matSort(sort: MatSort) {
    if (sort) this.dataSource.sort = sort;
  }

  dataSource = new MatTableDataSource<RosterPlayer>([]);
  loading = signal(true);
  error = signal('');
  balance = signal(0);
  selling = signal(false);
  sellResult = signal<{ success: boolean; message: string } | null>(null);

  // Selection state — use Record<string, boolean> for Angular change detection
  selectedIds = signal<Record<string, boolean>>({});

  // Date projection
  minDate = new Date();
  targetDate: Date | null = null;
  daysAhead = signal(0);

  columns = ['select', 'name', 'position', 'team', 'value', 'change', 'projected_value', 'profit'];

  // Players signal for reactive computations
  players = signal<RosterPlayer[]>([]);

  // Players currently on sale
  onSalePlayers = signal<any[]>([]);

  // Computed values
  selectedCount = computed(() => Object.keys(this.selectedIds()).length);

  onSaleTotal = computed(() => this.onSalePlayers().reduce((sum, p) => sum + p.value, 0));

  selectedTotal = computed(() => {
    const ids = this.selectedIds();
    const days = this.daysAhead();
    return this.players()
      .filter(p => ids[p.player_id])
      .reduce((sum, p) => sum + p.value + (p.change * days), 0);
  });

  futureBalance = computed(() => this.balance() + this.selectedTotal() + this.onSaleTotal());

  allSelected = computed(() => {
    const players = this.players();
    return players.length > 0 && Object.keys(this.selectedIds()).length === players.length;
  });

  someSelected = computed(() => {
    const s = Object.keys(this.selectedIds()).length;
    return s > 0 && s < this.players().length;
  });

  constructor() {
    if (this.isMobile() && !localStorage.getItem('futmondo_view_calculator')) this.viewMode.set('cards');

    effect(() => {
      const id = this.championshipService.activeId();
      if (id) this.loadData();
    });
  }

  async loadData() {
    this.loading.set(true);
    this.error.set('');
    try {
      const championshipId = this.championshipService.activeId();
      const params = new HttpParams().set('championship_id', championshipId);

      // Load roster, market (for balance), and on-sale players in parallel
      const [rosterData, marketData, onSaleData] = await Promise.all([
        this.rosterService.getMyRoster(championshipId),
        firstValueFrom(this.http.get<any>('/api/v1/market/today', { params })),
        this.rosterService.getOnSale(championshipId),
      ]);

      this.dataSource.data = rosterData.players || [];
      this.players.set(rosterData.players || []);
      this.balance.set(marketData.user_info?.balance || 0);
      this.onSalePlayers.set(onSaleData.players || []);

      // Filter out on-sale players from selectable list
      const onSaleIds = new Set((onSaleData.players || []).map((p: any) => p.player_id));
      const selectable = (rosterData.players || []).filter((p: any) => !onSaleIds.has(p.player_id));
      this.dataSource.data = selectable;
      this.players.set(selectable);
    } catch (err: any) {
      this.error.set(err?.error?.detail || err.message || 'Error cargando datos');
    } finally {
      this.loading.set(false);
    }
  }

  // --- Selection ---
  isSelected(player: RosterPlayer): boolean {
    return !!this.selectedIds()[player.player_id];
  }

  togglePlayer(player: RosterPlayer, selected: boolean) {
    const current = { ...this.selectedIds() };
    if (selected) {
      current[player.player_id] = true;
    } else {
      delete current[player.player_id];
    }
    this.selectedIds.set(current);
  }

  toggleAll(checked: boolean) {
    if (checked) {
      const all: Record<string, boolean> = {};
      this.players().forEach(p => all[p.player_id] = true);
      this.selectedIds.set(all);
    } else {
      this.selectedIds.set({});
    }
  }

  // --- Date projection ---
  onDateChange() {
    if (this.targetDate) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const target = new Date(this.targetDate);
      target.setHours(0, 0, 0, 0);
      const diff = Math.max(0, Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)));
      this.daysAhead.set(diff);
    } else {
      this.daysAhead.set(0);
    }
  }

  getProjectedValue(player: RosterPlayer): number {
    return player.value + (player.change * this.daysAhead());
  }

  getProjectionDelta(player: RosterPlayer): number {
    return player.change * this.daysAhead();
  }

  // --- View helpers ---
  setViewMode(mode: 'cards' | 'table') {
    this.viewMode.set(mode);
    localStorage.setItem('futmondo_view_calculator', mode);
  }

  onSortChange(value: string) {
    this.sortField.set(value);
    this.sortCards();
  }

  sortCards() {
    const field = this.sortField();
    const sorted = [...this.dataSource.data].sort((a: any, b: any) => {
      if (field === 'projected_value') {
        return this.getProjectedValue(b) - this.getProjectedValue(a);
      }
      const va = a[field] ?? -Infinity;
      const vb = b[field] ?? -Infinity;
      return vb - va;
    });
    this.dataSource.data = sorted;
  }

  // Shared utils as class properties for template access
  getPlayerPhoto = getPlayerPhoto;
  getTeamLogo = getTeamLogo;
  getPositionKey = getPositionKey;
  getPositionLabel = getPositionLabel;

  async sellPlayers() {
    const ids = Object.keys(this.selectedIds());
    if (!ids.length) return;

    const count = ids.length;
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Poner a la venta',
        message: `¿Poner a la venta ${count} jugador${count > 1 ? 'es' : ''} a su valor de mercado actual?`,
        confirmText: 'Vender',
        cancelText: 'Cancelar',
      },
      width: '400px',
    });

    const confirmed = await firstValueFrom(dialogRef.afterClosed());
    if (!confirmed) return;

    this.selling.set(true);
    this.sellResult.set(null);
    try {
      const resp = await this.rosterService.sell(this.championshipService.activeId(), ids);
      if (resp.sold === resp.total) {
        this.sellResult.set({ success: true, message: `✅ ${resp.sold} jugador${resp.sold > 1 ? 'es' : ''} puesto${resp.sold > 1 ? 's' : ''} a la venta` });
        // Remove sold players from the list
        const remaining = this.players().filter(p => !this.selectedIds()[p.player_id]);
        this.players.set(remaining);
        this.dataSource.data = remaining;
        this.selectedIds.set({});
        // Reload on-sale players
        this.loadOnSale();
      } else {
        const failed = resp.total - resp.sold;
        this.sellResult.set({ success: false, message: `⚠️ ${resp.sold}/${resp.total} vendidos, ${failed} fallaron` });
      }
    } catch (err: any) {
      this.sellResult.set({ success: false, message: err?.error?.detail || 'Error al poner a la venta' });
    } finally {
      this.selling.set(false);
    }
  }

  async cancelSale(player: any) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Cancelar venta',
        message: `¿Retirar a ${player.name} del mercado?`,
        confirmText: 'Retirar',
        cancelText: 'No',
        color: 'warn',
      },
      width: '400px',
    });

    const confirmed = await firstValueFrom(dialogRef.afterClosed());
    if (!confirmed) return;

    try {
      await this.rosterService.cancelSale(this.championshipService.activeId(), player.player_id);
      // Remove from on-sale list and reload roster
      this.onSalePlayers.set(this.onSalePlayers().filter(p => p.player_id !== player.player_id));
      this.loadData();
    } catch (err: any) {
      this.sellResult.set({ success: false, message: err?.error?.detail || 'Error al cancelar venta' });
    }
  }

  private async loadOnSale() {
    try {
      const data = await this.rosterService.getOnSale(this.championshipService.activeId());
      this.onSalePlayers.set(data.players || []);
    } catch { }
  }
}
