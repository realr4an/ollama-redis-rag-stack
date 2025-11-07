export type AgentStatus = 'idle' | 'retrieving' | 'generating' | 'error';

export interface SourceChunk {
  document_id: string;
  score: number;
  text: string;
  metadata?: Record<string, unknown> | null;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: SourceChunk[];
}

export interface ChatRequestPayload {
  query: string;
  namespace?: string;
  top_k?: number;
  guard_level?: 'standard' | 'strict' | 'disabled';
}

export interface ChatResponsePayload {
  answer: string;
  sources: SourceChunk[];
  guard_tripped: boolean;
  stats: Record<string, unknown>;
}
