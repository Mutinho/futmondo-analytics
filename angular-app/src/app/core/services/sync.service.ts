import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { SyncTriggerResponse, SyncTaskResponse } from '../models/budget.model';

const SYNC_TASK_KEY = 'futmondo_sync_task_id';

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

  /** Get saved task_id from localStorage (if any) */
  getSavedTaskId(): string | null {
    return localStorage.getItem(SYNC_TASK_KEY);
  }

  /** Save task_id to localStorage */
  saveTaskId(taskId: string): void {
    localStorage.setItem(SYNC_TASK_KEY, taskId);
  }

  /** Clear saved task_id */
  clearTaskId(): void {
    localStorage.removeItem(SYNC_TASK_KEY);
  }

  /**
   * Check if there's a running sync we can reconnect to.
   * Returns the task if still running/pending, otherwise null (and clears storage).
   */
  async getActiveTask(): Promise<SyncTaskResponse | null> {
    const taskId = this.getSavedTaskId();
    if (!taskId) return null;

    try {
      const task = await this.getTaskStatus(taskId);
      if (task.status === 'running' || task.status === 'pending') {
        return task;
      }
      // Task finished — clear it
      this.clearTaskId();
      return null;
    } catch {
      // Task not found (404) or error — clear
      this.clearTaskId();
      return null;
    }
  }

  /**
   * Trigger sync and poll until completed/failed.
   * Saves task_id to localStorage. Clears on completion.
   * Calls onProgress on every poll with the current task state.
   */
  async syncWithPolling(
    championshipId: string | undefined,
    onProgress: (task: SyncTaskResponse) => void,
    pollIntervalMs = 2000,
  ): Promise<SyncTaskResponse> {
    let taskId: string;

    // Check if there's already a running task saved
    const existing = await this.getActiveTask();
    if (existing) {
      taskId = existing.task_id;
      onProgress(existing);
    } else {
      const trigger = await this.triggerSync(championshipId);
      taskId = trigger.task_id;
      this.saveTaskId(taskId);
    }

    while (true) {
      await this.delay(pollIntervalMs);
      const task = await this.getTaskStatus(taskId);
      onProgress(task);

      if (task.status === 'completed' || task.status === 'failed') {
        this.clearTaskId();
        return task;
      }
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
