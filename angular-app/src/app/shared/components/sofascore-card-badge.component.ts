import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-sofascore-card-badge',
  standalone: true,
  template: `
    @if (rating != null) {
      <span class="card-badge" [class]="getClass()">
        <span class="card-badge-label">Sofa</span>
        <span class="card-badge-value">{{ rating.toFixed(1) }}</span>
      </span>
    }
  `,
  styles: [`
    .card-badge { display: inline-flex; align-items: center; gap: 5px; padding: 5px 10px; border-radius: 8px; font-size: 0.85em; font-weight: 700; border: 1px solid; cursor: pointer; }
    .card-badge-label { font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.03em; opacity: 0.8; }
    .card-badge-value { font-weight: 800; font-size: 1.1em; }
    .s-90 { background: rgba(55, 77, 245, 0.1); color: #374DF5; border-color: rgba(55, 77, 245, 0.25); }
    .s-80 { background: rgba(0, 173, 196, 0.1); color: #00ADC4; border-color: rgba(0, 173, 196, 0.25); }
    .s-70 { background: rgba(0, 196, 36, 0.1); color: #00C424; border-color: rgba(0, 196, 36, 0.25); }
    .s-65 { background: rgba(217, 175, 0, 0.1); color: #D9AF00; border-color: rgba(217, 175, 0, 0.25); }
    .s-60 { background: rgba(237, 126, 7, 0.1); color: #ED7E07; border-color: rgba(237, 126, 7, 0.25); }
  `]
})
export class SofascoreCardBadgeComponent {
  @Input() rating: number | null = null;

  getClass(): string {
    if (this.rating == null) return '';
    if (this.rating >= 9) return 's-90';
    if (this.rating >= 8) return 's-80';
    if (this.rating >= 7) return 's-70';
    if (this.rating >= 6.5) return 's-65';
    return 's-60';
  }
}
