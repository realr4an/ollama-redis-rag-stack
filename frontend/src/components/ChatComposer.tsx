import { useState } from 'react';

interface Props {
  onSend: (value: string) => Promise<void>;
  disabled?: boolean;
}

export function ChatComposer({ onSend, disabled }: Props) {
  const [value, setValue] = useState('');

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!value.trim()) return;
    await onSend(value.trim());
    setValue('');
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.8rem' }}>
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Frage zur Warehouse-Operation stellen..."
        style={{
          flex: 1,
          minHeight: '3.5rem',
          padding: '0.75rem',
          borderRadius: '0.6rem',
          border: '1px solid var(--color-border)',
          background: 'var(--color-card)',
          color: 'var(--color-fg)'
        }}
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled}
        style={{
          background: 'var(--color-accent)',
          color: '#fff',
          border: 'none',
          borderRadius: '0.6rem',
          padding: '0 1.2rem',
          fontWeight: 600
        }}
      >
        Senden
      </button>
    </form>
  );
}
