import { Component, inject, signal, computed } from '@angular/core';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { MoneyPipe } from '../../../shared/pipes/money.pipe';
import { SyncService } from '../../../core/services/sync.service';
import { ChampionshipService } from '../../../core/services/championship.service';
import { SyncTaskResponse, SyncTaskStepProgress } from '../../../core/models/budget.model';

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

const STEP_LABELS: Record<string, string> = {
  initializing: 'Inicializando...',
  players: 'Jugadores',
  transactions: 'Transacciones',
  clauses: 'Cláusulas',
  punishments_bonuses: 'Castigos y bonificaciones',
  dream_teams: 'Dream teams y MVPs',
  player_performance: 'Rendimiento por jornada',
  rosters: 'Plantillas',
  team_standings: 'Clasificación',
  match_odds: 'Cuotas de partidos',
};

const ALL_STEPS = [
  'players', 'transactions', 'clauses', 'punishments_bonuses',
  'dream_teams', 'player_performance', 'rosters', 'team_standings', 'match_odds'
];

@Component({
  selector: 'app-sync-dialog',
  standalone: true,
  imports: [
    MatDialogModule, MatButtonModule, MatProgressSpinnerModule,
    MatProgressBarModule, MatIconModule, MatDividerModule, MoneyPipe
  ],
  template: `
    <h2 mat-dialog-title>🔄 Sincronización</h2>
    <mat-dialog-content>
      <!-- Phase: Syncing with progress -->
      @if (phase() === 'syncing') {
        <div class="sync-steps">
          @for (step of allSteps; track step) {
            <div class="step-row" [class.active]="currentStep() === step" [class.done]="isStepDone(step)" [class.pending]="!isStepDone(step) && currentStep() !== step">
              @if (isStepDone(step)) {
                <mat-icon class="step-icon done">check_circle</mat-icon>
              } @else if (currentStep() === step) {
                <mat-spinner diameter="18" class="step-icon" />
              } @else {
                <mat-icon class="step-icon pending">radio_button_unchecked</mat-icon>
              }
              <span class="step-label">{{ stepLabel(step) }}</span>
              @if (isStepDone(step) && stepRecords(step) !== null) {
                <span class="step-records">{{ stepRecords(step) }} registros</span>
              }
            </div>
          }
        </div>
        <mat-progress-bar mode="determinate" [value]="progressPercent()" />
        <p class="progress-text">{{ completedSteps() }} de {{ allSteps.length }} pasos completados</p>
      }

      <!-- Phase: Checking phantoms -->
      @if (phase() === 'checking') {
        <div class="sync-progress">
          <mat-spinner diameter="36" />
          <span>Verificando jugadores fantasma...</span>
        </div>
      }

      <!-- Phase: Syncing sofascore -->
      @if (phase() === 'syncing_sofascore') {
        <div class="sync-progress">
          <mat-spinner diameter="36" />
          <span>Sincronizando ratings de Sofascore...</span>
        </div>
      }

      <!-- Phase: Error -->
      @if (phase() === 'error') {
        <div class="sync-result error">
          <mat-icon>error</mat-icon>
          <span>{{ error() }}</span>
        </div>
      }

      <!-- Phase: Done -->
      @if (phase() === 'done') {
        <div class="sync-result success">
          <mat-icon>check_circle</mat-icon>
          <div class="result-details">
            <p><strong>{{ totalRecords() }}</strong> registros sincronizados</p>
            @if (sofascoreResult()) {
              <p><strong>{{ sofascoreResult()!.players_synced }}</strong> jugadores con stats de Sofascore</p>
            }
            <p class="duration">Duración: {{ duration().toFixed(1) }}s</p>
          </div>
        </div>

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
      <button mat-button [disabled]="phase() === 'syncing' || phase() === 'checking' || phase() === 'syncing_sofascore'" (click)="close()">Cerrar</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .sync-steps { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
    .step-row { display: flex; align-items: center; gap: 10px; padding: 4px 0; transition: opacity 0.2s; }
    .step-row.pending { opacity: 0.4; }
    .step-row.active { opacity: 1; font-weight: 500; }
    .step-row.done { opacity: 0.8; }
    .step-icon { width: 18px; height: 18px; font-size: 18px; }
    .step-icon.done { color: #16a34a; }
    .step-icon.pending { color: var(--mat-sys-on-surface-variant); }
    .step-label { flex: 1; }
    .step-records { font-size: 0.8em; color: var(--mat-sys-on-surface-variant); }
    .progress-text { text-align: center; font-size: 0.85em; color: var(--mat-sys-on-surface-variant); margin-top: 8px; }
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
  private syncService = inject(SyncService);
  private championshipService = inject(ChampionshipService);
  private dialogRef = inject(MatDialogRef<SyncDialogComponent>);

  phase = signal<'syncing' | 'checking' | 'syncing_sofascore' | 'done' | 'error'>('syncing');
  error = signal('');
  currentStep = signal<string | null>(null);
  stepProgress = signal<Record<string, SyncTaskStepProgress>>({});
  finalResult = signal<SyncTaskResponse | null>(null);
  sofascoreResult = signal<{ players_synced: number } | null>(null);
  phantoms = signal<PhantomPlayer[]>([]);

  allSteps = ALL_STEPS;

  completedSteps = computed(() => {
    const progress = this.stepProgress();
    return Object.values(progress).filter(s => s.status !== 'running').length;
  });

  progressPercent = computed(() => {
    return (this.completedSteps() / this.allSteps.length) * 100;
  });

  totalRecords = computed(() => {
    const result = this.finalResult()?.result;
    if (!result) return 0;
    return Object.values(result).reduce((sum, step) => sum + (step.records_synced || 0), 0);
  });

  duration = computed(() => {
    const task = this.finalResult();
    if (!task?.started_at || !task?.completed_at) return 0;
    return (new Date(task.completed_at).getTime() - new Date(task.started_at).getTime()) / 1000;
  });

  constructor() {
    this.runSync();
  }

  stepLabel(step: string): string {
    return STEP_LABELS[step] || step;
  }

  isStepDone(step: string): boolean {
    const s = this.stepProgress()[step];
    return !!s && s.status !== 'running';
  }

  stepRecords(step: string): number | null {
    const s = this.stepProgress()[step];
    return s?.records_synced ?? null;
  }

  async runSync() {
    const championshipId = this.championshipService.activeId();

    // Phase 1: Async sync with progress polling
    try {
      const finalTask = await this.syncService.syncWithPolling(
        championshipId,
        (task) => {
          this.currentStep.set(task.current_step);
          this.stepProgress.set({ ...task.progress });
        }
      );

      if (finalTask.status === 'failed') {
        this.error.set(finalTask.error || 'Error desconocido en la sincronización');
        this.phase.set('error');
        return;
      }

      this.finalResult.set(finalTask);
    } catch (err: any) {
      const detail = err?.error?.detail || err?.message || 'Error al sincronizar';
      this.error.set(detail);
      this.phase.set('error');
      return;
    }

    // Phase 2: Check phantoms
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
      // Non-critical
    }

    // Phase 3: Sync Sofascore
    this.phase.set('syncing_sofascore');
    try {
      let params = new HttpParams();
      if (championshipId) params = params.set('championship_id', championshipId);
      const sofaData = await firstValueFrom(
        this.http.post<any>('/api/v1/sync/sofascore', {}, { params })
      );
      this.sofascoreResult.set({
        players_synced: sofaData.players_synced || sofaData.synced_count || 0,
      });
    } catch {
      // Non-critical
    }

    this.phase.set('done');
  }

  close() {
    this.dialogRef.close();
  }
}
