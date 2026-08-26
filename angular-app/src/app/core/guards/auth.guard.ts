import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = async () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  // Wait for session recovery to complete (max 3s)
  let attempts = 0;
  while (!auth.initialized() && attempts < 60) {
    await new Promise(r => setTimeout(r, 50));
    attempts++;
  }

  if (auth.getAccessToken()) return true;
  router.navigate(['/login']);
  return false;
};
