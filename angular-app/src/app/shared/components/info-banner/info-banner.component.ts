import { Component, ChangeDetectionStrategy, input } from '@angular/core';

export interface BannerItem {
  label: string;
  value: string;
  class?: string; // e.g. 'positive', 'negative', 'primary'
}

@Component({
  selector: 'app-info-banner',
  standalone: true,
  templateUrl: './info-banner.component.html',
  styleUrl: './info-banner.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InfoBannerComponent {
  items = input.required<BannerItem[]>();
}
