import { Component, inject, signal, effect, ViewChild, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
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
import { MAT_DATE_LOCALE, MAT_DATE_FORMATS, DateAdapter, NativeDateAdapter, MatNativeDateModule } from '@angular/material/core';
import { FormsModule } from '@angular/forms';

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
  override getFirstDayOfWeek(): number {
    return 1; // Monday
  }
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
import { MoneyPipe } from '../../shared/pipes/money.pipe';
import { StarterBadgeComponent } from '../../shared/components/starter-badge.component';
import { StarterCardBadgeComponent } from '../../shared/components/starter-card-badge.component';
import { SofascoreBadgeComponent } from '../../shared/components/sofascore-badge.component';
import { SofascoreCardBadgeComponent } from '../../shared/components/sofascore-card-badge.component';
import { ScrollTopComponent } from '../../shared/components/scroll-top.component';
import { ChampionshipService } from '../../core/services/championship.service';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../market/confirm-dialog.component';

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
    MoneyPipe, StarterBadgeComponent, StarterCardBadgeComponent,
    SofascoreBadgeComponent, SofascoreCardBadgeComponent, ScrollTopComponent
  ],
  template: `
    <h1>🧮 Calculadora</h1>
    <p class="description">Selecciona jugadores para simular ventas y proyecta su valor por tendencia.</p>

    @if (loading()) {
      <div class="loading"><mat-spinner diameter="40" /> <span>Cargando plantilla...</span></div>
    } @else if (error()) {
      <div class="error-message">{{ error() }}</div>
    } @else {
      <!-- Summary header -->
      <div class="calc-header">
        <div class="calc-header-item">
          <span class="calc-header-label">Saldo actual</span>
          <span class="calc-header-value" [class]="balance() >= 0 ? 'positive' : 'negative'">{{ balance() | money }}</span>
        </div>
        <div class="calc-header-item">
          <span class="calc-header-label">En venta</span>
          <span class="calc-header-value on-sale">{{ onSaleTotal() | money }}</span>
        </div>
        <div class="calc-header-item">
          <span class="calc-header-label">Seleccionadas</span>
          <span class="calc-header-value sales">{{ selectedTotal() | money }}</span>
        </div>
        <div class="calc-header-item">
          <span class="calc-header-label">Saldo futuro</span>
          <span class="calc-header-value" [class]="futureBalance() >= 0 ? 'positive' : 'negative'">{{ futureBalance() | money }}</span>
        </div>
      </div>

      <!-- On-sale players -->
      @if (onSalePlayers().length > 0) {
        <div class="on-sale-section">
          <h3 class="on-sale-title">🏷️ En venta ({{ onSalePlayers().length }})</h3>
          <div class="on-sale-cards">
            @for (p of onSalePlayers(); track p.player_id) {
              <div class="on-sale-card">
                <div class="on-sale-card-info">
                  <img [src]="getPlayerPhoto(p.slug)" class="on-sale-photo" [alt]="p.name" loading="lazy"
                       (error)="$event.target.style.display='none'" />
                  <div>
                    <strong>{{ p.name }}</strong>
                    <span class="on-sale-team">{{ p.team }}</span>
                  </div>
                </div>
                <div class="on-sale-card-price">{{ p.value | money }}</div>
                <button mat-icon-button class="on-sale-cancel" (click)="cancelSale(p)" matTooltip="Cancelar venta">
                  <mat-icon>close</mat-icon>
                </button>
              </div>
            }
          </div>
        </div>
      }

      <!-- Sell FAB (floating) -->
      @if (selectedCount() > 0) {
        <div class="sell-fab" (click)="sellPlayers()">
          @if (selling()) {
            <mat-spinner diameter="22" />
          } @else {
            <mat-icon>storefront</mat-icon>
          }
          <span class="sell-fab-label">Vender ({{ selectedCount() }})</span>
        </div>
      }
      @if (sellResult()) {
        <div class="sell-toast" [class]="sellResult()!.success ? 'success' : 'error'">
          {{ sellResult()!.message }}
        </div>
      }

      <!-- Date picker for projection -->
      <div class="date-row">
        <mat-form-field appearance="outline" class="date-field" subscriptSizing="dynamic">
          <mat-label>Fecha de venta</mat-label>
          <input matInput [matDatepicker]="picker" [min]="minDate" [(ngModel)]="targetDate" (dateChange)="onDateChange()">
          <mat-datepicker-toggle matIconSuffix [for]="picker" />
          <mat-datepicker #picker />
        </mat-form-field>
        <span class="days-label">
          @if (daysAhead() > 0) {
            {{ daysAhead() }} {{ daysAhead() === 1 ? 'día' : 'días' }} a futuro
          } @else {
            Hoy (valor actual)
          }
        </span>
      </div>

      <!-- View toggle + sort -->
      <div class="view-toggle">
        @if (viewMode() === 'cards') {
          <mat-form-field appearance="outline" class="sort-field" subscriptSizing="dynamic">
            <mat-label>Ordenar por</mat-label>
            <mat-select [value]="sortField()" (selectionChange)="onSortChange($event.value)">
              <mat-option value="projected_value">Valor proyectado</mat-option>
              <mat-option value="value">Valor actual</mat-option>
              <mat-option value="change">Tendencia</mat-option>
              <mat-option value="profit">Plusvalía</mat-option>
            </mat-select>
          </mat-form-field>
        }
        <mat-button-toggle-group [value]="viewMode()" (change)="setViewMode($event.value)" hideSingleSelectionIndicator>
          <mat-button-toggle value="cards"><mat-icon>grid_view</mat-icon></mat-button-toggle>
          <mat-button-toggle value="table"><mat-icon>table_rows</mat-icon></mat-button-toggle>
        </mat-button-toggle-group>
      </div>

      <p class="player-count">{{ players().length }} jugadores disponibles</p>

      @if (viewMode() === 'table') {
      <div class="table-container">
        <table mat-table [dataSource]="dataSource" matSort>
          <!-- Checkbox -->
          <ng-container matColumnDef="select">
            <th mat-header-cell *matHeaderCellDef>
              <mat-checkbox [checked]="allSelected()" [indeterminate]="someSelected()" (change)="toggleAll($event.checked)" />
            </th>
            <td mat-cell *matCellDef="let p">
              <mat-checkbox [checked]="isSelected(p)" (click)="$event.stopPropagation()" (change)="togglePlayer(p, $event.checked)" />
            </td>
          </ng-container>

          <!-- Name -->
          <ng-container matColumnDef="name">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Jugador</th>
            <td mat-cell *matCellDef="let p" class="player-cell">
              <div class="player-wrapper">
                <img [src]="getPlayerPhoto(p.slug)" class="player-photo" [alt]="p.name" loading="lazy"
                     (error)="$event.target.style.display='none'" />
                <strong>{{ p.name }}</strong>
              </div>
            </td>
          </ng-container>

          <!-- Position -->
          <ng-container matColumnDef="position">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Pos</th>
            <td mat-cell *matCellDef="let p">
              <span class="pos-chip" [class]="'pos-' + getPositionKey(p.position)">{{ getPositionLabel(p.position) }}</span>
            </td>
          </ng-container>

          <!-- Team -->
          <ng-container matColumnDef="team">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Equipo</th>
            <td mat-cell *matCellDef="let p" class="team-cell">
              <div class="team-wrapper">
                <img [src]="getTeamLogo(p.team_logo)" class="team-logo" [alt]="p.team" loading="lazy"
                     (error)="$event.target.style.display='none'" />
                <span>{{ p.team }}</span>
              </div>
            </td>
          </ng-container>

          <!-- Current Value -->
          <ng-container matColumnDef="value">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Valor actual</th>
            <td mat-cell *matCellDef="let p">{{ p.value | money }}</td>
          </ng-container>

          <!-- Trend -->
          <ng-container matColumnDef="change">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Tendencia</th>
            <td mat-cell *matCellDef="let p" [class]="p.change > 0 ? 'trend-up' : p.change < 0 ? 'trend-down' : 'trend-neutral'">
              @if (p.change !== 0) {
                {{ p.change > 0 ? '▲' : '▼' }} {{ p.change | money }}
              } @else {
                -
              }
            </td>
          </ng-container>

          <!-- Projected Value -->
          <ng-container matColumnDef="projected_value">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Valor proyectado</th>
            <td mat-cell *matCellDef="let p">
              <span class="projected" [class]="getProjectedValue(p) >= p.value ? 'trend-up' : 'trend-down'">
                {{ getProjectedValue(p) | money }}
              </span>
              @if (daysAhead() > 0 && p.change !== 0) {
                <span class="projection-delta" [class]="p.change > 0 ? 'trend-up' : 'trend-down'">
                  ({{ p.change > 0 ? '+' : '' }}{{ getProjectionDelta(p) | money }})
                </span>
              }
            </td>
          </ng-container>

          <!-- Profit -->
          <ng-container matColumnDef="profit">
            <th mat-header-cell *matHeaderCellDef mat-sort-header>Plusvalía</th>
            <td mat-cell *matCellDef="let p" [class]="p.profit >= 0 ? 'trend-up' : 'trend-down'">
              {{ p.profit >= 0 ? '+' : '' }}{{ p.profit | money }}
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="columns"></tr>
          <tr mat-row *matRowDef="let row; columns: columns" [class.selected-row]="isSelected(row)" (click)="togglePlayer(row, !isSelected(row))"></tr>
        </table>
      </div>
      }

      @if (viewMode() === 'cards') {
      <div class="cards-container">
        @for (p of dataSource.data; track p.player_id) {
          <article class="player-card" [class.selected-card]="isSelected(p)" (click)="togglePlayer(p, !isSelected(p))">
            <div class="card-header">
              <div class="card-avatar">
                <img [src]="getPlayerPhoto(p.slug)" [alt]="p.name" loading="lazy"
                     (error)="$event.target.style.display='none'" />
              </div>
              <div class="card-name-block">
                <h3 class="card-player-name">{{ p.name }}</h3>
                <div class="card-team-row">
                  <img [src]="getTeamLogo(p.team_logo)" class="card-team-logo" [alt]="p.team" loading="lazy"
                       (error)="$event.target.style.display='none'" />
                  <span class="card-team-name">{{ p.team }}</span>
                </div>
                <div class="card-badges">
                  <app-sofascore-card-badge [rating]="p.sofascore_rating" />
                  <app-starter-card-badge [pct]="p.starter_pct" />
                </div>
              </div>
              <div class="card-select" (click)="$event.stopPropagation(); togglePlayer(p, !isSelected(p))">
                @if (isSelected(p)) {
                  <div class="check-circle selected">
                    <mat-icon>check</mat-icon>
                  </div>
                } @else {
                  <div class="check-circle"></div>
                }
              </div>
              <span class="pos-chip card-pos-top" [class]="'pos-' + getPositionKey(p.position)">{{ getPositionLabel(p.position) }}</span>
            </div>
            <div class="card-stats-box">
              <div class="card-stats-grid">
                <div class="card-stat-item">
                  <span class="card-stat-label">VALOR ACTUAL</span>
                  <span class="card-stat-val">{{ p.value | money }}</span>
                </div>
                <div class="card-stat-item">
                  <span class="card-stat-label">TENDENCIA</span>
                  <span class="card-stat-val trend" [class.up]="p.change > 0" [class.down]="p.change < 0">
                    @if (p.change !== 0) { {{ p.change > 0 ? '↗' : '↘' }} {{ p.change | money }} } @else { - }
                  </span>
                </div>
                <div class="card-stat-item">
                  <span class="card-stat-label">VALOR PROYECTADO</span>
                  <span class="card-stat-val trend" [class.up]="getProjectedValue(p) >= p.value" [class.down]="getProjectedValue(p) < p.value">
                    {{ getProjectedValue(p) | money }}
                  </span>
                </div>
                <div class="card-stat-item">
                  <span class="card-stat-label">PLUSVALÍA</span>
                  <span class="card-stat-val trend" [class.up]="p.profit >= 0" [class.down]="p.profit < 0">{{ p.profit >= 0 ? '+' : '' }}{{ p.profit | money }}</span>
                </div>
              </div>
            </div>
          </article>
        }
      </div>
      <app-scroll-top />
      }
    }
  `,
  styles: [`
    .description { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin-bottom: 24px; }
    .player-count { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin: 0 0 12px; font-weight: 500; }
    .loading { display: flex; align-items: center; gap: 16px; padding: 60px; justify-content: center; color: var(--mat-sys-on-surface-variant); }
    .error-message { padding: 16px; background: #ffebee; color: #d32f2f; border-radius: 8px; }

    /* Header */
    .calc-header {
      display: flex; gap: 24px; flex-wrap: wrap; padding: 20px 24px;
      background: var(--mat-sys-surface-container); border-radius: 12px; margin-bottom: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .calc-header-item { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 120px; }
    .calc-header-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--mat-sys-on-surface-variant); font-weight: 600; }
    .calc-header-value { font-size: 1.4em; font-weight: 700; color: var(--mat-sys-on-surface); }
    .calc-header-value.positive { color: #2e7d32; }
    .calc-header-value.negative { color: #d32f2f; }
    .calc-header-value.sales { color: #1565c0; }
    .calc-header-value.on-sale { color: #e65100; }
    .calc-header-value.count { color: var(--mat-sys-on-surface); }

    /* On-sale section */
    .on-sale-section { margin-bottom: 20px; }
    .on-sale-title { font-size: 1em; margin: 0 0 12px; color: var(--mat-sys-on-surface); }
    .on-sale-cards { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; flex-wrap: wrap; }
    .on-sale-cards::-webkit-scrollbar { height: 4px; }
    .on-sale-cards::-webkit-scrollbar-thumb { background: var(--mat-sys-outline-variant); border-radius: 4px; }
    .on-sale-card {
      min-width: 240px; flex-shrink: 0;
      display: flex; align-items: center; gap: 12px;
      padding: 12px 16px; border-radius: 12px;
      background: var(--mat-sys-surface-container);
      border: 1px dashed #e65100;
      opacity: 0.75;
    }
    @media (max-width: 768px) {
      .on-sale-cards { flex-wrap: nowrap; }
    }
    .on-sale-card-info { display: flex; align-items: center; gap: 10px; flex: 1; }
    .on-sale-card-info div { display: flex; flex-direction: column; }
    .on-sale-photo { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; background: #f0f0f0; }
    .on-sale-team { font-size: 0.8em; color: var(--mat-sys-on-surface-variant); }
    .on-sale-card-price { font-weight: 700; font-size: 0.9em; color: #e65100; white-space: nowrap; }
    .on-sale-cancel { color: #d32f2f; }

    /* Date row */
    .date-row { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }

    /* Sell FAB */
    .sell-fab {
      position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); z-index: 100;
      display: flex; align-items: center; gap: 8px;
      padding: 14px 24px; border-radius: 28px;
      background: #2e7d32; color: #fff;
      font-weight: 700; font-size: 0.95em;
      box-shadow: 0 4px 16px rgba(0,0,0,0.25);
      cursor: pointer; transition: transform 0.15s, box-shadow 0.15s;
    }
    .sell-fab:hover { transform: translateX(-50%) scale(1.03); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }
    .sell-fab:active { transform: translateX(-50%) scale(0.97); }
    .sell-fab mat-icon { font-size: 20px; width: 20px; height: 20px; }
    .dark-theme .sell-fab { background: #14FF00; color: #000; }
    .sell-toast {
      position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%); z-index: 100;
      padding: 10px 20px; border-radius: 20px; font-size: 0.85em; font-weight: 600;
      box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    }
    .sell-toast.success { background: #e8f5e9; color: #2e7d32; }
    .sell-toast.error { background: #ffebee; color: #d32f2f; }
    .date-field { width: 200px; }
    .days-label { font-size: 0.9em; color: var(--mat-sys-on-surface-variant); font-weight: 500; }

    /* View toggle */
    .view-toggle { display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-bottom: 16px; }
    .sort-field { flex: 1; font-size: 0.9em; }

    /* Table */
    .table-container { overflow-x: auto; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    table { width: 100%; }
    .player-cell .player-wrapper { display: inline-flex; align-items: center; gap: 10px; }
    .player-photo { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: #f0f0f0; flex-shrink: 0; }
    .team-cell .team-wrapper { display: inline-flex; align-items: center; gap: 8px; }
    .team-logo { width: 32px; height: 32px; object-fit: contain; flex-shrink: 0; }
    .pos-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; color: #333; }
    .pos-fwd { background: #e57373; }
    .pos-mid { background: #64b5f6; }
    .pos-def { background: #ffb74d; }
    .pos-gk { background: #4caf50; }
    .trend-up { color: #2e7d32; font-weight: 600; }
    .trend-down { color: #d32f2f; font-weight: 600; }
    .trend-neutral { color: var(--mat-sys-on-surface-variant); }
    .projected { font-weight: 700; }
    .projection-delta { font-size: 0.8em; margin-left: 6px; }
    .selected-row { background: rgba(76, 175, 80, 0.08); }
    .dark-theme .selected-row { background: rgba(20, 255, 0, 0.06); }

    /* Cards */
    .cards-container { display: grid; grid-template-columns: 1fr; gap: 16px; }
    @media (min-width: 900px) { .cards-container { grid-template-columns: repeat(2, 1fr); } }
    @media (min-width: 1300px) { .cards-container { grid-template-columns: repeat(3, 1fr); } }
    @media (min-width: 1700px) { .cards-container { grid-template-columns: repeat(4, 1fr); } }
    .player-card {
      padding: 20px; border-radius: 16px; cursor: pointer;
      background: var(--mat-sys-surface-container);
      border: 1px solid var(--mat-sys-outline-variant);
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .player-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
    .selected-card {
      border-color: #0c370e;
      background: #0c370e;
      .card-player-name, .card-team-name, .card-stat-val, .card-stat-label { color: #fff; }
      .card-stats-box { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); }
      .pos-chip { opacity: 0.9; }
    }
    .dark-theme .selected-card {
      border-color: #14FF00;
      background: rgba(20, 255, 0, 0.1);
    }
    .dark-theme .player-card { border-color: rgba(20, 255, 0, 0.15); }
    .card-header { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 16px; position: relative; }
    .card-avatar { width: 56px; height: 56px; border-radius: 50%; overflow: hidden; border: 2px solid var(--mat-sys-primary); padding: 2px; flex-shrink: 0; }
    .card-avatar img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
    .card-name-block { flex: 1; display: flex; flex-direction: column; gap: 4px; }
    .card-player-name { font-size: 1.15em; font-weight: 700; margin: 0; color: var(--mat-sys-on-surface); }
    .card-team-row { display: flex; align-items: center; gap: 8px; }
    .card-team-logo { width: 22px; height: 22px; object-fit: contain; }
    .card-team-name { font-size: 0.9em; color: var(--mat-sys-on-surface-variant); font-weight: 500; }
    .card-pos-top { position: absolute; top: 4px; right: 44px; }
    .card-select { position: absolute; top: 4px; right: 4px; }
    .check-circle {
      width: 28px; height: 28px; border-radius: 50%;
      border: 2px solid var(--mat-sys-outline);
      display: flex; align-items: center; justify-content: center;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .check-circle:hover { border-color: #4caf50; }
    .check-circle.selected {
      background: #4caf50; border-color: #4caf50;
      mat-icon { color: #fff; font-size: 18px; width: 18px; height: 18px; }
    }
    .dark-theme .check-circle.selected { background: #14FF00; border-color: #14FF00; mat-icon { color: #000; } }
    .card-badges { display: flex; gap: 10px; margin-top: 8px; }
    .card-stats-box { background: var(--mat-sys-surface-container-highest); border-radius: 12px; padding: 14px; border: 1px solid var(--mat-sys-outline-variant); }
    .dark-theme .card-stats-box { background: rgba(53,53,52,0.5); border-color: rgba(132,150,124,0.2); }
    .card-stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .card-stat-item { display: flex; flex-direction: column; gap: 2px; }
    .card-stat-label { font-size: 0.65em; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--mat-sys-on-surface-variant); }
    .card-stat-val { font-size: 1.05em; font-weight: 600; color: var(--mat-sys-on-surface); }
    .card-stat-val.trend.up { color: #00C424; }
    .dark-theme .card-stat-val.trend.up { color: #14FF00; }
    .card-stat-val.trend.down { color: #d32f2f; }
  `]
})
export class CalculatorComponent {
  private http = inject(HttpClient);
  private championshipService = inject(ChampionshipService);
  private breakpointObserver = inject(BreakpointObserver);
  private dialog = inject(MatDialog);

