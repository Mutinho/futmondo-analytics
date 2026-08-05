import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-info-card',
  standalone: true,
  template: `
    <div class="info-card">
      <ng-content />
    </div>
  `,
  styles: [`
    .info-card {
      background: #ffffff;
      border-left: 4px solid #4CAF50;
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 24px;
      font-size: 13px;
      color: #444444;
      line-height: 1.5;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
    }

    :host-context(body.dark-theme) .info-card {
      background: var(--mat-sys-surface-container);
      color: var(--mat-sys-on-surface-variant);
      border-color: #66bb6a;
    }
  `]
})
export class InfoCardComponent {}
