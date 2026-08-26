import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { SofascoreCardBadgeComponent } from '../sofascore-card-badge.component';
import { StarterCardBadgeComponent } from '../starter-card-badge.component';
import { PositionChipComponent } from '../position-chip/position-chip.component';
import { getPlayerPhoto, getTeamLogo, onImgError } from '../../utils/player.utils';

export interface PlayerCardStat {
  label: string;
  value: string;
  class?: string;
}

@Component({
  selector: 'app-player-card',
  standalone: true,
  imports: [SofascoreCardBadgeComponent, StarterCardBadgeComponent, PositionChipComponent],
  templateUrl: './player-card.component.html',
  styleUrl: './player-card.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlayerCardComponent {
  name = input.required<string>();
  slug = input<string>('');
  team = input<string>('');
  teamLogo = input<string>('');
  position = input<string>('');
  sofascoreRating = input<number | null>(null);
  starterPct = input<number | null>(null);
  stats = input<PlayerCardStat[]>([]);
  highlighted = input(false);
  highlightClass = input('');

  getPlayerPhoto = getPlayerPhoto;
  getTeamLogo = getTeamLogo;
  onImgError = onImgError;

  onTeamImgError(event: Event): void {
    onImgError(event);
  }
}
