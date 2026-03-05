// all live data
import { useState, useEffect } from "react"
const ws_url = import.meta.env.VITE_WS_URL || 'ws://loclahost:8080/s'

export function useWatcher(){
    const [metrics, setMetrics] =useState(null)
    const [diagnosis, setDiagnosis] =useState(null)
    const [events, setEvents] = useState([]);
    const [connected, setConnected] = useState(false);
}

    useEffect(()=>{
    }, []);
    return {metrics, diagnosis, events, connected};
