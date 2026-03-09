// all live data
import { useState, useEffect, useRef, useCallback } from "react"
const ws_url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export function useWatcher() {
  const [metrics, setMetrics] =useState(null)
  const [diagnosis, setDiagnosis] =useState(null)
  const [events, setEvents] = useState([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const retryRef = useRef(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return
    const ws = new WebSocket(ws_url)
    wsRef.current = ws

    ws.onopen = ()=>{ setConnected(true); clearTimeout(retryRef.current) }
    ws.onclose = () => {
      setConnected(false)
      retryRef.current = setTimeout(connect, 3000)
    }
    ws.onerror =()=>ws.close()
    ws.onmessage=(e)=>{
      try {
        const data = JSON.parse(e.data)
        if (data.metrics) setMetrics(data.metrics)
        if (data.diagnosis && Object.keys(data.diagnosis).length > 0)
          setDiagnosis(data.diagnosis)
        if (data.events) setEvents(data.events)
      } catch {}
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(retryRef.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { metrics, diagnosis, events, connected }
}
