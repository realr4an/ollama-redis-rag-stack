import type { ChatMessage } from '../types/chat';

interface Props {
  messages: ChatMessage[];
}

export function MessageList({ messages }: Props) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {messages.map((message) => (
        <div
          key={message.id}
          style={{
            alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
            background: 'var(--color-card)',
            border: '1px solid var(--color-border)',
            padding: '0.9rem 1.1rem',
            borderRadius: '0.8rem',
            maxWidth: '75%'
          }}
        >
          <div style={{ fontSize: '0.8rem', opacity: 0.7, marginBottom: '0.3rem' }}>
            {message.role.toUpperCase()}
          </div>
          <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
          {message.meta && message.meta.model && (
            <div style={{ marginTop: '0.4rem', fontSize: '0.75rem', opacity: 0.7 }}>
              Modell: {String(message.meta.model)}
            </div>
          )}
          {message.sources && message.sources.length > 0 && (
            <div style={{ marginTop: '0.6rem', fontSize: '0.8rem' }}>
              Sources: {message.sources.map((src) => src.document_id).join(', ')}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
