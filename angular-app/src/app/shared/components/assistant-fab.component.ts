import { Component, ChangeDetectionStrategy, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AssistantChatComponent } from './assistant-chat.component';

@Component({
  selector: 'app-assistant-fab',
  standalone: true,
  // AssistantChatComponent se declara en `imports` para que el compilador
  // reconozca <app-assistant-chat>, pero al usarse EXCLUSIVAMENTE dentro del
  // bloque @defer, el compilador de Angular lo mueve —junto con su dependencia
  // `marked`— a un chunk diferido que se carga bajo demanda al abrir el chat.
  // Así sale del bundle initial sin romper la compilación (FR2, BR2.1, BR2.3, WF2).
  imports: [MatButtonModule, MatIconModule, AssistantChatComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @defer (when chatOpen()) {
      @if (chatOpen()) {
        <div class="chat-container">
          <app-assistant-chat (closed)="chatOpen.set(false)" />
        </div>
      }
    } @placeholder {
      <!-- Nada visible hasta que se abre el chat -->
    } @loading {
      <div class="chat-container chat-loading" data-testid="assistant-chat-loading">
        <mat-icon class="spin">smart_toy</mat-icon>
      </div>
    }

    <button
      mat-fab
      class="assistant-fab"
      data-testid="assistant-fab-toggle"
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

    .chat-loading {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 56px;
      height: 56px;
      border-radius: 12px;
      background: var(--mat-sys-surface);
      box-shadow: 0 1px 4px rgba(0,0,0,0.12);
    }

    .chat-loading .spin {
      animation: spin 1s linear infinite;
      color: var(--mat-sys-primary);
    }

    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
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
