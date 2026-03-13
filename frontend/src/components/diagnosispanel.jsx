const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const STATUS_COLORS = {
  healthy: '#22c55e',
  warning: '#f59e0b',
  critical: '#ef4444',
}

const BOTTLENECK_LABELS = {
  none: null,
  compute_bound: { label: 'Compute Bound', color: '#00d4ff' },
  vram_bound: { label: 'VRAM Bound', color: '#7c3aed' },
  thermal_throttle: { label: 'Thermal Throttle', color: '#ef4444' },
  power_throttle: { label: 'Power Throttle', color: '#f97316' },
  gpu_idle: { label: 'GPU Idle', color: '#94a3b8' },
}

export function DiagnosisPanel({ diagnosis }) {
  if (!diagnosis || !diagnosis.headline) {
    return (
      <div style={styles.panel}>
        <div style={styles.waiting}>
          <Spinner />
          <span style={{ color: '#94a3b8', fontSize: 14 }}>Analyzing GPU…</span>
        </div>
      </div>
    )
  }

  const statusColor = STATUS_COLORS[diagnosis.status] ?? '#94a3b8'
  const bnInfo = BOTTLENECK_LABELS[diagnosis.bottleneck]

  return (
    <div style={{ ...styles.panel, borderColor: statusColor + '44' }}>
      <div style={styles.header}>
        <span style={{ ...styles.statusDot, background: statusColor, boxShadow: `0 0 8px ${statusColor}` }} />
        <span style={{ ...styles.headline, color: statusColor }}>{diagnosis.headline}</span>
        {bnInfo && (
          <span style={{ ...styles.badge, background: bnInfo.color + '22', color: bnInfo.color, border: `1px solid ${bnInfo.color}44` }}>
            {bnInfo.label}
          </span>
        )}
      </div>

      <p style={styles.body}>{diagnosis.diagnosis}</p>

      <div style={styles.actionBox}>
        <span style={styles.actionLabel}>→ ACTION</span>
        <span style={styles.actionText}>{diagnosis.action}</span>
      </div>
    </div>
  )
}

function Spinner() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" style={{ animation: 'spin 1s linear infinite' }}>
      <circle cx="12" cy="12" r="10" fill="none" stroke="#1e2330" strokeWidth="3" />
      <path d="M12 2 A10 10 0 0 1 22 12" fill="none" stroke="#00d4ff" strokeWidth="3" strokeLinecap="round" />
    </svg>
  )
}

const styles = {
  panel: {
    background: '#111318',
    border: '1px solid #1e2330',
    borderRadius: 12,
    padding: 20,
    display: 'flex',
    flexDirection: 'column',
    gap: 14,
  },
  waiting: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    justifyContent: 'center',
    padding: '24px 0',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    flexWrap: 'wrap',
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: '50%',
    flexShrink: 0,
  },
  headline: {
    fontWeight: 600,
    fontSize: 16,
    flex: 1,
  },
  badge: {
    fontSize: 11,
    fontWeight: 600,
    padding: '2px 8px',
    borderRadius: 20,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  body: {
    fontSize: 14,
    color: '#94a3b8',
    lineHeight: 1.65,
  },
  actionBox: {
    background: '#0a0c10',
    border: '1px solid #1e2330',
    borderRadius: 8,
    padding: '10px 14px',
    display: 'flex',
    gap: 10,
    alignItems: 'flex-start',
  },
  actionLabel: {
    fontSize: 11,
    fontWeight: 700,
    color: '#00d4ff',
    flexShrink: 0,
    marginTop: 1,
  },
  actionText: {
    fontSize: 13,
    color: '#e2e8f0',
    lineHeight: 1.5,
  },

}
