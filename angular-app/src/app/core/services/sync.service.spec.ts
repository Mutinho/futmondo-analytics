import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { SyncService } from './sync.service';

/**
 * Seeded spec for `SyncService` (FR10.3.2). Verifies the trigger/polling
 * endpoints, the localStorage task-id helpers and the reconnect logic in
 * `getActiveTask` (keeps a running task, clears a finished/absent one).
 */
const SYNC_TASK_KEY = 'futmondo_sync_task_id';

describe('SyncService', () => {
  let service: SyncService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), SyncService],
    });
    service = TestBed.inject(SyncService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('triggerSync envia POST con sync_type y championship_id', async () => {
    const promise = service.triggerSync('champ-1');
    const req = httpMock.expectOne(
      (r) =>
        r.url === '/api/v1/sync/trigger' &&
        r.params.get('sync_type') === 'all' &&
        r.params.get('championship_id') === 'champ-1',
    );
    expect(req.request.method).toBe('POST');
    req.flush({ task_id: 't-1' });
    await expect(promise).resolves.toEqual({ task_id: 't-1' });
  });

  it('los helpers de localStorage guardan, leen y limpian el task_id', () => {
    expect(service.getSavedTaskId()).toBeNull();
    service.saveTaskId('t-99');
    expect(localStorage.getItem(SYNC_TASK_KEY)).toBe('t-99');
    expect(service.getSavedTaskId()).toBe('t-99');
    service.clearTaskId();
    expect(service.getSavedTaskId()).toBeNull();
  });

  it('getActiveTask mantiene una tarea en curso', async () => {
    service.saveTaskId('t-run');
    const promise = service.getActiveTask();
    const req = httpMock.expectOne('/api/v1/sync/task/t-run');
    req.flush({ task_id: 't-run', status: 'running' });

    const task = await promise;
    expect(task?.status).toBe('running');
    expect(service.getSavedTaskId()).toBe('t-run');
  });

  it('getActiveTask limpia una tarea ya finalizada', async () => {
    service.saveTaskId('t-done');
    const promise = service.getActiveTask();
    httpMock.expectOne('/api/v1/sync/task/t-done').flush({ task_id: 't-done', status: 'completed' });

    const task = await promise;
    expect(task).toBeNull();
    expect(service.getSavedTaskId()).toBeNull();
  });

  it('getActiveTask sin task_id guardado devuelve null sin tocar la red', async () => {
    const task = await service.getActiveTask();
    expect(task).toBeNull();
    httpMock.expectNone(() => true);
  });
});
