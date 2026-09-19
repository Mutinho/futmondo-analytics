import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';

import { AssistantService } from './assistant.service';
import { AuthService } from './auth.service';

/**
 * Seeded spec for `AssistantService` (FR10.3.2, P2).
 *
 * The HTTP CRUD surface is exercised with `HttpTestingController`. The SSE
 * streaming path (`askStream`) uses `fetch`, which we mock with a deterministic
 * ReadableStream so the P2 non-determinism (real streaming) never leaks into
 * the test. `AuthService.getAccessToken` is faked; no real secrets are used.
 */
const FAKE_TOKEN = 'fake-assistant-token';

function sseStream(lines: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(lines.join('\n') + '\n'));
      controller.close();
    },
  });
}

describe('AssistantService', () => {
  let service: AssistantService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: { getAccessToken: () => FAKE_TOKEN } },
        AssistantService,
      ],
    });
    service = TestBed.inject(AssistantService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    vi.restoreAllMocks();
  });

  it('ask envia el mensaje y el championship_id en el body', async () => {
    const promise = service.ask('hola', 'champ-1', 'conv-1');
    const req = httpMock.expectOne('/api/v1/assistant/ask');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      message: 'hola',
      championship_id: 'champ-1',
      conversation_id: 'conv-1',
      history: [],
    });
    req.flush({ response: 'ok', context_used: [], conversation_id: 'conv-1' });
    await expect(promise).resolves.toEqual({
      response: 'ok',
      context_used: [],
      conversation_id: 'conv-1',
    });
  });

  it('listConversations adjunta championship_id como param', async () => {
    const promise = service.listConversations('champ-1');
    const req = httpMock.expectOne(
      (r) =>
        r.url === '/api/v1/assistant/conversations' &&
        r.params.get('championship_id') === 'champ-1',
    );
    req.flush({ conversations: [] });
    await promise;
  });

  it('deleteConversation usa DELETE en la URL con id', async () => {
    const promise = service.deleteConversation('conv-9');
    const req = httpMock.expectOne('/api/v1/assistant/conversations/conv-9');
    expect(req.request.method).toBe('DELETE');
    req.flush(null);
    await promise;
  });

  it('askStream parsea los eventos SSE y acumula los chunks', async () => {
    const chunks: string[] = [];
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      body: sseStream([
        'data: {"type":"start","conversation_id":"conv-77"}',
        'data: {"type":"chunk","content":"Hola "}',
        'data: {"type":"chunk","content":"mundo"}',
        'data: {"type":"done","context_used":["ctx-1"]}',
      ]),
    });
    vi.stubGlobal('fetch', fetchMock);

    const result = await service.askStream(
      'pregunta',
      'champ-1',
      undefined,
      (t) => chunks.push(t),
    );

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const init = fetchMock.mock.calls[0][1];
    expect(init.headers.Authorization).toBe(`Bearer ${FAKE_TOKEN}`);
    expect(chunks.join('')).toBe('Hola mundo');
    expect(result.conversation_id).toBe('conv-77');
    expect(result.context_used).toEqual(['ctx-1']);
  });

  it('askStream lanza el error del cuerpo cuando la respuesta no es ok', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'rate limit' }),
    });
    vi.stubGlobal('fetch', fetchMock);

    await expect(
      service.askStream('x', 'champ-1', undefined, () => {}),
    ).rejects.toEqual({ error: { detail: 'rate limit' } });
  });
});
