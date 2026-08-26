import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { AuthService } from './auth.service';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AskResponse {
  response: string;
  context_used: string[];
  conversation_id: string;
}

export interface ConversationSummary {
  id: string;
  title: string;
  championship_id: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail {
  id: string;
  title: string;
  championship_id: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface UsageResponse {
  tokens_used: number;
  tokens_limit: number;
  pct_used: number;
  requests_today: number;
  requests_daily_limit: number;
  monthly_requests: number;
}

@Injectable({ providedIn: 'root' })
export class AssistantService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private baseUrl = '/api/v1/assistant';

  ask(message: string, championshipId: string, conversationId?: string): Promise<AskResponse> {
    return firstValueFrom(
      this.http.post<AskResponse>(`${this.baseUrl}/ask`, {
        message,
        championship_id: championshipId,
        conversation_id: conversationId || null,
        history: [],
      })
    );
  }

  /**
   * Stream a response from the assistant via SSE.
   * Calls the callback with each text chunk as it arrives.
   * Returns the conversation_id and context_used when done.
   */
  async askStream(
    message: string,
    championshipId: string,
    conversationId: string | undefined,
    onChunk: (text: string) => void,
    abortSignal?: AbortSignal
  ): Promise<{ conversation_id: string; context_used: string[] }> {
    const token = this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/ask/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        message,
        championship_id: championshipId,
        conversation_id: conversationId || null,
        history: [],
      }),
      signal: abortSignal,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Error de conexión' }));
      throw { error: err };
    }

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let conversationIdResult = conversationId || '';
    let contextUsed: string[] = [];
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'start') {
              conversationIdResult = data.conversation_id;
            } else if (data.type === 'chunk') {
              onChunk(data.content);
            } else if (data.type === 'done') {
              contextUsed = data.context_used || [];
            }
          }
        }
      }
    } catch (err: any) {
      if (err?.name === 'AbortError') {
        return { conversation_id: conversationIdResult, context_used: [] };
      }
      throw err;
    }

    return { conversation_id: conversationIdResult, context_used: contextUsed };
  }

  private getAuthToken(): string | null {
    return this.authService.getAccessToken();
  }

  listConversations(championshipId?: string): Promise<{ conversations: ConversationSummary[] }> {
    let params = new HttpParams();
    if (championshipId) params = params.set('championship_id', championshipId);
    return firstValueFrom(
      this.http.get<{ conversations: ConversationSummary[] }>(`${this.baseUrl}/conversations`, { params })
    );
  }

  getConversation(id: string): Promise<ConversationDetail> {
    return firstValueFrom(
      this.http.get<ConversationDetail>(`${this.baseUrl}/conversations/${id}`)
    );
  }

  deleteConversation(id: string): Promise<void> {
    return firstValueFrom(
      this.http.delete<void>(`${this.baseUrl}/conversations/${id}`)
    );
  }

  updateTitle(id: string, title: string): Promise<void> {
    return firstValueFrom(
      this.http.put<void>(`${this.baseUrl}/conversations/${id}/title`, { title })
    );
  }

  getUsage(): Promise<UsageResponse> {
    return firstValueFrom(this.http.get<UsageResponse>(`${this.baseUrl}/usage`));
  }
}
