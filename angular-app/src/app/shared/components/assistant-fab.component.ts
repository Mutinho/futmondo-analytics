import { Component, ChangeDetectionStrategy, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AssistantChatComponent } from './assistant-chat.component';

@Component({
  selector: 'app-assistant-fab',
  standalone: true,
  imports: [MatButtonModule, MatIconModule, AssistantChatComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (chatOpen()) {
      <div class="chat-container">
        <app-assistant-chat (closed)="chatOpen.set(false)" />
      </div>
    }

    <button
      mat-fab
      class="assistant-fab"
      [class.open]="chatOpen()"
      (click)="chatOpen.update(v => !v)"
      [title]="chatOpen() ? 'Cerrar asistente' : 'Abrir asistente IA'"
    >
      <mat-icon>{{ chatOpen() ? 'close' : 'smart_toy' }}</mat-icon>
    </button>
  `,
  styles: [`
    :host {
      position: fixed;
      bottom: 24px;
      left: 274px;
      z-index: 1000;
    }

    .chat-container {
      position: absolute;
      bottom: 72px;
      left: 0;
      animation: slideUp 0.2s ease-out;
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .assistant-fab {
      background: var(--mat-sys-primary);
      color: var(--mat-sys-on-primary);
    }

    .assistant-fab.open {
      background: var(--mat-sys-error);
      color: var(--mat-sys-on-error);
    }

    @media (max-width: 600px) {
      :host {
        bottom: 16px;
        left: 16px;
      }

      .chat-container {
        bottom: 0;
        right: 0;
      }

      .assistant-fab.open {
        display: none;
      }
    }
  `]
})
export class AssistantFabComponent {
  chatOpen = signal(false);
}
