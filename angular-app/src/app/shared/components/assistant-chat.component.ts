import { Component, signal, inject, output, ElementRef, ViewChild, AfterViewChecked, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { marked } from 'marked';
import { AssistantService, ChatMessage, ConversationSummary } from '../../core/services/assistant.service';
import { ChampionshipService } from '../../core/services/championship.service';

interface DisplayMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

@Component({
  selector: 'app-assistant-chat',
  standalone: true,
  imports: [
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatProgressBarModule,
    MatChipsModule,
    MatTooltipModule,
  ],
  templateUrl: './assistant-chat.component.html',
  styleUrl: './assistant-chat.component.scss'
})
export class AssistantChatComponent implements AfterViewChecked, OnInit {
  private assistantService = inject(AssistantService);
  private championshipService = inject(ChampionshipService);

  @ViewChild('chatBody') chatBody!: ElementRef<HTMLDivElement>;

  closed = output<void>();

  messages = signal<DisplayMessage[]>([]);
  loading = signal(false);
  expanded = signal(true);
  sidebarOpen = signal(false);
  conversations = signal<ConversationSummary[]>([]);
  activeConversationId = signal<string>('');
  inputText = '';
  private shouldScroll = false;

  ngOnInit() {
    this.loadConversations();
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  async loadConversations() {
    try {
      const championshipId = this.championshipService.activeId();
      const data = await this.assistantService.listConversations(championshipId);
      this.conversations.set(data.conversations);

      // Auto-select the most recent conversation if none is active
      if (!this.activeConversationId() && data.conversations.length > 0) {
        this.loadConversation(data.conversations[0].id);
      }
    } catch {}
  }

  async loadConversation(id: string) {
    try {
      const conv = await this.assistantService.getConversation(id);
      this.activeConversationId.set(id);
      this.messages.set(
        conv.messages.map(m => ({ role: m.role as 'user' | 'assistant', content: m.content, timestamp: new Date() }))
      );
      this.shouldScroll = true;
    } catch {}
  }

  newConversation() {
    this.activeConversationId.set('');
    this.messages.set([]);
  }

  async deleteConversation(id: string, event: Event) {
    event.stopPropagation();
    try {
      await this.assistantService.deleteConversation(id);
      this.conversations.update(list => list.filter(c => c.id !== id));
      if (this.activeConversationId() === id) {
        this.newConversation();
      }
    } catch {}
  }

  async send() {
    const text = this.inputText.trim();
    if (!text || this.loading()) return;

    this.inputText = '';
    this.messages.update(msgs => [...msgs, { role: 'user', content: text, timestamp: new Date() }]);
    this.shouldScroll = true;
    this.loading.set(true);

    try {
      const championshipId = this.championshipService.activeId();
      if (!championshipId) {
        this.messages.update(msgs => [...msgs, { role: 'assistant', content: '⚠️ No hay campeonato seleccionado.', timestamp: new Date() }]);
        this.loading.set(false);
        return;
      }

      const response = await this.assistantService.ask(text, championshipId, this.activeConversationId() || undefined);

      // Set conversation ID (new or existing)
      this.activeConversationId.set(response.conversation_id);

      this.messages.update(msgs => [...msgs, { role: 'assistant', content: response.response, timestamp: new Date() }]);

      // Refresh conversation list
      this.loadConversations();
    } catch (err: any) {
      const errorMsg = err?.error?.detail || 'Error al conectar con el asistente.';
      this.messages.update(msgs => [...msgs, { role: 'assistant', content: `❌ ${errorMsg}`, timestamp: new Date() }]);
    } finally {
      this.loading.set(false);
      this.shouldScroll = true;
    }
  }

  sendSuggestion(text: string) {
    this.inputText = text;
    this.send();
  }

  formatMarkdown(text: string): string {
    return marked.parse(text, { breaks: true, gfm: true }) as string;
  }

  private scrollToBottom() {
    if (this.chatBody) {
      const el = this.chatBody.nativeElement;
      el.scrollTop = el.scrollHeight;
    }
  }
}
