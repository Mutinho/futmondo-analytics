import { Component, inject, signal, computed } from '@angular/core';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
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
  prizes: 'Premios',
  phantoms: 'Verificar fantasmas',
};

const ALL_STEPS = [
  'players', 'transactions', 'clauses', 'punishments_bonuses',
  'dream_teams', 'player_performance', 'rosters', 'team_standings', 'match_odds',
  'prizes', 'phantoms'
];

@Component({
  selector: 'app-sync-dialog',
  standalone: true,
  imports: [
    MatDialogModule, MatButtonModule, MatProgressSpinnerModule,
    MatProgressBarModule, MatIconModule, MatDividerModule,
    MoneyPipe
  ],
  templateUrl: './sync-dialog.component.html',
  styleUrl: './sync-dialog.component.scss'
})
export class SyncDialogComponent {
  private syncService = inject(SyncService);
  private championshipService = inject(ChampionshipService);
  private dialogRef = inject(MatDialogRef<SyncDialogComponent>);

  phase = signal<'config' | 'syncing' | 'done' | 'error'>('config');
  error = signal('');
  currentStep = signal<string | null>(null);
  stepProgress = signal<Record<string, SyncTaskStepProgress>>({});
  finalResult = signal<SyncTaskResponse | null>(null);
  phantoms = signal<PhantomPlayer[]>([]);

  activeSteps = computed(() => ALL_STEPS);

  completedSteps = computed(() => {
    const progress = this.stepProgress();
    return Object.values(progress).filter(s => s.status !== 'running').length;
  });

  progressPercent = computed(() => {
    return (this.completedSteps() / this.activeSteps().length) * 100;
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
    // Check if there's already a running sync — if so, go directly to syncing phase
    this.checkExistingSync();
  }

  private async checkExistingSync() {
    const existing = await this.syncService.getActiveTask();
    if (existing) {
      this.phase.set('syncing');
      this.currentStep.set(existing.current_step);
      this.stepProgress.set({ ...existing.progress });
      this.pollUntilDone(existing.task_id);
    }
  }

  stepLabel(step: string): string {
    return STEP_LABELS[step] || step;
  }

  isStepDone(step: string): boolean {
    const s = this.stepProgress()[step];
    return !!s && s.status !== 'running';
  }

  stepRecords(step: string): number | null {
    const s = this.stepProgress()[step] as any;
    return s?.records_synced ?? s?.synced ?? s?.total_phantoms ?? null;
  }

  startSync() {
    this.phase.set('syncing');
    this.runSync();
  }

  async runSync() {
    const championshipId = this.championshipService.activeId();

    try {
      const finalTask = await this.syncService.syncWithPolling(
        championshipId,
        (task) => {
          this.currentStep.set(task.current_step);
          this.stepProgress.set({ ...task.progress });
        },
        2000,
      );

      this.handleComplete(finalTask);
    } catch (err: any) {
      const detail = err?.error?.detail || err?.message || 'Error al sincronizar';
      this.error.set(detail);
      this.phase.set('error');
    }
  }

  private async pollUntilDone(taskId: string) {
    try {
      while (true) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        const task = await this.syncService.getTaskStatus(taskId);
        this.currentStep.set(task.current_step);
        this.stepProgress.set({ ...task.progress });

        if (task.status === 'completed' || task.status === 'failed') {
          this.syncService.clearTaskId();
          this.handleComplete(task);
          return;
        }
      }
    } catch (err: any) {
      this.error.set(err?.message || 'Error al obtener el estado del sync');
      this.phase.set('error');
    }
  }

  private handleComplete(finalTask: SyncTaskResponse) {
    if (finalTask.status === 'failed') {
      this.error.set(finalTask.error || 'Error desconocido en la sincronización');
      this.phase.set('error');
      return;
    }

    this.finalResult.set(finalTask);

    const phantomsData = finalTask.result?.['phantoms'] as any;
    if (phantomsData?.roster_phantoms?.length || phantomsData?.sold_phantoms?.length) {
      const all = [...(phantomsData.roster_phantoms || []), ...(phantomsData.sold_phantoms || [])];
      this.phantoms.set(all);
    }

    this.phase.set('done');
  }

  close() {
    this.dialogRef.close();
  }
}
