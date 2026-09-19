import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { ChampionshipService, type Championship } from './championship.service';

/**
 * Seeded spec for `ChampionshipService` (FR10.3.2). Covers the signal-backed
 * state, the primary endpoint, the fallback to the legacy endpoint, and the
 * localStorage-backed active-championship selection.
 */
const STORAGE_KEY = 'futmondo_active_championship';

function champ(id: string, name = 'Liga'): Championship {
  return {
    championship_id: id,
    name,
    has_clauses: false,
    initial_budget: 100,
    excluded_teams: [],
  };
}

describe('ChampionshipService', () => {
  let service: ChampionshipService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), ChampionshipService],
    });
    service = TestBed.inject(ChampionshipService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('load pega al endpoint primario y auto-selecciona el primero', async () => {
    const promise = service.load();
    const req = httpMock.expectOne('/api/v1/user/championships');
    expect(req.request.method).toBe('GET');
    req.flush({ success: true, championships: [champ('c1'), champ('c2')] });

    await promise;
    expect(service.championships().length).toBe(2);
    expect(service.activeChampionship()?.championship_id).toBe('c1');
    expect(localStorage.getItem(STORAGE_KEY)).toBe('c1');
  });

  it('load cae al endpoint legacy cuando el primario falla', async () => {
    const promise = service.load();
    httpMock
      .expectOne('/api/v1/user/championships')
      .flush({ detail: 'nope' }, { status: 500, statusText: 'Server Error' });
    // Dejar que el catch (que lanza la peticion legacy) corra antes de esperarla.
    await Promise.resolve();
    const fallback = httpMock.expectOne('/api/v1/championships');
    fallback.flush({ success: true, championships: [champ('legacy')] });

    await promise;
    expect(service.championships()[0].championship_id).toBe('legacy');
  });

  it('setActive actualiza los signals y persiste en localStorage', () => {
    const c = champ('c9', 'Con clausulas');
    service.setActive({ ...c, has_clauses: true });

    expect(service.activeChampionship()?.championship_id).toBe('c9');
    expect(service.activeId()).toBe('c9');
    expect(service.hasClauses()).toBe(true);
    expect(localStorage.getItem(STORAGE_KEY)).toBe('c9');
  });
});
