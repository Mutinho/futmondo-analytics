import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { EvolutionService } from './evolution.service';

/**
 * Seeded spec for `EvolutionService` (FR10.3.2). Verifies the endpoint, the
 * optional `championship_id` param, and the in-memory cache (a second call
 * within the TTL does not hit the network again).
 */
describe('EvolutionService', () => {
  let service: EvolutionService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), EvolutionService],
    });
    service = TestBed.inject(EvolutionService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    vi.useRealTimers();
  });

  it('getEvolution pega a /matchdays/evolution y devuelve la respuesta', async () => {
    const promise = service.getEvolution('champ-1');
    const req = httpMock.expectOne(
      (r) =>
        r.url === '/api/v1/matchdays/evolution' &&
        r.params.get('championship_id') === 'champ-1',
    );
    expect(req.request.method).toBe('GET');
    const payload = { championship_id: 'champ-1', teams: [] } as any;
    req.flush(payload);
    await expect(promise).resolves.toEqual(payload);
  });

  it('cachea la respuesta dentro del TTL (segunda llamada no vuelve a la red)', async () => {
    const payload = { championship_id: 'champ-1', teams: [] } as any;

    const first = service.getEvolution('champ-1');
    httpMock
      .expectOne((r) => r.url === '/api/v1/matchdays/evolution')
      .flush(payload);
    await first;

    // Segunda llamada con la misma clave: servida desde cache, sin HTTP.
    const second = await service.getEvolution('champ-1');
    expect(second).toEqual(payload);
    httpMock.expectNone((r) => r.url === '/api/v1/matchdays/evolution');
  });
});
