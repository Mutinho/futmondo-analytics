import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-starter-badge',
  standalone: true,
  template: `
    @if (pct != null) {
      <span class="starter-badge" [class]="getClass()">{{ pct }}%</span>
    } @else {
      <span class="starter-na">-</span>
    }
  `,
  styles: [`
    .starter-badge { display: inline-block; padding: 4px 2px; border-radius: 6px; font-size: 0.85em; font-weight: 700; color: #fff; min-width: 28px; text-align: center; }
    .s-80 { background: #16a34a; }
    .s-60 { background: #65a30d; }
    .s-40 { background: #ca8a04; }
    .s-20 { background: #ea580c; }
    .s-0 { background: #dc2626; }
    .starter-na { color: var(--mat-sys-on-surface-variant); }
  `]
})
export class StarterBadgeComponent {
  @Input() pct: number | null = null;

  getClass(): string {
    if (this.pct == null) return '';
    if (this.pct >= 80) return 's-80';
    if (this.pct >= 60) return 's-60';
    if (this.pct >= 40) return 's-40';
    if (this.pct >= 20) return 's-20';
    return 's-0';
  }
}
