import { beforeEach, describe, expect, it, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import {
  type ActivatedRouteSnapshot,
  Router,
  type RouterStateSnapshot,
} from '@angular/router';

import { authGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';

/**
 * Seeded spec for `authGuard` (FR10.3.1, FR1.2).
 *
 * Freezes the current gate behavior: recover the session when the auth state
 * is not yet initialized, allow navigation when an access token exists, and
 * redirect to `/login` with `replaceUrl` when it does not. `CanActivateFn` is
 * invoked inside `TestBed.runInInjectionContext` so its `inject()` calls
 * resolve against the configured providers.
 */
type AuthMock = {
  initialized: ReturnType<typeof vi.fn>;
  tryRecoverSession: ReturnType<typeof vi.fn>;
  getAccessToken: ReturnType<typeof vi.fn>;
};

type RouterMock = {
  navigate: ReturnType<typeof vi.fn>;
};

describe('authGuard', () => {
  let auth: AuthMock;
  let router: RouterMock;

  // The guard reads neither snapshot; empty doubles keep the signature honest.
  const route = {} as ActivatedRouteSnapshot;
  const state = {} as RouterStateSnapshot;

  function runGuard(): boolean | Promise<boolean> {
    return TestBed.runInInjectionContext(() => authGuard(route, state)) as
      | boolean
      | Promise<boolean>;
  }

  beforeEach(() => {
    auth = {
      initialized: vi.fn().mockReturnValue(true),
      tryRecoverSession: vi.fn().mockResolvedValue(false),
      getAccessToken: vi.fn().mockReturnValue(null),
    };
    router = { navigate: vi.fn() };

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: auth },
        { provide: Router, useValue: router },
      ],
    });
  });

  it('permite la navegacion cuando ya hay access token e inicializado', async () => {
    auth.initialized.mockReturnValue(true);
    auth.getAccessToken.mockReturnValue('tok-123');

    const result = await runGuard();

    expect(result).toBe(true);
    expect(auth.tryRecoverSession).not.toHaveBeenCalled();
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('recupera la sesion cuando no esta inicializado y luego permite si hay token', async () => {
    auth.initialized.mockReturnValue(false);
    auth.tryRecoverSession.mockResolvedValue(true);
    auth.getAccessToken.mockReturnValue('recovered-tok');

    const result = await runGuard();

    expect(auth.tryRecoverSession).toHaveBeenCalledTimes(1);
    expect(result).toBe(true);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('redirige a /login con replaceUrl cuando no hay token', async () => {
    auth.initialized.mockReturnValue(true);
    auth.getAccessToken.mockReturnValue(null);

    const result = await runGuard();

    expect(result).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/login'], { replaceUrl: true });
  });

  it('tras recuperar sin token redirige a /login', async () => {
    auth.initialized.mockReturnValue(false);
    auth.tryRecoverSession.mockResolvedValue(false);
    auth.getAccessToken.mockReturnValue(null);

    const result = await runGuard();

    expect(auth.tryRecoverSession).toHaveBeenCalledTimes(1);
    expect(result).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/login'], { replaceUrl: true });
  });

  it('no vuelve a recuperar la sesion cuando ya esta inicializado', async () => {
    auth.initialized.mockReturnValue(true);
    auth.getAccessToken.mockReturnValue('tok');

    await runGuard();

    expect(auth.tryRecoverSession).not.toHaveBeenCalled();
  });
});
