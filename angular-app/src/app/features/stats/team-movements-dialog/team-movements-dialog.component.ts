import { Component, inject, signal, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { DatePipe } from '@angular/common';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';
import { BudgetService } from '../../../core/services/budget.service';
import { Transaction } from '../../../core/models/budget.model';

export interface TeamMovementsDialogData {
  teamId: string;
  teamName: string;
  championshipId: string;
}

@Component({
  selector: 'app-team-movements-dialog',
  standalone: true,
  imports: [MatDialogModule, MatTableModule, MatSortModule, MatButtonModule, MatProgressSpinnerModule, MatTabsModule, DatePipe, MoneyPipe],
  template: `
    <h2 mat-dialog-title>{{ data.teamName }}</h2>
    <mat-dialog-content>
      @if (loading()) {
        <div class="loading"><mat-spinner diameter="32" /> Cargando movimientos...</div>
      } @else {
        <mat-tab-group>
          <mat-tab label="📥 Compras ({{ purchasesSource.data.length }})">
            @if (purchasesSource.data.length) {
              <table mat-table [dataSource]="purchasesSource" matSort #purchaseSort="matSort" class="movements-table">
                <ng-container matColumnDef="player_name">
                  <th mat-header-cell *matHeaderCellDef mat-sort-header>Jugador</th>
                  <td mat-cell *matCellDef="let t">{{ t.player_name }}</td>
                </ng-container>
                <ng-container matColumnDef="price">
                  <th mat-header-cell *matHeaderCellDef mat-sort-header>Precio</th>
                  <td mat-cell *matCellDef="let t" class="money-neg">{{ t.price | money }}</td>
                </ng-container>
                <ng-container matColumnDef="from">
                  <th mat-header-cell *matHeaderCellDef mat-sort-header>Procedencia</th>
                  <td mat-cell *matCellDef="let t">{{ t.from }}</td>
                </ng-container>
                <ng-container matColumnDef="date">
                  <th mat-header-cell *matHeaderCellDef mat-sort-header>Fecha</th>
                  <td mat-cell *matCellDef="let t">{{ t.date | date:'dd/MM/yy' }}</td>
                </ng-container>
                <tr mat-header-row *matHeaderRowDef="purchaseCols"></tr>
                <tr mat-row *matRowDef="let row; columns: purchaseCols"></tr>
              </table>
            } @else {
              <p class="empty">Sin compras registradas</p>
            }
          </mat-tab>
          <mat-tab label="📤 Ventas ({{ salesSource.data.length }})">
            @if (salesSource.data.length) {
              <table mat-table [dataSource]="salesSource" matSort #saleSort="matSort" class="movements-table">
                <ng-container matColumnDef="player_name">
                  <th mat-header-cell *matHeaderCellDef mat-sort-header>Jugador</th>
                  <td mat-cell *matCellDef="let t">{{ t.player_name }}</td>
                </ng-container>
                <ng-container matColumnDef="price">
                  <th mat-header-cell *matHeaderCellDef mat-sort-header>Precio</th>
                  <td mat-cell *matCellDef="let t" class="money-pos">{{ t.price | money }}</td>
                </ng-container>
                <ng-container matColumnDef="to">
                  <th mat-header-cell *matHeaderCellDef mat-sort-header>Destino</th>
                  <td mat-cell *matCellDef="let t">{{ t.to }}</td>
                </ng-container>
                <ng-container matColumnDef="date">
                  <th mat-header-cell *matHeaderCellDef mat-sort-header>Fecha</th>
                  <td mat-cell *matCellDef="let t">{{ t.date | date:'dd/MM/yy' }}</td>
                </ng-container>
                <tr mat-header-row *matHeaderRowDef="saleCols"></tr>
                <tr mat-row *matRowDef="let row; columns: saleCols"></tr>
              </table>
            } @else {
              <p class="empty">Sin ventas registradas</p>
            }
          </mat-tab>
        </mat-tab-group>
      }
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cerrar</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .loading { display: flex; align-items: center; gap: 12px; padding: 24px; }
    .movements-table { width: 100%; margin-top: 12px; }
    .money-neg { color: #dc2626; font-weight: 600; }
    .money-pos { color: #16a34a; font-weight: 600; }
    .empty { padding: 24px; text-align: center; color: var(--mat-sys-on-surface-variant); }
    mat-dialog-content { min-width: 500px; max-height: 60vh; }
  `]
})
export class TeamMovementsDialogComponent {
  data = inject<TeamMovementsDialogData>(MAT_DIALOG_DATA);
  private budgetService = inject(BudgetService);

  loading = signal(true);
  purchasesSource = new MatTableDataSource<Transaction>([]);
  salesSource = new MatTableDataSource<Transaction>([]);

  @ViewChild('purchaseSort') set purchaseSort(sort: MatSort) {
    if (sort) this.purchasesSource.sort = sort;
  }
  @ViewChild('saleSort') set saleSort(sort: MatSort) {
    if (sort) this.salesSource.sort = sort;
  }

  purchaseCols = ['player_name', 'price', 'from', 'date'];
  saleCols = ['player_name', 'price', 'to', 'date'];

  constructor() {
    this.loadMovements();
  }

  async loadMovements() {
    try {
      const detail = await this.budgetService.getTeamDetail(this.data.teamId, this.data.championshipId);
      this.purchasesSource.data = detail.purchases;
      this.salesSource.data = detail.sales;
    } catch {}
    finally { this.loading.set(false); }
  }
}
