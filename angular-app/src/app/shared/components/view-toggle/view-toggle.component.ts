import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-view-toggle',
  standalone: true,
  imports: [MatButtonToggleModule, MatFormFieldModule, MatSelectModule, MatIconModule],
  templateUrl: './view-toggle.component.html',
  styleUrl: './view-toggle.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ViewToggleComponent {
  viewMode = input.required<'cards' | 'table'>();
  sortOptions = input<{ value: string; label: string }[]>([]);
  sortField = input<string>('');
  showSort = input(true);

  viewModeChange = output<'cards' | 'table'>();
  sortChange = output<string>();
}
