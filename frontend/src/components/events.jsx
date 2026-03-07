const STATUS_COLORS = {
  healthy: '#22c55e',
  warning: '#f59e0b',
  critical: '#ef4444',
}

export function EventTimeline({ events }) {
  if (!events || events.length === 0) {
    return (
      <div style={styles.empty}>
        No events yet -all clear 🟢
      </div>
    )
  }

  return (
    <div style={styles.list}>
      {events.map((evt) => {
        const color = STATUS_COLORS[evt.status] ?? '#94a3b8'
        return (
          <div key={evt.id} style={styles.item}>
            <span style={{ ...styles.dot, background: color, boxShadow: `0 0 6px ${color}` }} />
            <div style={styles.content}>
              <span style={styles.time}>{evt.time}</span>
              <span style={styles.headline}>{evt.headline}</span>
            </div>
            <span style={{ ...styles.badge, color, background: color + '18' }}>{evt.status}</span>
          </div>
        )
      })}
    </div>
  )
}

const styles = {
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
    maxHeight: 240,
    overflowY: 'auto',
  },
  item: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '8px 12px',
    background: '#111318',
    border: '1px solid #1e2330',
    borderRadius: 8,
    fontSize: 13,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    flexShrink: 0,
  },
  content: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
  },
  time: {
    fontSize: 11,
    color: '#94a3b8',
    fontVariantNumeric: 'tabular-nums',
  },
  headline: {
    color: '#e2e8f0',
  },
  badge: {
    fontSize: 11,
    fontWeight: 600,
    padding: '2px 6px',
    borderRadius: 12,
    textTransform: 'capitalize',
    flexShrink: 0,
  },
  empty: {
    textAlign: 'center',
    color: '#94a3b8',
    fontSize: 13,
    padding: '20px 0',
  },
}
