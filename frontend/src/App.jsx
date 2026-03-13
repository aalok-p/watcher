import { useWatcher } from './useWatcher'
import { GpuStatusCards } from './components/gpucard'
import { DiagnosisPanel } from './components/diagnosispanel'
import { EventTimeline } from './components/events'
import { MetricsChart } from './components/metrics'
import { ChatPanel } from './components/chatpanel'
import watcherLogo from './watcher.svg'

export default function App() {
  const { metrics, diagnosis, events, connected } = useWatcher()

  return (
    <div style={s.root}>
      <header style={s.header}>
        <div style={s.logo}>
          <img src={watcherLogo} alt="Watcher Logo" style={{ height: 32, marginRight: 12 }} />
          <span style={s.logoText}>i know what ur GPU's do</span>
        </div>
        <div style={s.connPill}>
          <span style={{
            width: 8, height: 8, borderRadius: '50%',
            background: connected ? '#22c55e' : '#ef4444',
            boxShadow: connected ? '0 0 6px #22c55e' : '0 0 6px #ef4444',
            flexShrink: 0,
          }} />
          <span style={{ fontSize: 12, color: '#94a3b8' }}>
            {connected ? 'Live' : 'Reconnecting…'}
          </span>
          {metrics && (
            <span style={s.gpuName}>{metrics.gpu_name}</span>
          )}
        </div>
      </header>

      <main style={s.main}>
        <div style={s.col}>
          <Section title="GPU Status">
            <GpuStatusCards metrics={metrics} />
          </Section>
          <Section title="Trends">
            <MetricsChart metrics={metrics} />
          </Section>
          <Section title="Event timeline">
            <EventTimeline events={events} />
          </Section>
        </div>

        <div style={s.col}>
          <Section title="Diagnosis">
            <DiagnosisPanel diagnosis={diagnosis} />
          </Section>
          <Section title="Ask Watcher" style={{ marginTop: 40 }}>
            <ChatPanel metrics={metrics} />
          </Section>
        </div>
      </main>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity:.4 } 50% { opacity:.8 } }
        @keyframes blink { 0%,100% { opacity:1 } 50% { opacity:0 } }
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
      `}</style>
    </div>
  )
}

function Section({ title, children, style }) {
  return (
    <section style={{ ...s.section, ...style }}>
      <h2 style={s.sectionTitle}>{title}</h2>
      {children}
    </section>
  )
}



const s = {
  root: {
    minHeight: '100vh',
    background: '#0a0c10',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif",
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 28px',
    borderBottom: '1px solid #1e2330',
    background: '#0d0f14',
    position: 'sticky',
    top: 0,
    zIndex: 10,
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  },
  logoText: {
    fontSize: 20,
    fontWeight: 700,
    color: '#e2e8f0',
    letterSpacing: '-0.02em',
  },
  logoSub: {
    fontSize: 12,
    color: '#94a3b8',
    marginLeft: 4,
  },
  connPill: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    background: '#111318',
    border: '1px solid #1e2330',
    borderRadius: 20,
    padding: '4px 12px',
  },
  gpuName: {
    fontSize: 11,
    color: '#00d4ff',
    marginLeft: 4,
    maxWidth: 200,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  main: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 20,
    padding: 24,
    flex: 1,
    alignItems: 'start',
  },
  col: {
    display: 'flex',
    flexDirection: 'column',
    gap: 20,
  },
  chatWrap: {
    padding: '0 24px 28px',
  },
  section: {
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
  },
}