  isMobile = toSignal(
    this.breakpointObserver.observe([Breakpoints.Handset]).pipe(map(r => r.matches)),
    { initialValue: false }
  );

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
      const params = new HttpParams().set('championship_id', this.championshipService.activeId());

      // Load roster, market (for balance), and on-sale players in parallel
      const [rosterData, marketData, onSaleData] = await Promise.all([
        firstValueFrom(this.http.get<any>('/api/v1/roster/my', { params })),
        firstValueFrom(this.http.get<any>('/api/v1/market/today', { params })),
        firstValueFrom(this.http.get<any>('/api/v1/roster/on-sale', { params })),
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

  getPlayerPhoto(slug: string): string {
    return `https://static01.mondocore.com/futmondo/img/faces/64/${slug}.png`;
  }

  getTeamLogo(logo: string): string {
    return `https://static02.mondocore.com/futmondo/img/teams/64/${logo}`;
  }

  getPositionKey(position: string): string {
    const p = (position || '').toLowerCase();
    if (p.includes('delantero')) return 'fwd';
    if (p.includes('centrocampista')) return 'mid';
    if (p.includes('defensa')) return 'def';
    if (p.includes('portero')) return 'gk';
    return 'mid';
  }

  getPositionLabel(position: string): string {
    const p = (position || '').toLowerCase();
    if (p.includes('delantero')) return 'DL';
    if (p.includes('centrocampista')) return 'MC';
    if (p.includes('defensa')) return 'DF';
    if (p.includes('portero')) return 'PT';
    return position;
  }

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
      const resp = await firstValueFrom(this.http.post<any>('/api/v1/roster/sell', {
        championship_id: this.championshipService.activeId(),
        player_ids: ids,
      }));
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
      await firstValueFrom(this.http.post<any>('/api/v1/roster/cancel-sale', {
        championship_id: this.championshipService.activeId(),
        player_id: player.player_id,
      }));
      // Remove from on-sale list and reload roster
      this.onSalePlayers.set(this.onSalePlayers().filter(p => p.player_id !== player.player_id));
      this.loadData();
    } catch (err: any) {
      this.sellResult.set({ success: false, message: err?.error?.detail || 'Error al cancelar venta' });
    }
  }

  private async loadOnSale() {
    try {
      const params = new HttpParams().set('championship_id', this.championshipService.activeId());
      const data = await firstValueFrom(this.http.get<any>('/api/v1/roster/on-sale', { params }));
      this.onSalePlayers.set(data.players || []);
    } catch { }
  }
}
