import { TestBed } from '@angular/core/testing';
import {
  HttpClient,
  provideHttpClient,
  withInterceptors,
} from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { authInterceptor } from './auth.interceptor';
import { AuthService } from '../services/auth.service';

/**
 * Spec de caracterización del `authInterceptor` (FR7.1, FR1.2).
 *
 * Congela el comportamiento ACTUAL: inyección del header Bearer, exclusión de
 * las URLs de auth, `withCredentials` para `/auth/*`, y el flujo de refresh en
 * cola ante un 401 (primer 401 dispara refresh y reintenta con el token nuevo;
 * si el refresh falla, propaga el error y hace logout). Es el primer test
 * frontend que estrena el runner; no se regeneran specs sobre lo existente.
 */
describe('authInterceptor (caracterizacion)', () => {
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let auth: jasmine.SpyObj<AuthService>;

  beforeEach(() => {
    auth = jasmine.createSpyObj<AuthService>('AuthService', [
      'getAccessToken',
      'refresh',
      'logout',
    ]);

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: auth },
      ],
    });

    http = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('adjunta el header Authorization Bearer cuando hay access token', () => {
    auth.getAccessToken.and.returnValue('tok-123');

    http.get('/api/v1/user/me').subscribe();

    const req = httpMock.expectOne('/api/v1/user/me');
    expect(req.request.headers.get('Authorization')).toBe('Bearer tok-123');
    req.flush({});
  });

  it('no adjunta Authorization en las URLs de auth (login) y usa withCredentials', () => {
    auth.getAccessToken.and.returnValue('tok-123');

    http.post('/auth/login', {}).subscribe();

    const req = httpMock.expectOne('/auth/login');
    expect(req.request.headers.has('Authorization')).toBe(false);
    expect(req.request.withCredentials).toBe(true);
    req.flush({});
  });

  it('no adjunta Authorization cuando no hay token en memoria', () => {
    auth.getAccessToken.and.returnValue(null);

    http.get('/api/v1/market/today').subscribe();

    const req = httpMock.expectOne('/api/v1/market/today');
    expect(req.request.headers.has('Authorization')).toBe(false);
    req.flush({});
  });

  it('ante un 401 refresca y reintenta con el nuevo token', (done) => {
    auth.getAccessToken.and.returnValue('old-token');
    auth.refresh.and.returnValue(Promise.resolve('new-token'));

    http.get('/api/v1/user/me').subscribe({
      next: (body: any) => {
        expect(body.ok).toBe(true);
        expect(auth.refresh).toHaveBeenCalledTimes(1);
        done();
      },
      error: done.fail,
    });

    // Primera peticion -> 401
    httpMock
      .expectOne('/api/v1/user/me')
      .flush({ detail: 'expired' }, { status: 401, statusText: 'Unauthorized' });

    // Tras el refresh (microtask), se reintenta con el token nuevo.
    setTimeout(() => {
      const retry = httpMock.expectOne('/api/v1/user/me');
      expect(retry.request.headers.get('Authorization')).toBe('Bearer new-token');
      retry.flush({ ok: true });
    }, 0);
  });

  it('ante un 401 con refresh fallido propaga el error y hace logout', (done) => {
    auth.getAccessToken.and.returnValue('old-token');
    auth.refresh.and.returnValue(Promise.resolve(null));

    http.get('/api/v1/user/me').subscribe({
      next: () => done.fail('deberia propagar error'),
      error: (err) => {
        expect(err.status).toBe(401);
        expect(auth.logout).toHaveBeenCalled();
        done();
      },
    });

    httpMock
      .expectOne('/api/v1/user/me')
      .flush({ detail: 'expired' }, { status: 401, statusText: 'Unauthorized' });
  });

  it('ante un 403 hace logout inmediato y propaga el error', (done) => {
    auth.getAccessToken.and.returnValue('tok');

    http.get('/api/v1/user/me').subscribe({
      next: () => done.fail('deberia propagar error'),
      error: (err) => {
        expect(err.status).toBe(403);
        expect(auth.logout).toHaveBeenCalled();
        done();
      },
    });

    httpMock
      .expectOne('/api/v1/user/me')
      .flush({ detail: 'forbidden' }, { status: 403, statusText: 'Forbidden' });
  });
});
