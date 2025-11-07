interface Props {
  value: string;
  options: string[];
  onChange: (value: string) => void;
}

export function ModelSelector({ value, options, onChange }: Props) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', fontSize: '0.85rem', color: 'var(--color-fg)' }}>
      <span style={{ marginBottom: '0.2rem' }}>LLM Model</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        style={{
          borderRadius: '0.6rem',
          border: '1px solid var(--color-border)',
          padding: '0.4rem 0.6rem',
          background: 'var(--color-card)',
          color: 'var(--color-fg)'
        }}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
