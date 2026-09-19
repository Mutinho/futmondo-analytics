import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { AnalyticsService } from './analytics.service';

/**
 * Seeded spec for `AnalyticsService` (FR10.3.2). Verifies a representative set
 * of the read-only analytics endpoints, their default window params, and the
 * multi-value `exclude_matchday` param appending.
 */
describe('AnalyticsService', () => {
  let service: AnalyticsService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), AnalyticsService],
    });
    service = TestBed.inject(AnalyticsService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('getTrends usa el window por defecto (5)', async () => {
    const promise = service.getTrends();
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/analytics/championship/trends' && r.params.get('window') === '5',
    );
    expect(req.request.method).toBe('GET');
    req.flush({ championship_id: 'c1', latest_matchday: 1, teams: [] });
    await promise;
  });

  it('getCustomClassification adjunta cada exclude_matchday', async () => {
    const promise = service.getCustomClassification(7, [3, 4]);
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/analytics/championship/custom-classification',
    );
    expect(req.request.params.get('window')).toBe('7');
    expect(req.request.params.getAll('exclude_matchday')).toEqual(['3', '4']);
    req.flush({
      championship_id: 'c1',
      latest_matchday: 7,
      window: 7,
      excluded_matchdays: [3, 4],
      available_matchdays: [],
      included_matchdays: [],
      classification: [],
    });
    await promise;
  });

  it('getHeatmap pega al endpoint de heatmap', async () => {
    const promise = service.getHeatmap();
    const req = httpMock.expectOne('/api/v1/analytics/championship/heatmap');
    expect(req.request.method).toBe('GET');
    req.flush({ championship_id: 'c1', latest_matchday: 1, matchdays: [] });
    await promise;
  });

  it('getWatchlist adjunta championship_id cuando se pasa', async () => {
    const promise = service.getWatchlist('champ-1');
    const req = httpMock.expectOne(
      (r) =>
        r.url === '/api/v1/analytics/market/watchlist' &&
        r.params.get('championship_id') === 'champ-1',
    );
    req.flush({ championship_id: 'champ-1', total: 0, players: [] });
    await promise;
  });

  it('getProjections pega al endpoint de projections', async () => {
    const promise = service.getProjections();
    const req = httpMock.expectOne('/api/v1/analytics/projections/matchday');
    req.flush({ championship_id: 'c1', target_matchday: 2, window: 5, matches: [] });
    await promise;
  });
});
