import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { SyncTriggerResponse, SyncTaskResponse } from '../models/budget.model';

@Injectable({ providedIn: 'root' })
export class SyncService {
  private http = inject(HttpClient);

  /** Trigger async sync — returns immediately with task_id */
  triggerSync(championshipId?: string, syncType = 'all'): Promise<SyncTriggerResponse> {
    let params = new HttpParams().set('sync_type', syncType);
    if (championshipId) params = params.set('championship_id', championshipId);
    return firstValueFrom(
      this.http.post<SyncTriggerResponse>('/api/v1/sync/trigger', {}, { params })
    );
  }

  /** Poll task status */
  getTaskStatus(taskId: string): Promise<SyncTaskResponse> {
    return firstValueFrom(
      this.http.get<SyncTaskResponse>(`/api/v1/sync/task/${taskId}`)
    );
  }

  /**
   * Trigger sync and poll until completed/failed.
   * Calls onProgress on every poll with the current task state.
   * Returns the final SyncTaskResponse.
   */
  async syncWithPolling(
    championshipId: string | undefined,
    onProgress: (task: SyncTaskResponse) => void,
    pollIntervalMs = 2000,
  ): Promise<SyncTaskResponse> {
    const trigger = await this.triggerSync(championshipId);
    const taskId = trigger.task_id;

    while (true) {
      await this.delay(pollIntervalMs);
      const task = await this.getTaskStatus(taskId);
      onProgress(task);

      if (task.status === 'completed' || task.status === 'failed') {
        return task;
      }
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
