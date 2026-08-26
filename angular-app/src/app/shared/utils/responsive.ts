import { inject } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs/operators';

/**
 * Injectable function that returns a signal<boolean> for mobile detection.
 * Must be called in an injection context (constructor, field initializer, or inject()).
 */
export function injectIsMobile() {
  const bp = inject(BreakpointObserver);
  return toSignal(
    bp.observe([Breakpoints.Handset]).pipe(map(r => r.matches)),
    { initialValue: false }
  );
}
