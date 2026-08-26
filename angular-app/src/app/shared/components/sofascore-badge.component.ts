import { Component, ChangeDetectionStrategy, input } from '@angular/core';

@Component({
  selector: 'app-sofascore-badge',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (rating() != null) {
      <span class="sofascore-badge" [class]="getClass()">{{ rating()!.toFixed(1) }}</span>
    } @else {
      <span class="sofascore-na">-</span>
    }
  `,
  styles: [`
    .sofascore-badge { display: inline-block; padding: 4px 2px; border-radius: 6px; font-size: 0.85em; font-weight: 700; color: #fff; min-width: 28px; text-align: center; cursor: pointer; }
    .s-90 { background: #374DF5; }
    .s-80 { background: #00ADC4; }
    .s-70 { background: #00C424; }
    .s-65 { background: #D9AF00; }
    .s-60 { background: #ED7E07; }
    .sofascore-na { color: var(--mat-sys-on-surface-variant); }
  `]
})
export class SofascoreBadgeComponent {
  rating = input<number | null>(null);

  getClass(): string {
    const r = this.rating();
    if (r == null) return '';
    if (r >= 9) return 's-90';
    if (r >= 8) return 's-80';
    if (r >= 7) return 's-70';
    if (r >= 6.5) return 's-65';
    return 's-60';
  }
}
