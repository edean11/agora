import { useCallback, useEffect, useRef, useState } from 'react'
import type { WSEvent } from '../api/types'

interface UseWebSocketOptions {
  onEvent?: (event: WSEvent) => void
}

export function useWebSocket(url: string | null, options?: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastEvent, setLastEvent] = useState<WSEvent | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!url) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}${url}`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => setIsConnected(true)
    ws.onclose = () => setIsConnected(false)
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data) as WSEvent
      setLastEvent(data)
      options?.onEvent?.(data)
    }

    return () => { ws.close() }
  }, [url, options])

  const send = useCallback((data: object) => {
    wsRef.current?.send(JSON.stringify(data))
  }, [])

  return { isConnected, lastEvent, send }
}
