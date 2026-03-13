import { useState, useRef, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function ChatPanel({ metrics }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hey! Ask me anything about your GPU -temperatures, VRAM, throttling, drivers, CUDA, overclocking, you name it. I'm strictly here for GPU talk ",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() =>{
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send() {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', text }])
    setLoading(true)

    setMessages(prev => [...prev, { role: 'assistant',text: '', streaming: true }])

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let full = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        full += chunk
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = { role: 'assistant', text: full, streaming: true }
          return updated
        })
      }

      //stremaing done mark
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', text: full }
        return updated
      })
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = {
          role: 'assistant',
          text: ` Error: ${err.message}. Check your OpenAI API key.`,
        }
        return updated
      })
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div style={s.panel}>
      <div style={s.messages}>
        {messages.map((msg, i) => (
          <div key={i} style={{ ...s.row, justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {msg.role === 'assistant' && <div style={s.avatar}>w</div>}
            <div
              style={{
                ...s.bubble,
                ...(msg.role === 'user' ? s.userBubble : s.aiBubble),
              }}
            >
              {msg.text || (msg.streaming && <BlinkCursor />)}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div style={s.inputRow}>
        <textarea
          ref={inputRef}
          style={s.textarea}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask about your GPU… (temperatures, VRAM, throttling, CUDA…)"
          rows={1}
          disabled={loading}
        />
        <button style={{ ...s.sendBtn, opacity: loading || !input.trim() ? 0.4 : 1 }} onClick={send} disabled={loading || !input.trim()}>
          {loading ? <Spinner /> : '↑'}
        </button>
      </div>

      {metrics && (
        <div style={s.contextBadge}>
          <span style={{ color: '#00d4ff' }}>⚡</span>
          <span>Live context: {metrics.gpu_name} · {metrics.gpu_util}% util · {metrics.temperature}°C · {metrics.mem_pct}% VRAM</span>
        </div>
      )}
    </div>
  )
}

function BlinkCursor() {
  return <span style={{ animation: 'blink 1s step-end infinite', borderRight: '2px solid #00d4ff' }}>&nbsp;</span>
}

function Spinner() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" style={{ animation: 'spin 1s linear infinite' }}>
      <circle cx="12" cy="12" r="10" fill="none" stroke="#1e2330" strokeWidth="3" />
      <path d="M12 2 A10 10 0 0 1 22 12" fill="none" stroke="#00d4ff" strokeWidth="3" strokeLinecap="round" />
    </svg>
  )
}

const s = {
  panel: {
    background: '#111318',
    border: '1px solid #1e2330',
    borderRadius: 12,
    display: 'flex',
    flexDirection: 'column',
    height: 420,
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px 16px 8px',
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  row: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: 8,
  },
  avatar: {
    width: 28,
    height: 28,
    borderRadius: '50%',
    background: '#00d4ff22',
    border: '1px solid #00d4ff44',
    color: '#00d4ff',
    fontSize: 10,
    fontWeight: 700,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  bubble: {
    maxWidth: '78%',
    padding: '10px 14px',
    borderRadius: 12,
    fontSize: 13,
    lineHeight: 1.6,
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  userBubble: {
    background: '#00d4ff18',
    border: '1px solid #00d4ff33',
    color: '#e2e8f0',
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    background: '#0a0c10',
    border: '1px solid #1e2330',
    color: '#94a3b8',
    borderBottomLeftRadius: 4,
  },
  inputRow: {
    display: 'flex',
    gap: 8,
    padding: '0 12px 12px',
    alignItems: 'flex-end',
  },
  textarea: {
    flex: 1,
    background: '#0a0c10',
    border: '1px solid #1e2330',
    borderRadius: 8,
    padding: '10px 12px',
    color: '#e2e8f0',
    fontSize: 13,
    resize: 'none',
    outline: 'none',
    fontFamily: 'inherit',
    lineHeight: 1.5,
  },
  sendBtn: {
    width: 38,
    height: 38,
    borderRadius: 8,
    background: '#00d4ff',
    border: 'none',
    color: '#0a0c10',
    fontSize: 18,
    fontWeight: 700,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    transition: 'opacity 0.15s',
  },
  contextBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '6px 16px 10px',
    fontSize: 11,
    color: '#475569',
    borderTop: '1px solid #1e2330',
  },
}
