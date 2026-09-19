import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { Router } from '@angular/router';

import { AuthService } from './auth.service';

/**
 * Seeded spec for `AuthService` (FR10.3.1, FR1.2, FR4.5, BR4.3).
 *
 * Freezes the current auth behavior: in-memory access token (never in
 * localStorage), `withCredentials` for `/auth/*`, session recovery on startup,
 * and local session teardown on logout/failed refresh. Uses invented fake
 * tokens only — never real secrets (gitleaks scans *.spec.ts).
 */
const USER_STORAGE_KEY = 'futmondo_user';
const FAKE_ACCESS_TOKEN = 'fake-access-token-abc';
const FAKE_REFRESH_TOKEN = 'fake-refreshed-token-def';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let router: { navigate: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    localStorage.clear();
    router = { navigate: vi.fn() };

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([])),
        provideHttpClientTesting(),
        { provide: Router, useValue: router },
        AuthService,
      ],
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('login guarda el token en memoria, persiste el usuario y envia withCredentials', async () => {
    const loginPromise = service.login('coach@example.com', 'secreto-de-prueba');

    const req = httpMock.expectOne('/auth/login');
    expect(req.request.method).toBe('POST');
    expect(req.request.withCredentials).toBe(true);
    expect(req.request.body).toEqual({
      email: 'coach@example.com',
      password: 'secreto-de-prueba',
    });

    req.flush({
      access_token: FAKE_ACCESS_TOKEN,
      token_type: 'bearer',
      expires_in: 3600,
      user_id: 'u-1',
      email: 'coach@example.com',
      display_name: 'Coach',
    });

    await loginPromise;

    expect(service.getAccessToken()).toBe(FAKE_ACCESS_TOKEN);
    expect(service.user()).toEqual({
      user_id: 'u-1',
      email: 'coach@example.com',
      display_name: 'Coach',
    });
    // El token vive solo en memoria: nunca en localStorage.
    expect(localStorage.getItem(USER_STORAGE_KEY)).not.toContain(FAKE_ACCESS_TOKEN);
    expect(service.isAuthenticated()).toBe(true);
  });

  it('refresh actualiza el access token en memoria', async () => {
    const refreshPromise = service.refresh();

    const req = httpMock.expectOne('/auth/refresh');
    expect(req.request.method).toBe('POST');
    expect(req.request.withCredentials).toBe(true);
    req.flush({
      access_token: FAKE_REFRESH_TOKEN,
      token_type: 'bearer',
      expires_in: 3600,
    });

    const token = await refreshPromise;
    expect(token).toBe(FAKE_REFRESH_TOKEN);
    expect(service.getAccessToken()).toBe(FAKE_REFRESH_TOKEN);
  });

  it('refresh fallido limpia la sesion y devuelve null', async () => {
    const refreshPromise = service.refresh();

    httpMock
      .expectOne('/auth/refresh')
      .flush({ detail: 'expired' }, { status: 401, statusText: 'Unauthorized' });

    const token = await refreshPromise;
    expect(token).toBeNull();
    expect(service.getAccessToken()).toBeNull();
    expect(service.user()).toBeNull();
  });

  it('tryRecoverSession sin usuario guardado marca initialized y devuelve false', async () => {
    const recovered = await service.tryRecoverSession();

    expect(recovered).toBe(false);
    expect(service.initialized()).toBe(true);
  });

  it('tryRecoverSession con usuario guardado y refresh OK recupera la sesion', async () => {
    localStorage.setItem(
      USER_STORAGE_KEY,
      JSON.stringify({ user_id: 'u-9', email: 'stored@example.com' }),
    );
    // Re-instanciar para que loadUser lea el usuario ya presente.
    service = TestBed.inject(AuthService);

    const promise = service.tryRecoverSession();
    httpMock.expectOne('/auth/refresh').flush({
      access_token: FAKE_REFRESH_TOKEN,
      token_type: 'bearer',
      expires_in: 3600,
    });

    const recovered = await promise;
    expect(recovered).toBe(true);
    expect(service.initialized()).toBe(true);
    expect(service.getAccessToken()).toBe(FAKE_REFRESH_TOKEN);
  });

  it('logout limpia la sesion local y navega a /login incluso si el revoke falla', async () => {
    const logoutPromise = service.logout();

    httpMock
      .expectOne('/auth/logout')
      .flush({ detail: 'error' }, { status: 500, statusText: 'Server Error' });

    await logoutPromise;
    expect(service.getAccessToken()).toBeNull();
    expect(service.user()).toBeNull();
    expect(localStorage.getItem(USER_STORAGE_KEY)).toBeNull();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });
});
