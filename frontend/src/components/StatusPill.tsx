import type { AgentStatus } from '../types/chat';

const STATUS_COPY: Record<AgentStatus, string> = {
  idle: 'Idle',
  retrieving: 'Retrieving context',
  generating: 'LLM generating',
  error: 'Error'
};

export function StatusPill({ status }: { status: AgentStatus }) {
  return (
    <div
      style={{
        padding: '0.35rem 0.9rem',
        borderRadius: '999px',
        border: '1px solid var(--color-border)',
        background: 'var(--color-card)',
        fontSize: '0.85rem'
      }}
    >
      {STATUS_COPY[status]}
    </div>
  );
}
