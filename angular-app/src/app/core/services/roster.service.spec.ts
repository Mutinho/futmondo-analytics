import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { RosterService } from './roster.service';

/**
 * Seeded spec for `RosterService` (FR10.3.2). CRUD boundary over the roster
 * endpoints: verifies URLs, params, methods and request bodies.
 */
describe('RosterService', () => {
  let service: RosterService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), RosterService],
    });
    service = TestBed.inject(RosterService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('getMyRoster pega a /roster/my con championship_id', async () => {
    const promise = service.getMyRoster('champ-1');
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/roster/my' && r.params.get('championship_id') === 'champ-1',
    );
    expect(req.request.method).toBe('GET');
    req.flush({ players: [] });
    await expect(promise).resolves.toEqual({ players: [] });
  });

  it('getOnSale pega a /roster/on-sale con championship_id', async () => {
    const promise = service.getOnSale('champ-1');
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/roster/on-sale' && r.params.get('championship_id') === 'champ-1',
    );
    expect(req.request.method).toBe('GET');
    req.flush({ players: [] });
    await promise;
  });

  it('sell envia POST con championship_id y player_ids en el body', async () => {
    const promise = service.sell('champ-1', ['p1', 'p2']);
    const req = httpMock.expectOne('/api/v1/roster/sell');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      championship_id: 'champ-1',
      player_ids: ['p1', 'p2'],
    });
    req.flush({ ok: true });
    await promise;
  });

  it('cancelSale envia POST con el player_id concreto', async () => {
    const promise = service.cancelSale('champ-1', 'p9');
    const req = httpMock.expectOne('/api/v1/roster/cancel-sale');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      championship_id: 'champ-1',
      player_id: 'p9',
    });
    req.flush({ ok: true });
    await promise;
  });
});
