import type { SourceChunk } from '../types/chat';

interface Props {
  sources: SourceChunk[];
}

export function SourceDrawer({ sources }: Props) {
  if (!sources.length) return null;
  return (
    <div
      style={{
        border: '1px solid var(--color-border)',
        borderRadius: '0.8rem',
        padding: '1rem',
        background: 'var(--color-card)'
      }}
    >
      <h3 style={{ marginTop: 0 }}>Cited Sources</h3>
      <div style={{ display: 'grid', gap: '0.8rem' }}>
        {sources.map((source, idx) => (
          <div key={source.document_id + idx}>
            <strong>[S{idx + 1}] {source.document_id}</strong>
            {source.score !== undefined && (
              <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', opacity: 0.7 }}>
                score: {source.score.toFixed(3)}
              </span>
            )}
            <p style={{ margin: '0.3rem 0', fontSize: '0.9rem' }}>{source.text}</p>
            {source.metadata && (
              <small style={{ opacity: 0.7 }}>meta: {JSON.stringify(source.metadata)}</small>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
