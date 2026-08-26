import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = async () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  // If not yet initialized, trigger session recovery (handles F5 on protected routes)
  if (!auth.initialized()) {
    await auth.tryRecoverSession();
  }

  if (auth.getAccessToken()) return true;
  router.navigate(['/login'], { replaceUrl: true });
  return false;
};
