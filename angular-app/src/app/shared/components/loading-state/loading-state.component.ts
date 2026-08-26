import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-loading-state',
  standalone: true,
  imports: [MatProgressSpinnerModule],
  templateUrl: './loading-state.component.html',
  styleUrl: './loading-state.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoadingStateComponent {
  loading = input.required<boolean>();
  error = input<string | null>(null);
  isEmpty = input(false);
  emptyMessage = input('No hay datos disponibles.');
  emptyIcon = input('🎯');
  loadingMessage = input('Cargando...');
}
