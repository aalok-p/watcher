import { Gauge, Bar } from './gauge'

const COLOR_MAP = {
  vram: '#7c3aed',
  temp: '#f59e0b',
  power:'#f97316',
  util: '#00d4ff',
}

function tempColor(t) {
  if (t > 83) return '#ef4444'
  if (t > 70) return '#f59e0b'
  return '#22c55e'
}

export function GpuStatusCards({ metrics }) {
  if (!metrics) return (
    <div style={styles.grid}>
      {[...Array(4)].map((_, i) => (
        <div key={i} style={{ ...styles.card, opacity: 0.3 }}>
          <div style={styles.skeleton} />
        </div>
      ))}
    </div>
  )

  const tc = tempColor(metrics.temperature)

  const cards=[
    {
      label:'GPU Util',
      value: metrics.gpu_util,
      max: 100,
      color: COLOR_MAP.util,
      detail: `${metrics.gpu_util}%`,
    },
    {
      label: 'VRAM',
      value: metrics.mem_pct,
      max: 100,
      color: COLOR_MAP.vram,
      detail: `${metrics.mem_used_mb} / ${metrics.mem_total_mb} MB`,
    },
    {
      label: 'Temp',
      value: metrics.temperature,
      max: 100,
      color: tc,
      detail: `${metrics.temperature}°C`,
      noGaugePct: true,
    },
    {
      label: 'Power',
      value: metrics.power_pct,
      max: 100,
      color: COLOR_MAP.power,
      detail: `${metrics.power_draw}W / ${metrics.power_limit > 0 ? metrics.power_limit + 'W' : 'N/A'}`,
    },
  ]

  return (
    <div style={styles.grid}>
      {cards.map((c) => (
        <div key={c.label} style={styles.card}>
          <Gauge
            value={c.noGaugePct ? (metrics.temperature / 100) * 100 : c.value}
            max={100}
            label={c.label}
            color={c.color}
          />
          <Bar value={c.value} max={100} color={c.color} />
          <span style={styles.detail}>{c.detail}</span>
        </div>
      ))}
    </div>
  )
}

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: 12,
  },
  card: {
    background: '#111318',
    border: '1px solid #1e2330',
    borderRadius: 12,
    padding: '16px 12px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 10,
  },
  detail: {
    fontSize: 12,
    color: '#94a3b8',
    fontVariantNumeric: 'tabular-nums',
  },
  skeleton: {
    width: 96,
    height: 96,
    background: '#1e2330',
    borderRadius: '50%',
    animation:'pulse 1.5s infinite',
  },
}
// most of the ui components are written by ai, so please change if you want