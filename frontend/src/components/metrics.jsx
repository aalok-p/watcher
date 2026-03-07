import { useState, useEffect, useRef } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'

const LINES = [
  { key: 'gpu_util', label: 'GPU Util %', color: '#00d4ff' },
  { key: 'mem_pct', label: 'VRAM %', color: '#7c3aed' },
  { key: 'temperature', label: 'Temp °C', color: '#f59e0b' },
]

export function MetricsChart({ metrics }) {
  const [history, setHistory] = useState([])
  const [active, setActive] = useState('gpu_util')

  useEffect(() => {
    if (!metrics) return
    const point = {
      t: new Date(metrics.timestamp * 1000).toLocaleTimeString('en', { hour12: false }),
      gpu_util: metrics.gpu_util,
      mem_pct: metrics.mem_pct,
      temperature: metrics.temperature,
    }
    setHistory(prev => {
      const next = [...prev, point]
      return next.length > 60 ? next.slice(-60) : next
    })
  }, [metrics])

  const line = LINES.find(l => l.key === active)

  return (
    <div style={styles.wrap}>
      {/* Tab bar */}
      <div style={styles.tabs}>
        {LINES.map(l => (
          <button
            key={l.key}
            onClick={() => setActive(l.key)}
            style={{
              ...styles.tab,
              color: active === l.key ? l.color : '#94a3b8',
              borderBottom: active === l.key ? `2px solid ${l.color}` : '2px solid transparent',
            }}
          >
            {l.label}
          </button>
        ))}
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={140}>
        <AreaChart data={history} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id={`grad-${active}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={line.color} stopOpacity={0.25} />
              <stop offset="95%" stopColor={line.color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" vertical={false} />
          <XAxis
            dataKey="t"
            tick={{ fontSize: 10, fill: '#94a3b8' }}
            interval="preserveStartEnd"
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            domain={[0, active === 'temperature' ? 100 : 100]}
            tick={{ fontSize: 10, fill: '#94a3b8' }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{ background: '#111318', border: '1px solid #1e2330', borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: '#94a3b8' }}
            itemStyle={{ color: line.color }}
          />
          <Area
            type="monotone"
            dataKey={active}
            stroke={line.color}
            strokeWidth={2}
            fill={`url(#grad-${active})`}
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

const styles = {
  wrap: {
    background: '#111318',
    border: '1px solid #1e2330',
    borderRadius: 12,
    padding: '12px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
  },
  tabs: {
    display: 'flex',
    gap: 4,
  },
  tab: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: 12,
    fontWeight: 600,
    padding: '4px 10px 6px',
    borderRadius: '4px 4px 0 0',
    transition: 'color 0.2s',
  },
}
