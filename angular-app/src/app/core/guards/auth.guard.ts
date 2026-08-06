import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Check if access token is in memory (set after login or session recovery)
  if (authService.getAccessToken()) {
    return true;
  }

  router.navigate(['/']);
  return false;
};
