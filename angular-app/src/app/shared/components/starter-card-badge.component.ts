import { Component, ChangeDetectionStrategy, input } from '@angular/core';

@Component({
  selector: 'app-starter-card-badge',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (pct() != null) {
      <span class="card-badge" [class]="getClass()">
        <span class="card-badge-label">Tit</span>
        <span class="card-badge-value">{{ pct() }}%</span>
      </span>
    }
  `,
  styles: [`
    .card-badge { display: inline-flex; align-items: center; gap: 5px; padding: 5px 10px; border-radius: 8px; font-size: 0.85em; font-weight: 700; border: 1px solid; }
    .card-badge-label { font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.03em; opacity: 0.8; }
    .card-badge-value { font-weight: 800; font-size: 1.1em; }
    .s-80 { background: rgba(22, 163, 74, 0.1); color: #16a34a; border-color: rgba(22, 163, 74, 0.25); }
    .s-60 { background: rgba(101, 163, 13, 0.1); color: #65a30d; border-color: rgba(101, 163, 13, 0.25); }
    .s-40 { background: rgba(202, 138, 4, 0.1); color: #ca8a04; border-color: rgba(202, 138, 4, 0.25); }
    .s-20 { background: rgba(234, 88, 12, 0.1); color: #ea580c; border-color: rgba(234, 88, 12, 0.25); }
    .s-0 { background: rgba(220, 38, 38, 0.1); color: #dc2626; border-color: rgba(220, 38, 38, 0.25); }
  `]
})
export class StarterCardBadgeComponent {
  pct = input<number | null>(null);

  getClass(): string {
    const p = this.pct();
    if (p == null) return '';
    if (p >= 80) return 's-80';
    if (p >= 60) return 's-60';
    if (p >= 40) return 's-40';
    if (p >= 20) return 's-20';
    return 's-0';
  }
}
