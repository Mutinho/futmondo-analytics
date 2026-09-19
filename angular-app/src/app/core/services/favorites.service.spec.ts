import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { FavoritesService } from './favorites.service';

/**
 * Seeded spec for `FavoritesService` (FR10.3.2). Verifies the favorites
 * endpoints and how the `unfollow` action wires both ids as query params.
 */
describe('FavoritesService', () => {
  let service: FavoritesService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), FavoritesService],
    });
    service = TestBed.inject(FavoritesService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('getMyFavorites pega a /favorites/my con championship_id', async () => {
    const promise = service.getMyFavorites('champ-1');
    const req = httpMock.expectOne(
      (r) => r.url === '/api/v1/favorites/my' && r.params.get('championship_id') === 'champ-1',
    );
    expect(req.request.method).toBe('GET');
    req.flush({ favorites: [] });
    await expect(promise).resolves.toEqual({ favorites: [] });
  });

  it('unfollow envia POST con championship_id y player_id como params', async () => {
    const promise = service.unfollow('champ-1', 'p7');
    const req = httpMock.expectOne(
      (r) =>
        r.url === '/api/v1/favorites/unfollow' &&
        r.params.get('championship_id') === 'champ-1' &&
        r.params.get('player_id') === 'p7',
    );
    expect(req.request.method).toBe('POST');
    req.flush({ ok: true });
    await promise;
  });
});
