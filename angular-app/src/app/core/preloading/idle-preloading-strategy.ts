import { Injectable } from '@angular/core';
import { PreloadingStrategy, Route } from '@angular/router';
import { Observable, of, timer } from 'rxjs';
import { mergeMap } from 'rxjs/operators';

/**
 * Retardo por defecto (ms) antes de intentar precargar una ruta.
 * Valor conservador: damos margen a que el arranque y la primera navegación
 * terminen antes de consumir red/CPU en precargas de baja prioridad (NFR4).
 */
export const DEFAULT_IDLE_DELAY_MS = 2000;

/**
 * Firma mínima de `requestIdleCallback` que usamos. El navegador la expone en
 * `window`; en entornos sin soporte (tests con jsdom, navegadores antiguos)
 * caemos a `setTimeout` (ver `scheduleWhenIdle`).
 */
type IdleCallback = (deadline?: { didTimeout: boolean; timeRemaining: () => number }) => void;

/**
 * Estrategia de precarga propia que difiere el `load()` de cada ruta lazy hasta
 * que el navegador está inactivo tras el arranque, en lugar de precargarlo todo
 * inmediatamente como hace `PreloadAllModules`.
 *
 * Objetivo (FR3): mantener la precarga —para que la navegación posterior siga
 * siendo instantánea— pero moverla fuera de la ventana crítica de arranque, de
 * modo que no compita con la carga inicial y se reduzca el pico de red (NFR4).
 *
 * Reglas de negocio:
 *  - BR3.1: se precarga con retardo tras inactividad (no de forma eager).
 *  - BR3.3: si `data.preload === false`, o la ruta no es realmente lazy
 *    (sin `loadChildren`/`loadComponent`), NO se precarga.
 *  - NFR3: sin dependencias nuevas — solo APIs del navegador + RxJS ya presente.
 */
@Injectable({ providedIn: 'root' })
export class IdlePreloadingStrategy implements PreloadingStrategy {
  /** Retardo configurable; por defecto conservador. */
  idleDelay = DEFAULT_IDLE_DELAY_MS;

  preload(route: Route, load: () => Observable<unknown>): Observable<unknown> {
    // BR3.3: respetar la exclusión explícita por `data.preload === false`.
    if (route.data?.['preload'] === false) {
      return of(null);
    }

    // BR3.3: una ruta sin carga diferida no tiene nada que precargar.
    if (!route.loadChildren && !route.loadComponent) {
      return of(null);
    }

    // BR3.1 / NFR4: esperar a la inactividad antes de disparar `load()`.
    // `timer(0)` emite ya en el microtask siguiente; encadenamos la espera de
    // inactividad real dentro de `mergeMap` para poder cancelar si el observable
    // se desuscribe (p. ej. el router deja de precargar).
    return timer(0).pipe(
      mergeMap(() =>
        new Observable<unknown>((subscriber) => {
          const cancel = this.scheduleWhenIdle(() => {
            // Delegamos en el `load()` del router; propagamos su resultado/errores.
            load().subscribe({
              next: (value) => subscriber.next(value),
              error: (err) => subscriber.error(err),
              complete: () => subscriber.complete(),
            });
          });
          // Función de teardown: cancela la precarga pendiente si nadie la espera.
          return cancel;
        }),
      ),
    );
  }

  /**
   * Programa `cb` para cuando el navegador esté inactivo. Usa
   * `requestIdleCallback` con un `timeout` igual a `idleDelay` (garantiza que se
   * ejecute como muy tarde tras ese margen aunque el navegador nunca quede
   * "ocioso"). Si la API no existe (jsdom, navegadores antiguos), cae a
   * `setTimeout(idleDelay)`. Devuelve una función de cancelación.
   */
  private scheduleWhenIdle(cb: IdleCallback): () => void {
    const w = typeof window !== 'undefined' ? (window as unknown as Record<string, unknown>) : undefined;

    const ric = w?.['requestIdleCallback'] as
      | ((callback: IdleCallback, opts?: { timeout: number }) => number)
      | undefined;
    const cic = w?.['cancelIdleCallback'] as ((handle: number) => void) | undefined;

    if (typeof ric === 'function') {
      const handle = ric(cb, { timeout: this.idleDelay });
      return () => {
        if (typeof cic === 'function') cic(handle);
      };
    }

    // Fallback sin `requestIdleCallback`: temporizador simple con el retardo.
    const handle = setTimeout(() => cb(), this.idleDelay);
    return () => clearTimeout(handle);
  }
}
