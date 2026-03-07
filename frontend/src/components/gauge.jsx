export function Gauge({ value = 0, max = 100, label, color = '#00d4ff', size = 96 }) {
  const r=38
  const circ=2*Math.PI * r
  const pct=Math.min(value / max, 1)
  const dash = pct *circ
  const gap = circ - dash

  const trackColor ='#1e2330'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
      <svg width={size} height={size} viewBox="0 0 96 96">
        {/* track */}
        <circle cx="48" cy="48" r={r} fill="none" stroke={trackColor} strokeWidth="8" />
        {/* progress */}
        <circle
          cx="48" cy="48" r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${gap}`}
          strokeDashoffset={circ / 4}   /* start at top */
          style={{ transition: 'stroke-dasharray 0.6s ease', filter: `drop-shadow(0 0 4px ${color})` }}
        />
        <text x="48" y="53" textAnchor="middle" fill="#e2e8f0" fontSize="16" fontWeight="700">
          {Math.round(value)}%
        </text>
      </svg>
      <span style={{ fontSize:11, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
        {label}
      </span>
    </div>
  )
}

export function Bar({ value=0, max = 100, color = '#00d4ff' }) {
  const pct = Math.min(100,(value / max) * 100)
  return (
    <div style={{
      background: '#1e2330', borderRadius: 4, height: 6, overflow: 'hidden', width: '100%'
    }}>
      <div style={{
        width: `${pct}%`,
        height: '100%',
        background:color,
        borderRadius:4,
        transition:'width 0.5s ease',
        boxShadow:`0 0 6px ${color}`,
      }} />
    </div>
  )
}
