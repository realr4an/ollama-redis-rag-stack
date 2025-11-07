interface Props {
  theme: 'light' | 'dark';
  onToggle: () => void;
}

export function ThemeToggle({ theme, onToggle }: Props) {
  return (
    <button
      type="button"
      onClick={onToggle}
      style={{
        border: '1px solid var(--color-border)',
        background: 'var(--color-card)',
        borderRadius: '999px',
        padding: '0.5rem 1rem',
        color: 'var(--color-fg)'
      }}
    >
      {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
    </button>
  );
}
