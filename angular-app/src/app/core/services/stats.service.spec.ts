import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { StatsService } from './stats.service';

/**
 * Seeded spec for `StatsService` (FR10.3.2). Verifies the three stats
 * endpoints and the per-key in-memory cache shared across them.
 */
describe('StatsService', () => {
  let service: StatsService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), StatsService],
    });
    service = TestBed.inject(StatsService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('getUserStats pega a /user-stats/ y cachea la respuesta', async () => {
    const payload = { user_id: 'u1' } as any;
    const first = service.getUserStats('champ-1');
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/user-stats/' && r.params.get('championship_id') === 'champ-1',
    );
    expect(req.request.method).toBe('GET');
    req.flush(payload);
    await expect(first).resolves.toEqual(payload);

    // Cache hit: sin segunda peticion.
    await service.getUserStats('champ-1');
    httpMock.expectNone((r) => r.url === '/api/v1/user-stats/');
  });

  it('getPlayerFinances pega a /player-finances/', async () => {
    const promise = service.getPlayerFinances('champ-1');
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/player-finances/' && r.params.get('championship_id') === 'champ-1',
    );
    req.flush({ players: [] });
    await promise;
  });

  it('getClausulablePlayers pega a /clausulable-players/', async () => {
    const promise = service.getClausulablePlayers();
    const req = httpMock.expectOne('/api/v1/clausulable-players/');
    expect(req.request.params.has('championship_id')).toBe(false);
    req.flush({ players: [] });
    await promise;
  });
});
