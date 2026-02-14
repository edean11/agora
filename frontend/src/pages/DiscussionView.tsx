import { useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchDiscussion } from '../api/discussions'
import { useWebSocket } from '../hooks/useWebSocket'
import { useHealth } from '../hooks/useHealth'
import TranscriptView from '../components/discussions/TranscriptView'
import UserInput from '../components/discussions/UserInput'
import Spinner from '../components/ui/Spinner'
import Button from '../components/ui/Button'
import type { TranscriptEntry, WSEvent } from '../api/types'

function DiscussionView() {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()

  // State
  const [messages, setMessages] = useState<TranscriptEntry[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null)
  const [isFinished, setIsFinished] = useState(false)
  const [rounds, setRounds] = useState<{ round: number; index: number }[]>([])
  const [topic, setTopic] = useState('')
  const [participants, setParticipants] = useState<string[]>([])
  const [status, setStatus] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Fetch existing discussion data
  const { data: discussion, isLoading } = useQuery({
    queryKey: ['discussion', id],
    queryFn: () => fetchDiscussion(id!),
    enabled: !!id,
  })

  // Check health for Ollama status
  const { data: health } = useHealth()

  // Update state when discussion loads (only on first load)
  useEffect(() => {
    if (discussion && messages.length === 0) {
      setMessages(discussion.transcript)
      setTopic(discussion.topic)
      setParticipants(discussion.participants)
      setStatus(discussion.status)
      setIsFinished(discussion.status.toLowerCase() === 'completed')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [discussion])

  // WebSocket event handler
  const handleWSEvent = (event: WSEvent) => {
    console.log('WS Event:', event)

    switch (event.type) {
      case 'connected':
        if (event.topic) setTopic(event.topic as string)
        if (event.participants) setParticipants(event.participants as string[])
        if (event.status) setStatus(event.status as string)
        break

      case 'round_start':
        setRounds((prev) => [
          ...prev,
          { round: event.round as number, index: messages.length },
        ])
        setIsProcessing(true)
        break

      case 'agent_thinking':
        setThinkingAgent(event.agent as string)
        break

      case 'agent_message':
        setMessages((prev) => [
          ...prev,
          {
            timestamp: event.timestamp as string,
            speaker: event.speaker as string,
            content: event.content as string,
          },
        ])
        setThinkingAgent(null)
        break

      case 'round_end':
        setIsProcessing(false)
        setThinkingAgent(null)
        break

      case 'user_prompt':
        setIsProcessing(false)
        setThinkingAgent(null)
        break

      case 'discussion_finished':
        setIsFinished(true)
        setIsProcessing(false)
        setThinkingAgent(null)
        setStatus('completed')
        break

      case 'error':
        setError(event.message as string)
        setIsProcessing(false)
        setThinkingAgent(null)
        break
    }
  }

  // WebSocket connection
  const { isConnected, connectionError, send, retry } = useWebSocket(
    id ? `/api/discussions/${id}/ws` : null,
    { onEvent: handleWSEvent, reconnect: true }
  )

  // Auto-start for new discussions
  useEffect(() => {
    if (isConnected && searchParams.has('autostart')) {
      const rounds = parseInt(searchParams.get('rounds') || '5', 10)
      send({ type: 'start', rounds })
    }
  }, [isConnected, searchParams, send])

  // Handlers
  const handleSendMessage = (content: string) => {
    send({ type: 'user_message', content })
    setIsProcessing(true)
  }

  const handleContinue = (rounds: number) => {
    send({ type: 'continue', rounds })
    setIsProcessing(true)
  }

  const handleEndDiscussion = () => {
    send({ type: 'done' })
    setIsFinished(true)
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-olive text-parchment'
      case 'completed':
        return 'bg-charcoal-light text-parchment'
      case 'pending':
        return 'bg-gold text-charcoal'
      default:
        return 'bg-marble-dark text-charcoal'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full py-20">
        <Spinner size="lg" text="Loading discussion..." />
      </div>
    )
  }

  if (!id || !discussion) {
    return (
      <div className="flex items-center justify-center h-full py-20">
        <p className="font-sans text-charcoal-light">Discussion not found</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="border-b border-marble-dark bg-parchment px-4 sm:px-6 py-3 sm:py-4">
        <div className="max-w-4xl mx-auto space-y-2">
          <div className="flex flex-col sm:flex-row items-start justify-between gap-2 sm:gap-4">
            <h1 className="font-serif text-lg sm:text-2xl text-charcoal flex-1">
              {topic}
            </h1>
            <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
              <span
                className={`px-2 sm:px-3 py-1 rounded-full text-xs font-sans uppercase tracking-wide ${getStatusColor(status)}`}
              >
                {status}
              </span>
              {!isConnected && (
                <span className="text-xs font-sans text-charcoal-light hidden sm:inline">
                  Connecting...
                </span>
              )}
            </div>
          </div>

          {/* Participants and metadata */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm text-charcoal-light font-sans">
            <span>
              {participants.length} participant
              {participants.length !== 1 ? 's' : ''}
            </span>
            <span className="opacity-50">•</span>
            <span className="text-xs opacity-75 truncate">ID: {id}</span>
          </div>

          {/* Participant names */}
          {participants.length > 0 && (
            <div className="flex flex-wrap gap-1.5 sm:gap-2">
              {participants.map((name) => (
                <span
                  key={name}
                  className="px-2 py-1 bg-marble rounded text-xs font-sans text-charcoal"
                >
                  {name}
                </span>
              ))}
            </div>
          )}

          {/* Connection error display */}
          {connectionError && (
            <div className="px-3 sm:px-4 py-2 sm:py-3 bg-terracotta bg-opacity-20 border border-terracotta rounded flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <p className="font-sans text-sm text-terracotta">{connectionError}</p>
              <Button size="sm" variant="secondary" onClick={retry} className="w-full sm:w-auto">
                Retry
              </Button>
            </div>
          )}

          {/* Ollama down warning */}
          {health && !health.ollama_available && (
            <div className="px-3 sm:px-4 py-2 sm:py-3 bg-terracotta bg-opacity-20 border border-terracotta rounded">
              <p className="font-sans text-sm text-terracotta">
                <strong>Ollama is not available.</strong> Please start Ollama to
                use discussions.
              </p>
            </div>
          )}

          {/* Error display */}
          {error && (
            <div className="px-3 sm:px-4 py-2 bg-terracotta bg-opacity-20 border border-terracotta rounded">
              <p className="font-sans text-sm text-terracotta">{error}</p>
            </div>
          )}
        </div>
      </div>

      {/* Transcript */}
      <TranscriptView
        messages={messages}
        thinkingAgent={thinkingAgent}
        rounds={rounds}
      />

      {/* User Input */}
      <UserInput
        disabled={isProcessing || !isConnected}
        isFinished={isFinished}
        onSendMessage={handleSendMessage}
        onContinue={handleContinue}
        onEndDiscussion={handleEndDiscussion}
      />
    </div>
  )
}

export default DiscussionView
