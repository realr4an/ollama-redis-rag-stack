import { useCallback, useEffect, useMemo, useState } from 'react';
import { sendChatRequest } from './api/client';
import { ChatComposer } from './components/ChatComposer';
import { MessageList } from './components/MessageList';
import { SourceDrawer } from './components/SourceDrawer';
import { StatusPill } from './components/StatusPill';
import { ThemeToggle } from './components/ThemeToggle';
import { ModelSelector } from './components/ModelSelector';
import type { AgentStatus, ChatMessage } from './types/chat';

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [status, setStatus] = useState<AgentStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const modelProfiles = [
    {
      value: 'mistral',
      label: 'Mistral – Balance',
      description: 'Gute Balance aus Geschwindigkeit und deutschsprachiger Antwortqualität.',
    },
    {
      value: 'phi3',
      label: 'Phi-3 – Schnell',
      description: 'Sehr kurze Antwortzeiten, ideal für schnelle Kontrollfragen auf Englisch/Deutsch.',
    },
    {
      value: 'gemma',
      label: 'Gemma – Präzise',
      description: 'Stabil für strukturierte Antworten, leicht langsamer als Phi-3.',
    },
    {
      value: 'llama3',
      label: 'Llama 3 – Höchste Qualität',
      description: 'Beste kontextuelle Qualität, dafür längere Latenz – perfekt für finale Antworten.',
    },
  ];
  const [model, setModel] = useState(modelProfiles[0].value);
  const modelOptions = modelProfiles.map(({ value, label }) => ({ value, label }));
  const activeModelProfile = useMemo(
    () => modelProfiles.find((profile) => profile.value === model) ?? modelProfiles[0],
    [model]
  );

  useEffect(() => {
    document.body.classList.toggle('light', theme === 'light');
  }, [theme]);

  const latestSources = useMemo(() => {
    const lastAssistant = [...messages].reverse().find((msg) => msg.role === 'assistant');
    return lastAssistant?.sources ?? [];
  }, [messages]);

  const sendMessage = useCallback(
    async (content: string) => {
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content
      };
      setMessages((prev) => [...prev, userMessage]);
      setStatus('retrieving');
      setError(null);

      try {
        setStatus('generating');
        const response = await sendChatRequest({ query: content, model });
        const assistantMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          meta: response.stats
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setStatus('idle');
      } catch (err) {
        console.error(err);
        setStatus('error');
        setError('Anfrage fehlgeschlagen. Bitte erneut versuchen.');
      }
    },
    []
  );

  return (
    <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ margin: 0 }}>Warehouse Knowledge Assistant</h1>
          <p style={{ marginTop: '0.2rem', opacity: 0.7 }}>
            Produktionsnahes RAG-System für Logistik- &amp; WMS-Teams
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.8rem', alignItems: 'center' }}>
          <StatusPill status={status} />
          <ModelSelector value={model} options={modelOptions} onChange={setModel} />
          <ThemeToggle theme={theme} onToggle={() => setTheme((prev) => (prev === 'light' ? 'dark' : 'light'))} />
        </div>
      </header>

      <main style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        <section
          style={{
            border: '1px solid var(--color-border)',
            borderRadius: '1rem',
            padding: '1.5rem',
            background: 'var(--color-card)',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem'
          }}
        >
          <div style={{ flex: 1, minHeight: '320px', overflowY: 'auto' }}>
            {messages.length === 0 ? (
              <p style={{ opacity: 0.6 }}>Noch keine Interaktion. Starte mit einer Frage zur Lagerlogistik.</p>
            ) : (
              <MessageList messages={messages} />
            )}
          </div>
          {error && <div style={{ color: '#ef4444' }}>{error}</div>}
          <ChatComposer onSend={sendMessage} disabled={status === 'retrieving' || status === 'generating'} />
        </section>
        <aside style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <SourceDrawer sources={latestSources} />
          <div
            style={{
              border: '1px solid var(--color-border)',
              borderRadius: '0.8rem',
              padding: '1rem',
              background: 'var(--color-card)'
            }}
          >
            <h3 style={{ marginTop: 0 }}>Modell-Guide</h3>
            <strong>{activeModelProfile.label}</strong>
            <p style={{ margin: '0.2rem 0 0.6rem', fontSize: '0.85rem', opacity: 0.9 }}>
              {activeModelProfile.description}
            </p>
            <details style={{ fontSize: '0.8rem' }}>
              <summary style={{ cursor: 'pointer' }}>Alle Modelle</summary>
              <ul>
                {modelProfiles.map((profile) => (
                  <li key={profile.value}>
                    <strong>{profile.label}:</strong> {profile.description}
                  </li>
                ))}
              </ul>
            </details>
          </div>
          <div
            style={{
              border: '1px dashed var(--color-border)',
              borderRadius: '0.8rem',
              padding: '1rem'
            }}
          >
            <h3 style={{ marginTop: 0 }}>Agent Runbook</h3>
            <ul>
              <li>1. Retrieval</li>
              <li>2. Guard &amp; PII Checks</li>
              <li>3. Response + Quellen</li>
            </ul>
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;
