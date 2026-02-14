import { useCallback, useEffect, useRef, useState } from 'react'
import type { WSEvent } from '../api/types'

interface UseWebSocketOptions {
  onEvent?: (event: WSEvent) => void
  reconnect?: boolean
}

export function useWebSocket(url: string | null, options?: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [lastEvent, setLastEvent] = useState<WSEvent | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const reconnectAttemptRef = useRef(0)
  const shouldReconnectRef = useRef(true)
  const connectRef = useRef<(() => void) | null>(null)

  const connect = useCallback(() => {
    if (!url) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}${url}`

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        setConnectionError(null)
        reconnectAttemptRef.current = 0
      }

      ws.onclose = () => {
        setIsConnected(false)

        // Attempt reconnection with exponential backoff
        if (shouldReconnectRef.current && options?.reconnect !== false) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptRef.current), 30000)
          reconnectAttemptRef.current += 1

          reconnectTimeoutRef.current = window.setTimeout(() => {
            connectRef.current?.()
          }, delay)
        }
      }

      ws.onerror = () => {
        setConnectionError('Unable to connect. Check that the backend is running.')
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data) as WSEvent
        setLastEvent(data)
        options?.onEvent?.(data)
      }
    } catch {
      setConnectionError('Failed to establish WebSocket connection.')
    }
  }, [url, options])

  useEffect(() => {
    connectRef.current = connect
  }, [connect])

  useEffect(() => {
    shouldReconnectRef.current = true
    // eslint-disable-next-line react-hooks/set-state-in-effect
    connect()

    return () => {
      shouldReconnectRef.current = false
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      wsRef.current?.close()
    }
  }, [connect])

  const send = useCallback((data: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  const retry = useCallback(() => {
    reconnectAttemptRef.current = 0
    connect()
  }, [connect])

  return { isConnected, connectionError, lastEvent, send, retry }
}
