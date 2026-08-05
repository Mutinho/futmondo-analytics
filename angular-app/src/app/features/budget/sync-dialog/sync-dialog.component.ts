import { Component, inject, signal } from '@angular/core';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { BudgetService } from '../../../core/services/budget.service';
import { ChampionshipService } from '../../../core/services/championship.service';

@Component({
  selector: 'app-sync-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule, MatProgressSpinnerModule, MatIconModule],
  template: `
    <h2 mat-dialog-title>🔄 Sincronización</h2>
    <mat-dialog-content>
      @if (syncing()) {
        <div class="sync-progress">
          <mat-spinner diameter="36" />
          <span>Sincronizando transacciones...</span>
        </div>
      } @else if (error()) {
        <div class="sync-result error">
          <mat-icon>error</mat-icon>
          <span>{{ error() }}</span>
        </div>
      } @else if (result()) {
        <div class="sync-result success">
          <mat-icon>check_circle</mat-icon>
          <div class="result-details">
            <p><strong>{{ result()!.records_synced }}</strong> nuevas transacciones</p>
            <p class="duration">Duración: {{ result()!.duration_seconds.toFixed(1) }}s</p>
            <p class="status">Estado: {{ result()!.status }}</p>
          </div>
        </div>
      }
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button [disabled]="syncing()" (click)="close()">Cerrar</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .sync-progress { display: flex; align-items: center; gap: 16px; padding: 24px 0; }
    .sync-result { display: flex; align-items: flex-start; gap: 12px; padding: 16px 0; }
    .sync-result.success mat-icon { color: #16a34a; font-size: 32px; width: 32px; height: 32px; }
    .sync-result.error mat-icon { color: #dc2626; font-size: 32px; width: 32px; height: 32px; }
    .result-details p { margin: 4px 0; }
    .duration, .status { color: var(--mat-sys-on-surface-variant); font-size: 0.85em; }
  `]
})
export class SyncDialogComponent {
  private budgetService = inject(BudgetService);
  private championshipService = inject(ChampionshipService);
  private dialogRef = inject(MatDialogRef<SyncDialogComponent>);

  syncing = signal(true);
  error = signal('');
  result = signal<{ records_synced: number; duration_seconds: number; status: string } | null>(null);

  constructor() {
    this.runSync();
  }

  async runSync() {
    try {
      const data = await this.budgetService.syncTransactions(this.championshipService.activeId());
      this.result.set(data.results.transactions);
    } catch (err: any) {
      this.error.set(err.message || 'Error al sincronizar');
    } finally {
      this.syncing.set(false);
    }
  }

  close() {
    this.dialogRef.close(this.result());
  }
}
