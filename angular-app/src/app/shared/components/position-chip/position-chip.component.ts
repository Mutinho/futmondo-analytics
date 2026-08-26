import { Component, ChangeDetectionStrategy, input, computed } from '@angular/core';
import { getPositionKey, getPositionLabel } from '../../utils/player.utils';

@Component({
  selector: 'app-position-chip',
  standalone: true,
  template: `<span class="pos-chip" [class]="'pos-' + posKey()">{{ label() }}</span>`,
  styles: [`
    :host { display: inline-block; margin-right: 4px; }
    :host:last-child { margin-right: 0; }
    .pos-chip {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      white-space: nowrap;
    }
    .pos-gk { background: #fff3e0; color: #e65100; }
    .pos-def { background: #e3f2fd; color: #1565c0; }
    .pos-mid { background: #e8f5e9; color: #2e7d32; }
    .pos-fwd { background: #fce4ec; color: #c62828; }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PositionChipComponent {
  position = input.required<string>();

  posKey = computed(() => getPositionKey(this.position()));
  label = computed(() => getPositionLabel(this.position()));
}
