import { Component, ChangeDetectionStrategy } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-scroll-top',
  standalone: true,
  imports: [MatButtonModule, MatIconModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button mat-fab class="scroll-top-btn" (click)="scrollToTop()" title="Ir arriba">
      <mat-icon>arrow_upward</mat-icon>
    </button>
  `,
  styles: [`
    .scroll-top-btn { position: fixed; bottom: 24px; right: 24px; z-index: 100; }
  `]
})
export class ScrollTopComponent {
  scrollToTop() {
    document.querySelector('mat-sidenav-content')?.scrollTo({ top: 0, behavior: 'smooth' });
    document.querySelector('.mat-sidenav-content')?.scrollTo({ top: 0, behavior: 'smooth' });
    document.querySelector('.page-content')?.scrollTo({ top: 0, behavior: 'smooth' });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}
