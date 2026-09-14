import { of, type Observable } from 'rxjs';
import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import type { Route } from '@angular/router';
import { DEFAULT_IDLE_DELAY_MS, IdlePreloadingStrategy } from './idle-preloading-strategy';

/**
 * Tests de la lógica pura de precarga. Usamos fake timers para simular el
 * retardo/inactividad sin espera real. Forzamos el fallback a `setTimeout`
 * eliminando `requestIdleCallback` del entorno, de modo que el reloj falso
 * controle el disparo de forma determinista.
 */
describe('IdlePreloadingStrategy', () => {
  let strategy: IdlePreloadingStrategy;

  beforeEach(() => {
    vi.useFakeTimers();
    // Aseguramos el camino de fallback (setTimeout) para un control determinista
    // del reloj: jsdom no trae requestIdleCallback, pero lo borramos por si acaso.
    delete (globalThis as Record<string, unknown>)['requestIdleCallback'];
    delete (globalThis as Record<string, unknown>)['cancelIdleCallback'];
    if (typeof window !== 'undefined') {
      delete (window as unknown as Record<string, unknown>)['requestIdleCallback'];
      delete (window as unknown as Record<string, unknown>)['cancelIdleCallback'];
    }
    strategy = new IdlePreloadingStrategy();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  /** Ruta lazy sintética con un `load` espiable. */
  function lazyRoute(data?: Route['data']): Route {
    return { path: 'x', loadComponent: () => Promise.resolve({}), data } as Route;
  }

  it('happy-path: precarga la ruta tras el retardo por inactividad', () => {
    const loadSpy = vi.fn(() => of('loaded') as Observable<unknown>);
    const received: unknown[] = [];

    strategy.preload(lazyRoute(), loadSpy).subscribe((v) => received.push(v));

    // timer(0) para el arranque del pipe.
    vi.advanceTimersByTime(0);
    // Antes del idleDelay no debe haberse disparado load().
    expect(loadSpy).not.toHaveBeenCalled();

    // Avanzamos hasta el retardo de inactividad.
    vi.advanceTimersByTime(DEFAULT_IDLE_DELAY_MS);

    expect(loadSpy).toHaveBeenCalledTimes(1);
    expect(received).toContain('loaded');
  });

  it('edge: NO precarga inmediatamente (antes del idle)', () => {
    const loadSpy = vi.fn(() => of('loaded') as Observable<unknown>);

    strategy.preload(lazyRoute(), loadSpy).subscribe();

    // Solo arrancamos el pipe (timer 0) y avanzamos justo por debajo del retardo.
    vi.advanceTimersByTime(0);
    vi.advanceTimersByTime(DEFAULT_IDLE_DELAY_MS - 1);

    expect(loadSpy).not.toHaveBeenCalled();
  });

  it('edge: NO precarga rutas con data.preload === false', () => {
    const loadSpy = vi.fn(() => of('loaded') as Observable<unknown>);

    strategy.preload(lazyRoute({ preload: false }), loadSpy).subscribe();

    // Aunque avancemos el reloj holgadamente, no debe cargar.
    vi.advanceTimersByTime(DEFAULT_IDLE_DELAY_MS * 2);

    expect(loadSpy).not.toHaveBeenCalled();
  });

  it('edge: NO precarga rutas sin loadChildren/loadComponent', () => {
    const loadSpy = vi.fn(() => of('loaded') as Observable<unknown>);
    const eagerRoute = { path: 'y' } as Route;

    strategy.preload(eagerRoute, loadSpy).subscribe();

    vi.advanceTimersByTime(DEFAULT_IDLE_DELAY_MS * 2);

    expect(loadSpy).not.toHaveBeenCalled();
  });

  it('edge: cancelar la suscripción antes del idle evita la precarga', () => {
    const loadSpy = vi.fn(() => of('loaded') as Observable<unknown>);

    const sub = strategy.preload(lazyRoute(), loadSpy).subscribe();
    vi.advanceTimersByTime(0);
    sub.unsubscribe();

    vi.advanceTimersByTime(DEFAULT_IDLE_DELAY_MS * 2);

    expect(loadSpy).not.toHaveBeenCalled();
  });
});
