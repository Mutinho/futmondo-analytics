import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError, filter, take } from 'rxjs';
import { from, BehaviorSubject } from 'rxjs';
import { AuthService } from '../services/auth.service';

/** URLs that should NOT get the Authorization header */
const SKIP_AUTH_URLS = ['/auth/login', '/auth/refresh', '/auth/logout'];

/** URLs that need withCredentials (cookie-based auth) */
const COOKIE_URLS = ['/auth/'];

/** Flag to prevent multiple simultaneous refresh attempts */
let isRefreshing = false;

/** Subject that emits the new token once refresh completes. null = not yet ready. */
const refreshTokenSubject = new BehaviorSubject<string | null>(null);

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

      if (error.status === 401) {
        if (!isRefreshing) {
          // First 401 — start the refresh
          isRefreshing = true;
          refreshTokenSubject.next(null); // reset

          return from(authService.refresh()).pipe(
            switchMap((newToken) => {
              isRefreshing = false;

              if (newToken) {
                refreshTokenSubject.next(newToken); // notify queued requests
                // Retry original request with new token
                const retryReq = req.clone({
                  setHeaders: { Authorization: `Bearer ${newToken}` }
                });
                return next(retryReq);
              }

              // Refresh failed — logout and reject all
              refreshTokenSubject.next(''); // unblock waiting requests (they'll fail)
              authService.logout();
              return throwError(() => error);
            }),
            catchError((refreshError) => {
              isRefreshing = false;
              refreshTokenSubject.next(''); // unblock waiting requests
              authService.logout();
              return throwError(() => refreshError);
            })
          );
        } else {
          // Another request got 401 while refresh is in progress — wait for it
          return refreshTokenSubject.pipe(
            filter(token => token !== null), // wait until refresh completes
            take(1),
            switchMap((newToken) => {
              if (!newToken) {
                // Refresh failed
                return throwError(() => error);
              }
              // Retry with the new token
              const retryReq = req.clone({
                setHeaders: { Authorization: `Bearer ${newToken}` }
              });
              return next(retryReq);
            })
          );
        }
      }

      return throwError(() => error);
    })
  );
};
