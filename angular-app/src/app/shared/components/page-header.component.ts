import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-page-header',
  standalone: true,
  imports: [MatIconModule],
  template: `
    <div class="page-header">
      <h1><mat-icon class="page-icon">{{ icon }}</mat-icon> {{ title }}</h1>
      @if (description) {
        <p class="description">{{ description }}</p>
      }
    </div>
  `,
  styles: [`
    .page-header { margin-bottom: 20px; }
    h1 { display: flex; align-items: center; gap: 10px; font-size: 1.5em; font-weight: 700; margin: 0 0 8px; color: var(--mat-sys-on-surface); }
    .page-icon { font-size: 28px; width: 28px; height: 28px; color: var(--mat-sys-primary); }
    .description { color: var(--mat-sys-on-surface-variant); font-size: 13px; margin: 0; }
  `]
})
export class PageHeaderComponent {
  @Input({ required: true }) title!: string;
  @Input({ required: true }) icon!: string;
  @Input() description = '';
}
