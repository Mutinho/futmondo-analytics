import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { from } from 'rxjs';
import { AuthService } from '../services/auth.service';

/** URLs that should NOT get the Authorization header */
const SKIP_AUTH_URLS = ['/auth/login', '/auth/refresh', '/auth/logout'];

/** URLs that need withCredentials (cookie-based auth) */
const COOKIE_URLS = ['/auth/'];

/** Flag to prevent multiple simultaneous refresh attempts */
let isRefreshing = false;

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  // Add withCredentials for /auth endpoints (sends HttpOnly cookie)
  if (COOKIE_URLS.some(url => req.url.includes(url))) {
    req = req.clone({ withCredentials: true });
  }

  // Skip auth header for login/refresh/logout requests
  if (SKIP_AUTH_URLS.some(url => req.url.includes(url))) {
    return next(req);
  }

  // Attach access token from memory
  const token = authService.getAccessToken();
  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // 403 = Futmondo session expired, force re-login
      if (error.status === 403) {
        authService.logout();
        return throwError(() => error);
      }

      if (error.status === 401 && !isRefreshing) {
        isRefreshing = true;

        return from(authService.refresh()).pipe(
          switchMap((newToken) => {
            isRefreshing = false;

            if (newToken) {
              // Retry original request with new token
              const retryReq = req.clone({
                setHeaders: { Authorization: `Bearer ${newToken}` }
              });
              return next(retryReq);
            }

            // Refresh failed — logout
            authService.logout();
            return throwError(() => error);
          }),
          catchError((refreshError) => {
            isRefreshing = false;
            authService.logout();
            return throwError(() => refreshError);
          })
        );
      }

      return throwError(() => error);
    })
  );
};
