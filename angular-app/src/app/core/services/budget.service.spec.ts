import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { BudgetService } from './budget.service';

/**
 * Seeded spec for `BudgetService` (FR10.3.2). Verifies the exact analytics
 * endpoints, the optional `championship_id` param wiring, and the sync trigger
 * contract (always `sync_type=all`).
 */
describe('BudgetService', () => {
  let service: BudgetService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), BudgetService],
    });
    service = TestBed.inject(BudgetService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('getBalances sin championship pega a /analytics/balances', async () => {
    const promise = service.getBalances();
    const req = httpMock.expectOne('/api/v1/analytics/balances');
    expect(req.request.method).toBe('GET');
    expect(req.request.params.has('championship_id')).toBe(false);
    req.flush({ balances: [] });
    await expect(promise).resolves.toEqual({ balances: [] });
  });

  it('getBalances adjunta championship_id cuando se pasa', async () => {
    const promise = service.getBalances('champ-1');
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/analytics/balances' && r.params.get('championship_id') === 'champ-1',
    );
    req.flush({ balances: [{ team_id: 't1' }] });
    await promise;
  });

  it('getTeamDetail construye la URL con el teamId', async () => {
    const promise = service.getTeamDetail('team-42', 'champ-1');
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/analytics/balances/team-42',
    );
    expect(req.request.params.get('championship_id')).toBe('champ-1');
    req.flush({ team_id: 'team-42' });
    await promise;
  });

  it('syncTransactions envia POST con sync_type=all', async () => {
    const promise = service.syncTransactions('champ-1');
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/sync/trigger',
    );
    expect(req.request.method).toBe('POST');
    expect(req.request.params.get('sync_type')).toBe('all');
    expect(req.request.params.get('championship_id')).toBe('champ-1');
    req.flush({ status: 'ok' });
    await promise;
  });
});
