import { z } from 'zod';
import type { ChatRequestPayload, ChatResponsePayload } from '../types/chat';

const chatResponseSchema = z.object({
  answer: z.string(),
  sources: z.array(
    z.object({
      document_id: z.string(),
      score: z.number().optional().default(0),
      text: z.string(),
      metadata: z.record(z.any()).nullish()
    })
  ),
  guard_tripped: z.boolean(),
  stats: z.record(z.any())
});

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api';

async function request<T>(path: string, init?: RequestInit, retries = 2): Promise<T> {
  const url = `${API_BASE}${path}`;
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
      ...init
    });
    clearTimeout(timeout);
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    if (retries <= 0) {
      throw error;
    }
    await new Promise((resolve) => setTimeout(resolve, 500 * (3 - retries)));
    return request<T>(path, init, retries - 1);
  }
}

export async function sendChatRequest(payload: ChatRequestPayload): Promise<ChatResponsePayload> {
  const data = await request<unknown>('/chat', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
  return chatResponseSchema.parse(data);
}
