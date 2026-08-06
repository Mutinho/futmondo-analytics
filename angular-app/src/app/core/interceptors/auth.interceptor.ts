import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { from } from 'rxjs';
import { AuthService } from '../services/auth.service';

/** URLs that should NOT get the Authorization header */
const SKIP_URLS = ['/auth/login', '/auth/refresh', '/auth/logout'];

/** Flag to prevent multiple simultaneous refresh attempts */
let isRefreshing = false;

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  // Skip auth header for login/refresh/logout requests
  if (SKIP_URLS.some(url => req.url.includes(url))) {
    return next(req);
  }

  // Attach access token
  const token = authService.getAccessToken();
  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
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
