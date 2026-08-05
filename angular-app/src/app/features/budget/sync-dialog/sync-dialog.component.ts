import { Component, inject, signal } from '@angular/core';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';
import { BudgetService } from '../../../core/services/budget.service';
import { ChampionshipService } from '../../../core/services/championship.service';

interface PhantomPlayer {
  team_name: string;
  player_name: string;
  value?: number;
  sell_price?: number;
  sell_date?: string;
  type: 'roster' | 'sold';
}

interface PhantomsResponse {
  success: boolean;
  roster_phantoms: PhantomPlayer[];
  sold_phantoms: PhantomPlayer[];
  total_phantoms: number;
}

@Component({
  selector: 'app-sync-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule, MatProgressSpinnerModule, MatIconModule, MatDividerModule, MoneyPipe],
  template: `
    <h2 mat-dialog-title>🔄 Sincronización</h2>
    <mat-dialog-content>
      <!-- Fase 1: Sync -->
      @if (phase() === 'syncing') {
        <div class="sync-progress">
          <mat-spinner diameter="36" />
          <span>Sincronizando datos...</span>
        </div>
      }

      <!-- Fase 2: Checking phantoms -->
      @if (phase() === 'checking') {
        <div class="sync-progress">
          <mat-spinner diameter="36" />
          <span>Verificando jugadores fantasma...</span>
        </div>
      }

      <!-- Fase 3: Error -->
      @if (phase() === 'error') {
        <div class="sync-result error">
          <mat-icon>error</mat-icon>
          <span>{{ error() }}</span>
        </div>
      }

      <!-- Fase 4: Resultado -->
      @if (phase() === 'done') {
        <div class="sync-result success">
          <mat-icon>check_circle</mat-icon>
          <div class="result-details">
            <p><strong>{{ syncResult()!.records_synced }}</strong> nuevas transacciones</p>
            <p class="duration">Duración: {{ syncResult()!.duration_seconds.toFixed(1) }}s</p>
          </div>
        </div>

        <!-- Avisos de fantasmas -->
        @if (phantoms().length) {
          <mat-divider />
          <div class="phantoms-section">
            <h3>⚠️ Jugadores sin compra registrada ({{ phantoms().length }})</h3>
            <p class="phantom-hint">Estos jugadores necesitan que se registre su compra manualmente.</p>
            <div class="phantom-list">
              @for (p of phantoms(); track p.player_name + p.team_name) {
                <div class="phantom-item">
                  <span class="phantom-player">{{ p.player_name }}</span>
                  <span class="phantom-team">{{ p.team_name }}</span>
                  @if (p.type === 'roster') {
                    <span class="phantom-badge roster">En plantilla (valor: {{ p.value | money }})</span>
                  } @else {
                    <span class="phantom-badge sold">Vendido por {{ p.sell_price | money }} ({{ p.sell_date }})</span>
                  }
                </div>
              }
            </div>
          </div>
        } @else {
          <div class="no-phantoms">
            <mat-icon>verified</mat-icon>
            <span>Todas las transacciones están correctas</span>
          </div>
        }
      }
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button [disabled]="phase() === 'syncing' || phase() === 'checking'" (click)="close()">Cerrar</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .sync-progress { display: flex; align-items: center; gap: 16px; padding: 24px 0; }
    .sync-result { display: flex; align-items: flex-start; gap: 12px; padding: 16px 0; }
    .sync-result.success mat-icon { color: #16a34a; font-size: 32px; width: 32px; height: 32px; }
    .sync-result.error mat-icon { color: #dc2626; font-size: 32px; width: 32px; height: 32px; }
    .result-details p { margin: 4px 0; }
    .duration { color: var(--mat-sys-on-surface-variant); font-size: 0.85em; }
    .phantoms-section { margin-top: 16px; }
    .phantoms-section h3 { color: #d97706; margin-bottom: 4px; font-size: 1em; }
    .phantom-hint { color: var(--mat-sys-on-surface-variant); font-size: 0.8em; margin-bottom: 12px; }
    .phantom-list { max-height: 200px; overflow-y: auto; }
    .phantom-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--mat-sys-outline-variant); flex-wrap: wrap; }
    .phantom-player { font-weight: 600; }
    .phantom-team { color: var(--mat-sys-on-surface-variant); font-size: 0.85em; }
    .phantom-badge { font-size: 0.75em; padding: 2px 8px; border-radius: 12px; }
    .phantom-badge.roster { background: #fef3c7; color: #92400e; }
    .phantom-badge.sold { background: #fee2e2; color: #991b1b; }
    .no-phantoms { display: flex; align-items: center; gap: 8px; padding: 12px 0; color: #16a34a; }
    .no-phantoms mat-icon { font-size: 20px; width: 20px; height: 20px; }
    mat-dialog-content { min-width: 450px; }
  `]
})
export class SyncDialogComponent {
  private http = inject(HttpClient);
  private budgetService = inject(BudgetService);
  private championshipService = inject(ChampionshipService);
  private dialogRef = inject(MatDialogRef<SyncDialogComponent>);

  phase = signal<'syncing' | 'checking' | 'done' | 'error'>('syncing');
  error = signal('');
  syncResult = signal<{ records_synced: number; duration_seconds: number; status: string } | null>(null);
  phantoms = signal<PhantomPlayer[]>([]);

  constructor() {
    this.runSync();
  }

  async runSync() {
    const championshipId = this.championshipService.activeId();

    // Fase 1: Sync completo
    try {
      const data = await this.budgetService.syncTransactions(championshipId);
      const results = data.results || {};
      const txn = results.transactions || results;
      this.syncResult.set({
        records_synced: txn.records_synced || 0,
        duration_seconds: txn.duration_seconds || 0,
        status: txn.status || 'success',
      });
    } catch (err: any) {
      this.error.set(err.message || 'Error al sincronizar');
      this.phase.set('error');
      return;
    }

    // Fase 2: Check phantoms
    this.phase.set('checking');
    try {
      let params = new HttpParams();
      if (championshipId) params = params.set('championship_id', championshipId);
      const phantomData = await firstValueFrom(
        this.http.post<PhantomsResponse>('/api/v1/sync/check-phantoms', {}, { params })
      );
      const all = [...(phantomData.roster_phantoms || []), ...(phantomData.sold_phantoms || [])];
      this.phantoms.set(all);
    } catch {
      // Si falla el check, no es crítico — mostramos resultado del sync sin avisos
    }

    this.phase.set('done');
  }

  close() {
    this.dialogRef.close(this.syncResult());
  }
}
